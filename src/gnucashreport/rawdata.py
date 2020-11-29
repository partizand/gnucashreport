import gettext
import locale
import os
from copy import copy
from datetime import date, datetime
from decimal import Decimal

import pandas
import numpy
from gnucashreport import utils

from gnucashreport.financial import xirr
from gnucashreport.margins import Margins
from gnucashreport.gnucashbook import GNUCashBook

import gnucashreport.cols as cols

# Признак, что счет не участвует в расчете доходности
MARKER_NO_INVEST = '%no_invest%'
# Признак, что счет участвует в расчете доходности
MARKER_INVEST = '%invest%'


class RawData:
    """
    Low level DataFrame implementation of GnuCash database tables for build reports
    function returns DataFrames with data, without totals and styling

    """

    # # GnuCash account types
    # CASH = 'CASH'
    # BANK = 'BANK'
    # ASSET = 'ASSET'
    # STOCK = 'STOCK'
    # MUTUAL = 'MUTUAL'
    # INCOME = 'INCOME'
    # EXPENSE = 'EXPENSE'
    # EQUITY = 'EQUITY'
    # LIABILITY = 'LIABILITY'
    # ROOT = 'ROOT'
    # # GNUCash all account assets types
    # ALL_ASSET_TYPES = [CASH, BANK, ASSET, STOCK, MUTUAL]
    #
    # # All account types for calc yield by xirr
    # ALL_XIRR_TYPES = [BANK, ASSET, STOCK, MUTUAL, LIABILITY]
    # ASSET_XIRR_TYPES = [BANK, ASSET, LIABILITY]
    # STOCK_XIRR_TYPES = [STOCK, MUTUAL]
    # INCEXP_XIRR_TYPES = [INCOME, EXPENSE]

    # Данные для генерации тестовых данных и тестирования
    dir_pickle = 'V:/test_data'

    pickle_prices = 'prices.pkl'
    pickle_splits = 'splits.pkl'
    pickle_accounts = 'accounts.pkl'
    pickle_tr = 'transactions.pkl'
    pickle_commodities = 'commodities.pkl'

    dir_excel = "v:/tables"

    def __init__(self, filename=None):
        self.df_accounts = pandas.DataFrame()
        self.df_transactions = pandas.DataFrame()
        self.df_commodities = pandas.DataFrame()
        self.df_splits = pandas.DataFrame()
        self.df_prices = pandas.DataFrame()

        # self.book_name = None


        # internalization
        self.set_locale()

        self.book = None
        self.root_account_guid = None

        if filename:
            self.open_book_file(filename)

        self._xirr_info_added = False


    @staticmethod
    def set_locale():
        """
        Set current os locale for gettext
        :return:
        """
        # internalization
        if os.name == 'nt':
            current_locale, encoding = locale.getdefaultlocale()
            os.environ['LANGUAGE'] = current_locale

        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        dir_locale = os.path.join(dir_path, 'locale')
        gettext.install('gnucashreport', localedir=dir_locale)

    # def open_book_file(self, filename, readonly=True, open_if_lock=False,):
    def open_book_file(self, filename):
        """
        Open GnuCash database file. Autodetect type: sqlite or xml
        :param filename:
        :param readonly: only for sqlite
        :param open_if_lock: only for sqlite
        :return:
        """

        self.book = GNUCashBook()
        self.book.open_file(filename)

        self.df_accounts = self.book.df_accounts
        self.df_commodities = self.book.df_commodities
        self.df_prices = self.book.df_prices
        self.df_transactions = self.book.df_transactions
        self.df_splits = self.book.df_splits

        self.root_account_guid = self.book.root_account_guid

        self._after_read()


    def __repr__(self):
        return 'gcreport {book}'.format(book=self.book)




    def _after_read(self):
        """
        Some manipulation with dataframes after load data
        :return:
        """

        # # Минимальная и максимальная даты в базе
        self.min_date = self.df_splits[cols.POST_DATE].min() #.date()
        self.max_date = self.df_splits[cols.POST_DATE].max() #.date()

        # Цены за каждый день по каждому инструменту
        self.df_prices_days = self._group_prices_by_period(self.min_date, self.max_date, 'D')


        # Пересчет транзакций в валюту учета
        self.df_splits = self._currency_calc(self.df_splits,
                                             col_currency_guid=cols.CURRENCY_GUID,
                                             col_rate=cols.RATE_CURRENCY
                                             )

    def _add_margins(self, dataframe, margins=None):
        """
        Add totals into DataFrame
        :param dataframe:
        :param margins:
        :return: DataFrame with totals
        """

        df = dataframe.copy()
        if margins:
            if margins.total_row:
                df = self._add_row_total(df, margins)

            if margins.total_col or margins.mean_col:
                df = self._add_col_total(df, margins)
        return df

    def _add_col_total(self, dataframe, margins):

        # Список полей для подсчета среднего
        columns = dataframe.columns.tolist()
        df_ret = dataframe.copy()
        # Добавление пустого столбца
        if margins.empty_col:
            df_ret[''] = ''
        if margins.total_col:
            df_ret[margins.total_name] = df_ret[columns].sum(axis=1)
        if margins.mean_col:
            df_ret[margins.mean_name] = df_ret[columns].mean(axis=1)

        return df_ret

    def _add_row_total(self, dataframe, margins=None):

        total_name = _('Total')
        if margins:
            total_name = margins.total_name
        if isinstance(dataframe.index, pandas.MultiIndex):

            df_ret = dataframe.copy()
            df_sum = pandas.DataFrame(data=dataframe.sum()).T
            # df_sum.reindex()
            # Строковые имена колонок индекса
            strinames = [str(name) for name in dataframe.index.names]

            first = True
            for i in strinames:
                if first:
                    df_sum[i] = total_name
                    first = False
                else:
                    df_sum[i] = ''
            df_sum.set_index(strinames, inplace=True)
            df_ret = df_ret.append(df_sum)
            return df_ret

        else:
            index = total_name
            df_ret = dataframe.copy()
            df_ret.loc[index] = dataframe.sum()
            return df_ret

    def equity_by_period(self, from_date, to_date, period='M', glevel=1, margins = None):
        """
        Получение капитала за период (активы минус пассивы)
        Возвращает DataFrame

        :param from_date: Start date
        :param to_date: Finish date
        :param period: "M" for month, "D" for day...
        :param glevel: group level
        :param margins:
        :return: pivot DataFrame
        """
        assets_and_liability = copy(GNUCashBook.ALL_ASSET_TYPES)
        assets_and_liability.append(GNUCashBook.LIABILITY)

        # Группировка по периоду
        group_acc = self._balance_group_by_period(from_date=from_date, to_date=to_date, period=period,
                                                  account_types=assets_and_liability, drop_null=False)

        # пересчет в нужную валюту
        group_acc = self._currency_calc(group_acc)

        # Суммируем
        equity_name = _('Equity')
        if margins:
            equity_name = margins.equity_name
        df = self._sum_all(group_acc, total_name=equity_name, glevel=glevel, inverse=False)

        # Добавление итогов
        df = self._add_margins(df, margins)

        return df

    def balance_on_date(self, on_date, col_value_currency=cols.VALUE_CURRENCY,
                        account_names=None, account_guids=None, start_balance=False):
        """
        Возвращает DataFrame со строками балансов выбранных счетов на конец дня заданной даты
        Если задано start_balance=True - будет значение на начало дня заданной даты
         (если баланс 0, строки не будет)
        Баланс в кол-ве бумаг - cum_sum
        Баланс в валюте учета - value_currency
        :param on_date: 
        :param account_names: 
        :param account_guids: 
        :param start_balance: False - баланс на конец дня, True - баланс на начало дня
        :return: DataFrame с балансами
        """

        # Сортировка по дате

        if start_balance:
            df = (self.df_splits[(self.df_splits[cols.POST_DATE] < on_date)]).copy()
        else:
            df = (self.df_splits[(self.df_splits[cols.POST_DATE] <= on_date)]).copy()
        # Сортировка по счетам
        if account_names:
            df = df[(df[cols.FULLNAME]).isin(account_names)]
        if account_guids:
            df = df[(df[cols.ACCOUNT_GUID]).isin(account_guids)]

        # Установка индекса по account_guid
        df['guid'] = df.index
        df.set_index(cols.ACCOUNT_GUID, inplace=True, drop=False)
        # отсечение повторов по индексу
        df = df[~df.index.duplicated(keep='last')]
        # Теперь в cum_sum - остаток по счету на дату (если он есть)
        df[cols.POST_DATE] = numpy.datetime64(on_date)
        # df.drop(cols.VALUE, axis=1, inplace=True)
        # df.rename(columns={cols.CUM_SUM: cols.VALUE}, inplace=True)
        if not df.empty:
            df = self._currency_calc(df, col_value=cols.CUM_SUM,
                                     col_value_currency=col_value_currency)
        # Убрать нулевые значения
        df = df[df[cols.VALUE_CURRENCY] != 0]
        df[cols.DESCRIPTION] = 'Balance on date'
        df.set_index('guid', inplace=True)
        return df

    def yield_calc(self, account_guid=None, account_name=None, account_types=None, from_date=None, to_date=None,
                   recurse=True, rename_col=True):
        """
        Calculate annual return for account or account and it childrens (recurse)
        
        Set account name or account guid
        if not set account_guid and account_name will use root account
        
        if not set to_date will use today date
        You may use self.max_date - to set last transaction date in gnucash base
        
        :param account_guid: 
        :param account_name: 
        :param account_types: array for filter by account types
        :param from_date: 
        :param to_date: 
        :param recurse: calculate children accounts returns too
        :return: dataframe
        """

        self._add_xirr_info()

        ar_xirr = self._xirr_child_calc_array(account_guid=account_guid, account_name=account_name,
                                              account_types=account_types,
                                              from_date=from_date, to_date=to_date,
                                              recurse=recurse
                                              )

        # Колонки в нужной последовательности
        df = pandas.DataFrame(ar_xirr, columns=[
                                                # cols.SHORTNAME,
                                                cols.FULLNAME,
                                                cols.YIELD_TOTAL,
                                                cols.YIELD_INCOME,
                                                cols.YIELD_CAPITAL,
                                                cols.YIELD_EXPENSE,
                                                cols.START_DATE,
                                                cols.END_DATE,
                                                cols.DAYS
                                                ])

        # Переименовать колонки для отображения
        if rename_col:
            df.rename({cols.YIELD_TOTAL: _('Total'),
                            cols.YIELD_INCOME: _('Cashflow'),
                            cols.YIELD_CAPITAL: _('Capital'),
                            cols.YIELD_EXPENSE: _('Expense'),
                            cols.START_DATE: _('Start date'),
                            cols.END_DATE: _('End date'),
                            cols.DAYS: _('Days')
                            }, inplace=True, axis=1 )

        if account_guid:
            account_name = self.df_accounts.loc[account_guid, cols.SHORTNAME]

        df.sort_values(cols.FULLNAME, inplace=True)
        df[cols.FULLNAME] = df[cols.FULLNAME].apply(utils.shift_account_name, args=(account_name,))
        df.set_index(cols.FULLNAME, inplace=True, drop=True)

        return df



    def _xirr_child_calc_array(self, account_guid=None, account_name=None, account_types=None,
                               from_date=None, to_date=None, df_all_xirr=None, recurse=True):
        """
        Подсчитывает доходность счета или счетов
        Возвращает массив словарей
        :param account_guid: 
        :param account_name: 
        :param account_types: 
        :param from_date: 
        :param to_date: 
        :param df_all_xirr: 
        :param recurse: 
        :return: array of dictionaries with annual return 
        """

        root_guid = account_guid

        # Получение guid счета для которого считать доходность
        if not root_guid:
            if account_name:
                root_guid = self._get_account_guid(account_name)
            else:
                root_guid = self.root_account_guid

        # Если типы счетов не заданы, все типы для xirr
        if not account_types:
            account_types = [GNUCashBook.BANK,
                             GNUCashBook.ASSET,
                             GNUCashBook.STOCK,
                             GNUCashBook.MUTUAL,
                             GNUCashBook.LIABILITY]

        # Теперь в root_guid счет с которого нужно начинать
        # Нужно посчитать его доходность и доходности его потомков

        ar_xirr = []

        # Получение списка проводок по которым считается доходность
        if df_all_xirr is None:
            child_guids = self._get_child_accounts(root_guid, account_types=account_types,
                                                   xirr_enable=True, recurse=True)
            account_guids = [root_guid] + child_guids
            df_all_xirr = self._get_all_for_xirr(account_guids=account_guids, from_date=from_date, to_date=to_date)

        # Подсчет доходности текущего счета
        if root_guid != self.root_account_guid:
            xirr_root = self._xirr_calc(account_guid=root_guid, account_types=account_types,
                                        df_all_xirr=df_all_xirr)
            if xirr_root:
                ar_xirr += [xirr_root]

        # Считаем доходность потомков, если нужно
        if recurse:

            childs = self._get_child_accounts(account_guid=root_guid, account_types=account_types,
                                              xirr_enable=True, recurse=False)

            for child in childs:

                sub_xirr = self._xirr_child_calc_array(account_guid=child, account_types=account_types,
                                                       df_all_xirr=df_all_xirr, recurse=recurse)
                if sub_xirr:
                    ar_xirr += sub_xirr

        return ar_xirr

    def _xirr_calc(self, account_guid, account_types, df_all_xirr):
        """
        Возвращает итоговую доходность по указанному счету по таблице df_all_xirr
        :param account_guid: 
        :param account_types: 
        :param df_all_xirr: table with all xirr values for calculating
        :return: dictionary with annual return
        """
        child_guids = self._get_child_accounts(account_guid, account_types=account_types,
                                               xirr_enable=True, recurse=True)
        account_guids = [account_guid] + child_guids

        df_xirr = (df_all_xirr[df_all_xirr[cols.XIRR_ACCOUNT].isin(account_guids)]).copy()
        if df_xirr.empty:
            return


        # Общая доходность
        yield_total = self._xirr_by_dataframe(df_xirr)

        # Доходность денежного потока
        if not any(df_xirr[cols.ACCOUNT_TYPE].isin([GNUCashBook.INCOME])):
            yield_income = Decimal(0)
        else:
            # Доходность без денежного потока
            df_without_income = df_xirr[df_xirr[cols.ACCOUNT_TYPE] != GNUCashBook.INCOME]
            without_income_yeld = self._xirr_by_dataframe(df_without_income)
            yield_income = yield_total - without_income_yeld

        # Стоимость расходов
        if not any(df_xirr[cols.ACCOUNT_TYPE].isin([GNUCashBook.EXPENSE])):
            yield_expense = Decimal(0)
        else:
            # Доходность без расходов
            df_without_expense = df_xirr[df_xirr[cols.ACCOUNT_TYPE] != GNUCashBook.EXPENSE]
            yield_without_expense = self._xirr_by_dataframe(df_without_expense)
            yield_expense = yield_without_expense - yield_total

        itog = {}
        round_prec = 4
        itog[cols.FULLNAME] = self.df_accounts.loc[account_guid][cols.FULLNAME]
        itog[cols.SHORTNAME] = self.df_accounts.loc[account_guid][cols.SHORTNAME]
        itog[cols.YIELD_TOTAL] = round(yield_total, round_prec)
        itog[cols.YIELD_INCOME] = round(yield_income, round_prec)
        itog[cols.YIELD_EXPENSE] = round(yield_expense, round_prec)
        itog[cols.YIELD_CAPITAL] = itog[cols.YIELD_TOTAL] - itog[cols.YIELD_INCOME]
        itog[cols.START_DATE] = df_xirr[cols.POST_DATE].min().date()
        itog[cols.END_DATE] = df_xirr[cols.POST_DATE].max().date()
        itog[cols.DAYS] = (itog[cols.END_DATE] - itog[cols.START_DATE]).days
        # itog[cols.XIRR_DAYS] = days

        return itog

    def _xirr_by_dataframe(self, obj, date_field=cols.POST_DATE, value_field=cols.XIRR_VALUE):
        """
        Считает функцию xirr по значениям dataframe. obj может быть dataframe или массивом словарей
        :param obj: DataFrame 
        :param date_field: Name of date column
        :param value_field: Name of value column
        :return: annual yield
        """
        df = pandas.DataFrame(obj, columns=[date_field, value_field])
        df[date_field] = pandas.to_datetime(df[date_field]).dt.date
        tuples = [tuple(x) for x in df.to_records(index=False)]
        a_yield = xirr(tuples)
        return a_yield


    def _get_child_accounts(self, account_guid, account_types=None, xirr_enable=None, recurse=True):
        """
        Возвращает список счетов потомков
        recurse=True - Список всех потомков
        recurse=False - Только потомки первого уровня
        :param account_guid:
        :return:
        """
        # speed optimization
        df = self.df_accounts
        # Фильтрация по типам счетов
        if account_types:
            df = df[(df[cols.ACCOUNT_TYPE]).isin(account_types)]
        # Фильтрация по xirr_enable
        if xirr_enable:
            df = df[df[cols.XIRR_ENABLE] == xirr_enable]

        df = df[df[cols.PARENT_GUID] == account_guid]
        childs = df.index.tolist()

        if recurse:
            sub_childs = []
            for child_account in childs:
                sub_childs += self._get_child_accounts(child_account)
            childs += sub_childs

        return childs

    def _get_account_guid(self, fullname):
        """
        Возвращает guid счета по полному имени или none если имя не найдено
        :param fullname: 
        :return: account guid
        """
        idx = self.df_accounts[self.df_accounts[cols.FULLNAME] == fullname].index.tolist()
        if idx:
            return idx[0]
        else:
            return None

    def _add_xirr_info(self):

        if self._xirr_info_added:
            return

        # Добавление столбцов для xirr в df_splits
        self.df_splits[cols.XIRR_ACCOUNT] = ''
        self.df_splits[cols.XIRR_VALUE] = ''

        # Получить список tr_guid
        tr_guids = self.df_splits[cols.TRANSACTION_GUID].drop_duplicates().tolist()

        # Установить индекс по tr_guid
        self.df_splits.set_index(cols.TRANSACTION_GUID, inplace=True, append=True, drop=True)
        self.df_splits = self.df_splits.swaplevel()
        # dataframe_to_excel(self.df_splits, 'splits-after-index')


        # Перебираем все транзакции
        for tr_guid in tr_guids:
            df_tr_splits = self.df_splits.loc[tr_guid]
            self._add_xirr_by_transaction(df_tr_splits, tr_guid)

        # Вернуть индекс на место
        self.df_splits = self.df_splits.swaplevel()
        # dataframe_to_excel(self.df_splits, 'splits-swap')
        self.df_splits.reset_index(level=1, drop=False, inplace=True)

        self._xirr_info_added = True

    def _add_xirr_by_transaction(self, df_tr_splits: pandas.DataFrame, tr_guid: str):
        """
        Добавляет значения в поля xirr_account и xirr_value в df_splits
        Согласно правил, описанных в excel нике
        Возможно можно оптимизировать быстродействие
        :param df_tr_splits: pandas.DataFrame
                            Все сплиты транзакции
        :param tr_guid: transaction guid
        :return: 
        """

        # income and expense types
        incexp_types = [GNUCashBook.INCOME, GNUCashBook.EXPENSE]
        # income splits
        df_incexps = df_tr_splits[df_tr_splits[cols.ACCOUNT_TYPE].isin(incexp_types)]
        # все оставшиеся splits
        df_assets = df_tr_splits[~df_tr_splits[cols.ACCOUNT_TYPE].isin(incexp_types)]

        # есть ли счета для xirr
        if not any(df_assets[cols.XIRR_ENABLE]):
            return

        # Простая 2-х проводочная транзакция
        if len(df_tr_splits) == 2:

            if (len(df_incexps) == 1) and (len(df_assets) == 1):
                # у asset уже стоит xirr_enable
                # Нужно добавить df_asset, если xirr_enabe у incexp = False
                ie_xirr_enable = df_incexps.iloc[0][cols.XIRR_ENABLE]
                if not ie_xirr_enable:
                    self._set_xirr_to_splits(tr_guid=tr_guid, df=df_assets)
                return
            elif len(df_assets) == 2:
                # добавить все строки с xirr_enable
                self._set_xirr_to_splits(tr_guid=tr_guid, df=df_assets)
                return
            else:
                # Неясность
                print("Unknown transaction type for xirr.")
                self._print_transaction_info(df_tr_splits, tr_guid)
                return

        # Multi transaction
        # has one stock
        df_stocks = df_tr_splits[df_tr_splits[cols.ACCOUNT_TYPE].isin(GNUCashBook.STOCK_XIRR_TYPES)]
        len_stocks = len(df_stocks) # number of stock account in transaction
        if len_stocks > 0:  # transaction has stock accounts
            asset_guid = df_stocks.iloc[0][cols.ACCOUNT_GUID]  # first stock account
            if len_stocks == 2:
                asset_guid2 = df_stocks.iloc[1][cols.ACCOUNT_GUID]  # second stock account
                if asset_guid != asset_guid2:
                    # unknown transaction
                    print("Unknown stock transaction with two different stock")
                    self._print_transaction_info(df_tr_splits, tr_guid)
                    return
                else:
                    print("Warning! two equal stocks in one transaction. I am calculate xirr, but it is wrong")
                    self._print_transaction_info(df_tr_splits, tr_guid)
            if len_stocks > 2:
                # unknown transaction
                print("Unknown transaction with more than two stocks")
                self._print_transaction_info(df_tr_splits, tr_guid)
                return
            # Тут нужно добавить все asset у которых xirr_enable = True
            self._set_xirr_to_splits(tr_guid=tr_guid, df=df_assets)
            # Тут нужно определить счет на который пойдут прибыли или убытки
            # И добавить все расходы/доходы у которых xirr_enable=true
            self._set_xirr_to_splits(tr_guid=tr_guid, df=df_incexps, xirr_account=asset_guid)
            return
        elif (len(df_assets) == 2) and (len(df_incexps) == 1):
            # Тест. Добавление признака такой транзакции
            # self.df_splits.loc[tr_guid, 'tr_type'] = 'asset-asset-incexp'

            # Нужно добавить все строки asset с xirr_enable = True
            self._set_xirr_to_splits(tr_guid=tr_guid, df=df_assets)
            # И добавить все расходы/доходы у которых xirr_enable=true
            master_guid = self._get_master_asset_guid(df_assets)
            self._set_xirr_to_splits(tr_guid=tr_guid, df=df_incexps, xirr_account=master_guid)
            return
        elif (len(df_assets) == 1) and (len(df_incexps) == 2):
            # Нужно добавить все строки asset с xirr_enable = True
            self._set_xirr_to_splits(tr_guid=tr_guid, df=df_assets)
            # И добавить все расходы/доходы у которых xirr_enable=true
            master_guid = df_assets.iloc[0][cols.ACCOUNT_GUID]
            self._set_xirr_to_splits(tr_guid=tr_guid, df=df_incexps, xirr_account=master_guid)
            return
        else:
            # Error, unknown stock transaction for xirr
            print('Unknown multi transaction for xirr calculate.')
            self._print_transaction_info(df_tr_splits, tr_guid)
            return

    def _print_transaction_info(self, df_tr_splits, tr_guid):
        """
        Print transaction info
        :param df_tr_splits: pandas.DataFrame
                            Все сплиты транзакции
        :param tr_guid: transaction guid
        :return:
        """
        tr_date = df_tr_splits.iloc[0][cols.POST_DATE]
        tr_descr = df_tr_splits.iloc[0][cols.DESCRIPTION]
        print('Transaction info: '
              'guid={tr_guid}. Date={tr_date}.\n Description={tr_descr}'.format(tr_guid=tr_guid, tr_date=tr_date,
                                                                        tr_descr=tr_descr))

    def _set_xirr_to_splits(self, tr_guid: str, df: pandas.DataFrame, xirr_account: str = None):
        """
        Задает значения колонок xirr_value (сумма с обратным знаком) и xirr_account (guid счета по которому идет этот оборот в xirr)
        в таблице df_splits
        Из строк таблицы df, у которых xirr_enable = True
        Если xirr_account заполнен, то берется он, иначе берется счет из строки df
        :param tr_guid: 
        :param df: 
        :param xirr_account: 
        :return: 
        """
        for index, row in df.iterrows():
            if row[cols.XIRR_ENABLE]:
                value_currency = row[cols.VALUE_CURRENCY]
                if value_currency != 0:
                    self.df_splits.loc[(tr_guid, index), cols.XIRR_VALUE] = value_currency * -1
                    if xirr_account:
                        self.df_splits.loc[(tr_guid, index), cols.XIRR_ACCOUNT] = xirr_account
                    else:
                        self.df_splits.loc[(tr_guid, index), cols.XIRR_ACCOUNT] = row[cols.ACCOUNT_GUID]

    def _get_master_asset_guid(self, df_assets: pandas.DataFrame):
        """
        Находит account_guid из df_assets на который писать доход/убыток транзакции
        Возвращает account_guid для отобранного счета
        :param df_assets: проводки транзакции с типом asset
        :param df_incexp: проводки транзакции с типом incexp
        :return: account_guid
        """

        df_asset = df_assets[df_assets[cols.XIRR_ENABLE]]
        # Нет счетов вообще
        if df_asset.empty:
            return None
        # Если счет один, то он и главный
        if len(df_asset) == 1:
            return df_asset.iloc[0][cols.ACCOUNT_GUID]

        # если есть тип stock, то он главный
        if any(df_asset[cols.ACCOUNT_TYPE].isin(GNUCashBook.STOCK_XIRR_TYPES)):
            df = df_asset[df_asset[cols.ACCOUNT_TYPE].isin(GNUCashBook.STOCK_XIRR_TYPES)]
            return df.iloc[0][cols.ACCOUNT_GUID]

        # Если есть счет с 0, то главный он
        df_zero = df_asset[df_asset[cols.VALUE_CURRENCY] == 0]
        if len(df_zero) > 0:
            return df_zero.iloc[0][cols.ACCOUNT_GUID]

        # Если есть счет с типом liability, то главный он
        if any(df_asset[cols.ACCOUNT_TYPE].isin([GNUCashBook.LIABILITY])):
            df = df_asset[df_asset[cols.ACCOUNT_TYPE].isin([GNUCashBook.LIABILITY])]
            return df.iloc[0][cols.ACCOUNT_GUID]
        # А здесь сложно понять кто главный
        # Берем счет с отрицательной суммой
        df = df_asset[df_asset[cols.VALUE_CURRENCY] < 0]
        if df.empty:
            print('Error detect master account for xirr')
            return None
        else:
            return df.iloc[0][cols.ACCOUNT_GUID]

    def _get_all_for_xirr(self, account_guids, from_date=None, to_date=None):
        """
        Возвращает все данные для подсчета xirr
        :param account_guids: 
        :param from_date: 
        :param to_date: 
        :return: 
        """
        df_splits = self._get_splits_for_xirr(account_guids=account_guids, from_date=from_date, to_date=to_date)
        df_balances = self._get_balances_for_xirr(account_guids=account_guids, from_date=from_date, to_date=to_date)
        df_all = pandas.concat([df_splits, df_balances], ignore_index=True, sort=True)
        return df_all

    def _get_balances_for_xirr(self, account_guids, from_date=None, to_date=None):
        """
        Возвращает начальный и конечный баланс для подсчета xirr
        :param account_guids: 
        :param from_date: 
        :param to_date: 
        :return: 
        """

        # Дата для конечного баланса
        end_date = to_date
        if not end_date:
            # end_date = self.max_date # Дата последней проводки в базе
            end_date = datetime.today()  # Текущая дата

        # Конечный баланс
        df_itog_balances = self.balance_on_date(end_date, account_guids=account_guids)

        # Добавление начального баланса
        if from_date:
            start_balances = self.balance_on_date(from_date, account_guids=account_guids, start_balance=True)
            # Начальный баланс - это потрачено
            start_balances[cols.VALUE_CURRENCY] = start_balances[cols.VALUE_CURRENCY] * (-1)

            df_itog_balances = pandas.concat([start_balances, df_itog_balances], ignore_index=True, sort=True)

        # Задать xirr_value и xirr_account
        df_itog_balances[cols.XIRR_VALUE] = df_itog_balances[cols.VALUE_CURRENCY]
        df_itog_balances[cols.XIRR_ACCOUNT] = df_itog_balances[cols.ACCOUNT_GUID]

        return df_itog_balances

    def _get_splits_for_xirr(self, account_guids, from_date=None, to_date=None):
        """
        Возвращает строки из df_splits, для подсчета xirr
        :param account_guids: 
        :param from_date: 
        :param to_date: 
        :return: dataframe
        """
        sel_df = (self.df_splits[(self.df_splits[cols.XIRR_ACCOUNT]).isin(account_guids)]).copy()

        # Фильтрация по времени
        if from_date:
            sel_df = sel_df[(sel_df[cols.POST_DATE] >= from_date)]
        if to_date:
            sel_df = sel_df[(sel_df[cols.POST_DATE] <= to_date)]

        return sel_df

    def _balance_group_by_period(self, from_date, to_date, period, account_types=None, drop_null=False, accounts=None, is_guid=False):
        """
        Группирует балансы по периоду у заданных типов счетов
        Возвращает DataFrame со всеми счетами сгруппированными по периоду (суммирует за период)

        :param from_date:
        :param to_date:
        :param period:
        :param account_types:
        :param drop_null:
        :return:
        """

        # Отбираем нужные колонки (почти все и нужны)
        sel_df = pandas.DataFrame(self.df_splits,
                                  columns=[cols.ACCOUNT_GUID, cols.POST_DATE, cols.FULLNAME, cols.COMMODITY_GUID, cols.ACCOUNT_TYPE,
                                           cols.CUM_SUM, cols.SHORTNAME, cols.HIDDEN, cols.MNEMONIC])
        # Фильтр по типам счетов
        if account_types:
            if type(account_types) is str:
                account_types = [account_types]
            sel_df = sel_df[(sel_df[cols.ACCOUNT_TYPE]).isin(account_types)]

        # Фильтр по именам счетов или guid счетов
        if accounts:
            if is_guid:
                sel_df = sel_df[(sel_df[cols.ACCOUNT_GUID]).isin(accounts)]
            else:
                sel_df = sel_df[(sel_df[cols.FULLNAME]).isin(accounts)]

        # Список всех account_guid
        account_guids = sel_df[cols.ACCOUNT_GUID].drop_duplicates().tolist()

        # Добавление колонки нарастающий итог по счетам
        # Будет ли нарастающий итог по порядку возрастания дат???? Нет! Нужно сначала отсортировать
        sel_df.rename(columns={cols.CUM_SUM: cols.VALUE}, inplace=True)

        # здесь подразумевается, что есть только одна цена за день
        # Поэтому отсекаем повторы
        sel_df.set_index([cols.ACCOUNT_GUID, cols.POST_DATE], inplace=True)
        # отсечение повторов по индексу
        sel_df = sel_df[~sel_df.index.duplicated(keep='last')]

        # Индекс по периоду
        idx = pandas.date_range(from_date, to_date, freq=period)

        # цикл по всем commodity_guid
        group_acc = pandas.DataFrame()
        for account_guid in account_guids:

            # DataFrame с датами и значениями
            df_acc = sel_df.loc[account_guid]
            if not df_acc.empty:

                df_acc = df_acc.resample(period).ffill()

                df_acc = df_acc.reindex(idx, method='ffill')
                # Здесь теряются все колонки если начинается с пустой

                if drop_null:
                    # Убрать если все значения 0
                    has_balances = not (df_acc[cols.VALUE].apply(lambda x: x == 0).all())
                else:
                    has_balances = True
                # Берем только не пустые счета
                if has_balances:
                    acc_info = self.df_accounts.loc[account_guid]
                    df_acc.index.name = cols.POST_DATE
                    df_acc[cols.ACCOUNT_GUID] = account_guid
                    df_acc[cols.FULLNAME] = acc_info[cols.FULLNAME]
                    df_acc[cols.COMMODITY_GUID] = acc_info[cols.COMMODITY_GUID]
                    df_acc[cols.ACCOUNT_TYPE] = acc_info[cols.ACCOUNT_TYPE]
                    df_acc[cols.SHORTNAME] = acc_info[cols.SHORTNAME]
                    df_acc[cols.HIDDEN] = acc_info[cols.HIDDEN]
                    df_acc[cols.MNEMONIC] = acc_info[cols.MNEMONIC]

                    df_acc.set_index(cols.ACCOUNT_GUID, append=True, inplace=True)
                    # Меняем местами индексы
                    df_acc = df_acc.swaplevel()

                    group_acc = group_acc.append(df_acc)

        # Сбрасываем один уровень индекса (post_date)
        group_acc.reset_index(inplace=True)

        # Заменяем Nan нулями
        group_acc.fillna(Decimal(0), inplace=True)

        return group_acc

    def balance_to_currency(self, from_date=None, to_date=None, accounts=None):
        """
        Возвращает баланс счетов по имени или guid счета на заданную дату с пересчетом в валюту представления
        :param on_date:
        :param accounts:
        :param is_guid:
        :return: DataFrame
        """

        # Отбираем нужные колонки
        sel_df = pandas.DataFrame(self.df_splits,
                                  columns=[cols.POST_DATE,
                                           cols.TRANSACTION_GUID,
                                           cols.ACCOUNT_GUID,
                                           cols.FULLNAME,
                                           cols.COMMODITY_GUID,
                                           cols.ACCOUNT_TYPE,
                                           cols.VALUE,
                                           cols.CUM_SUM,
                                           cols.SHORTNAME,
                                           cols.MNEMONIC,
                                           cols.CURRENCY_GUID])
        if accounts:
            # Выбранные счета
            if type(accounts) is str:
                accounts = [accounts]
            sel_df = sel_df[(sel_df[cols.FULLNAME]).isin(accounts)]
        else:
            # отбираем все счета с активами
            sel_df = sel_df[(sel_df[cols.ACCOUNT_TYPE]).isin(GNUCashBook.ALL_ASSET_TYPES)]

        # Фильтрация по времени
        if from_date:
            sel_df = sel_df[(sel_df[cols.POST_DATE] >= from_date)]

        if to_date:
            sel_df = sel_df[(sel_df[cols.POST_DATE] <= to_date)]



        # пересчет в нужную валюту
        group = self._currency_calc(sel_df, from_date=from_date)

        return group

    def balance_by_period(self, from_date, to_date, period='M', account_types=GNUCashBook.ALL_ASSET_TYPES, glevel=1,
                          margins = None, drop_null=False):
        """
        Возвращает сводный баланс по счетам за интервал дат с разбивкой по периодам
        :param from_date:
        :param to_date:
        :param period:
        :param account_types:
        :param glevel:
        :param margins:
        :param drop_null: Отбрасывать нулевые значения (итоги могут не содержать всех столбцов)
        :return: DataFrame
        """

        group_acc = self._balance_group_by_period(from_date=from_date, to_date=to_date, period=period,
                                                  account_types=account_types, drop_null=drop_null)

        # пересчет в нужную валюту
        group = self._currency_calc(group_acc)

        # Группировка по счетам
        group = self._group_by_accounts(group, glevel=glevel, drop_null=drop_null)
        # group = self._curcalc_and_accgroup(group_acc, from_date=from_date, to_date=to_date, period=period,
        #                                    glevel=glevel, margins=margins, drop_null=drop_null)

        # Добавление итогов
        group = self._add_margins(group, margins)

        return group

    def turnover_by_period(self, from_date, to_date, period='M', account_type=GNUCashBook.EXPENSE, glevel=1,
                           margins: Margins = None, drop_null=False):

        """
        Получение сводных оборотов по тратам/доходам за промежуток времени с разбивкой на периоды
        Например, ежемесячные траты за год. Возвращает DataFrame

        :param from_date: Start date
        :param to_date: Finish date
        :param period: "M" for month, "D" for day...
        :param account_type: INCOME or EXPENSE
        :param glevel: group level
        :return: pivot DataFrame
        """

        sel_df = self._turnover_group_by_period(from_date=from_date, to_date=to_date, period=period,
                                                account_type=account_type)

        # inverse income
        if account_type == GNUCashBook.INCOME:
            sel_df[cols.VALUE] = sel_df[cols.VALUE].apply(lambda x: -1 * x)

        # пересчет в нужную валюту
        group = self._currency_calc(sel_df)

        # Группировка по счетам
        group = self._group_by_accounts(group, glevel=glevel, drop_null=drop_null)

        # Здесь появляются нули
        # group.fillna(Decimal(0), inplace=True)

        # Добавление итогов
        group = self._add_margins(group, margins)

        group.replace(0, Decimal(0), inplace=True)

        return group

    def profit_by_period(self, from_date: date, to_date: date, period='M', glevel=1, margins: Margins = None):
        """
        Получение прибыли за период
        Возвращает DataFrame

        :param from_date: Start date
        :param to_date: Finish date
        :param period: "M" for month, "D" for day...
        :param account_type: INCOME or EXPENSE
        :param glevel: group level
        :param margins:
        :return: pivot DataFrame
        """

        income_and_expense = [GNUCashBook.INCOME, GNUCashBook.EXPENSE]

        # Группировка по периоду
        sel_df = self._turnover_group_by_period(from_date=from_date, to_date=to_date, period=period,
                                                account_type=income_and_expense)

        # пересчет в нужную валюту
        group = self._currency_calc(sel_df)
        # Группировка по счетам

        # Суммируем
        profit_name = _('Profit')
        if margins:
            profit_name = margins.profit_name
        df = self._sum_all(group, total_name=profit_name, glevel=glevel, inverse=True)

        # Добавление итогов
        df = self._add_margins(df, margins)

        return df

    def _sum_all(self, dataframe, total_name, glevel, inverse):
        """
        Суммирует все значения DataFrame, возвращает итоговую строку с именем total_name

        :param dataframe:
        :param total_name:
        :param glevel:
        :param inverse:
        :return:
        """

        # Суммируем
        # group = dataframe.groupby(cols.POST_DATE).value_currency.sum()
        group = dataframe.groupby(cols.POST_DATE).value_currency.sum()

        if inverse:
            group = group.map(lambda x: x * -1)

        # Переворот дат из строк в колонки
        df = pandas.DataFrame(group).T

        df.index = [total_name]

        # Нужно добавить колонки если Multiindex
        if type(glevel) is int:
            glevel = [glevel]
        idx_len = len(glevel)
        new_indexes = [str(i) for i in range(1, idx_len)]
        if new_indexes:
            # Нужно добавить уровни
            for col_name in new_indexes:
                df[col_name] = ''
            df.set_index(new_indexes, append=True, inplace=True)

        return df

    def _turnover_group_by_period(self, from_date, to_date, period, account_type):
        """
        Возвращает обороты по счетам сгруппированные по периодам
        :param from_date:
        :param to_date:
        :param period:
        :param account_type:
        :return:
        """
        if type(account_type) is str:
            account_type = [account_type]

        # Фильтрация по времени
        sel_df = self.df_splits[(self.df_splits[cols.POST_DATE] >= from_date)
                                & (self.df_splits[cols.POST_DATE] <= to_date)]

        # Отбираем нужные типы счетов
        sel_df = sel_df[(sel_df[cols.ACCOUNT_TYPE]).isin(account_type)]

        # Группировка по месяцу
        sel_df.set_index(cols.POST_DATE, inplace=True)
        sel_df = sel_df.groupby([pandas.Grouper(freq=period), cols.FULLNAME, cols.COMMODITY_GUID]).value.sum().reset_index()

        return sel_df

    def _currency_calc(self, dataframe,
                       col_value=cols.VALUE,
                       col_currency_guid=cols.COMMODITY_GUID,
                       col_rate=cols.RATE,
                       col_value_currency=cols.VALUE_CURRENCY
                       ):
        """
        Добавляет в dataframe колонку с курсом валюты и колонку со стоимостью в валюте учета
        Исходный datafrmae должен содержать поля:
        post_date - дата
        value - стоимость в валюте счета или кол-во ценных бумаг
        commodity_guid - guid счета или ценной бумаги
        Добавятся колонки:
        rate - курс в валюте  учета
        value_currency - стоимость в валюте учета
        исходный datafrmae должен быть сгруппирован по from_date, to_date, period
        Но функция его не группирует!
        :param dataframe:
        :param from_date:
        :param to_date:
        :param period:
        :return: DataFrame с добавленными колонками
        """

        df = dataframe

        # Определяем цены на нужные даты
        # group_prices = self.df_prices_days
        start_date = df[cols.POST_DATE].min()
        end_date = df[cols.POST_DATE].max()

        prices_on_dates = self._group_prices_by_period(start_date, end_date, 'D', col_rate=col_rate)

        # Добавление колонки курс
        if prices_on_dates.empty:
            df[col_rate] = 1
        else:
            df = df.merge(prices_on_dates, left_on=[col_currency_guid, cols.POST_DATE], right_index=True,
                          how='left')
        # Заполнить пустые поля еденицей
        df[col_rate] = df[col_rate].fillna(Decimal(1))

        # Пересчет в валюту представления
        df[col_value_currency] = (df[col_value] * df[col_rate]).apply(lambda x: round(x, 2))
        # Теперь в колонке value_currency реальная сумма в рублях

        # Конец пересчета в нужную валюту
        return df

    def _group_by_accounts(self, dataframe, glevel=1, drop_null=False):
        """
        Group dataframe by accounts, add totals
        glevel - group level of accounts: array of levels or single int level
        Example:
        glevel=[0, 1] - Group accounts for 0 and 1 level,
        into 2 rows and 2 columns (Multiindex dataframe):
        Assets - Current assets
               - reserve

        glevel=1 - groups only 1 level, into 2 rows and 1 column:
        Current assets
        reserve

        Accounts example:
            0   1               2 (account levels)
        Assets:Current assets:Cash
        Assets:Current assets:Card
        Assets:reserve:Deposite
        Assets:reserve:Cash


        Группирует dataframe по счетам, добавляет итоги
        glevel - Уровень группировки счетов: массив уровней или номер уровня
        Например:
        glevel=[0, 1] - Сгруппирует все счета с 0 по 1-ый уровень,
        будут две строки и два столбца (Multiindex dataframe):
        Активы - Текущие активы
               - Резервы

        glevel=1 - сгруппирует только первый уровень, будут две строки и один столбец:
        Текущие активы
        Резервы

        Пример счетов:
            0   1               2 (Уровни счетов)
        Активы:Текущие активы:Деньги
        Активы:Текущие активы:Карта
        Активы:Резервы:Депозит
        Активы:Резервы:Заначка

        :param dataframe:
        :param glevel: Уровень группировки счетов: массив уровней или номер уровня
        :param margins: Итоги
        :param drop_null:
        :return:
        """

        # Отбираем нужные колонки
        sel_df = pandas.DataFrame(dataframe,
                                  columns=[cols.POST_DATE, cols.FULLNAME, cols.VALUE_CURRENCY]).copy()

        # Добавление MultiIndex по дате и названиям счетов
        # Get dataframe where fullname split to parts (only these parts)
        s = sel_df[cols.FULLNAME].str.split(':', expand=True)
        # change columns name type from int to string, for new version Pandas
        s.rename(str, axis='columns', inplace=True)
        # Get list of column name's of fullname parts
        columns = s.columns
        columns = columns.tolist()
        columns = [cols.POST_DATE] + columns
        # Add splitted fullname columns
        sel_df = pandas.concat([sel_df, s], axis=1)

        sel_df.sort_values(by=columns, inplace=True)  # Сортировка по дате и счетам

        if drop_null:
            sel_df.dropna(subset=[cols.VALUE_CURRENCY], inplace=True)  # Удаление пустых значений
            # sel_df = sel_df[sel_df[cols.VALUE] != 0]  # Удаление нулевых значений

        sel_df.drop(cols.FULLNAME, axis=1, inplace=True)  # Удаление колонки fullname

        # set index by date and splitted fulname columns
        sel_df.set_index(columns, inplace=True)

        # Переворот дат из строк в колонки
        # date index to column
        unst = sel_df.unstack(level=cols.POST_DATE, fill_value=0)

        # delete column level header
        unst.columns = unst.columns.droplevel()

        # Группировка по нужному уровню
        group = unst.groupby(level=glevel).sum()

        return group



    def inflation_by_period(self, from_date, to_date, period='A', glevel=1, cumulative=False):
        """
        Calcs inflation by periods. Return DataFrame with percent of inflation
        :param from_date:
        :param to_date:
        :param period:
        :param glevel:
        :param cumulative: in each column calculate cumulative inflation to the first column (True)
         or inflation to the previous column (False)
        :return: DataFrame
        """
        # Calculate expenses
        margins = Margins()
        margins.total_row = True
        df = self.turnover_by_period(from_date=from_date, to_date=to_date, period=period,
                                     account_type=GNUCashBook.EXPENSE, glevel=glevel, margins=margins)

        # Empty Dataframe with same columns and index
        df_inf = pandas.DataFrame(index=df.index, columns=df.columns[1:])

        columns = df.columns

        for i in range(1, len(columns)):

            if not cumulative:
                # Процент к предыдущему
                df_inf[columns[i]] = self._percent_increase(df[columns[i-1]], df[columns[i]])
            else:
                # Процент к началу
                df_inf[columns[i]] = self._percent_increase(df[columns[0]], df[columns[i]], i)

        # Average by period
        if not cumulative:
            i2 = len(columns) - 1
            df_inf[('Total')] = self._percent_increase(df[columns[0]], df[columns[i2]], i2)

        return df_inf

    @staticmethod
    def _percent_increase(a_ser, b_ser, distance=1):
        """
        Return percent increase between two series
        :param a_ser: First series
        :param b_ser: Last series
        :param distance: time counts between series
        :return: series: percent increase
        """
        i_ser = ((b_ser.astype('float64')).divide(a_ser.astype('float64'))).pow(1 / distance) - 1
        return i_ser

    def _group_prices_by_period(self, from_date, to_date, period='M', guids=None, col_rate=cols.RATE):
        """
        Получение курса/цен активов за период
        Возвращает таблицу с ценой каждого актива на конец периода (по последней ближайшей к дате)
        Возвращаемый DataFrame содержит индекс и столбцы
        [cols.COMMODITY_GUID, 'date'] ([cols.MNEMONIC, cols.CURRENCY_GUID, cols.RATE], dtype='object')
        rate - курс
        :param from_date:
        :param to_date:
        :param period:
        :param guids: Список commodities_guids или None для всех
        :return: DataFrame with grouped prices
        """

        all_commodities_guids = set(self.df_prices.index.get_level_values(cols.COMMODITY_GUID).drop_duplicates().tolist())

        # Индекс по периоду

        from_date2 = from_date
        to_date2 = to_date
        if not from_date:
            from_date2 = self.min_date
        if not to_date:
            to_date2 = self.max_date

        idx = pandas.date_range(from_date2, to_date2, freq=period)

        # Список commodities guids
        if guids is None:
            guids_list = all_commodities_guids
        else:
            guids_list = set(guids) & all_commodities_guids

        # здесь подразумевается, что есть только одна цена за день
        sel_df = pandas.DataFrame(self.df_prices,
                                  columns=[cols.MNEMONIC, cols.CURRENCY_GUID, cols.VALUE])

        # цикл по всем commodity_guid
        group_prices = pandas.DataFrame()
        for commodity_guid in guids_list:

            # DataFrame с датами и значениями
            sel_mnem = sel_df.loc[commodity_guid]
            if not sel_mnem.empty:
                sel_mnem = sel_mnem.resample(period).ffill()

                sel_mnem = sel_mnem.reindex(idx, method='nearest')
                sel_mnem.index.name = 'date'
                sel_mnem[cols.COMMODITY_GUID] = commodity_guid
                sel_mnem.set_index(cols.COMMODITY_GUID, append=True, inplace=True)
                # Меняем местами индексы
                sel_mnem = sel_mnem.swaplevel()

                group_prices = group_prices.append(sel_mnem)

        # Список guid всех нужных валют
        if group_prices.empty:
            currency_guids=None
        else:
            currency_guids = set(group_prices[cols.CURRENCY_GUID].drop_duplicates().tolist()) & all_commodities_guids

        if currency_guids:
            # TODO: Здесь нужен пересчет в валюту представления
            pass

        # Теперь в колонке rate курс ценной бумаги в рублях
        group_prices.rename(columns={cols.VALUE: col_rate, cols.CURRENCY_GUID: cols.PRICE_CURRENCY_GUID}, inplace=True)
        return group_prices

