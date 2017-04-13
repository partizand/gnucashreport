import gettext
import locale
import os
from copy import copy
from datetime import date
from decimal import Decimal
from operator import attrgetter

import pandas
import numpy
import piecash
from gnucashreport.utils import dataframe_to_excel

from gnucashreport.financial import xirr, xirr_simple
from gnucashreport.gcxmlreader import GNUCashXMLBook
from gnucashreport.margins import Margins

#ACCOUNT_GUID = 'account_guid'

POST_DATE = 'post_date'

FULLNAME = 'fullname'


class GNUCashData:
    """
    Low level DataFrame implementation of GnuCash database tables for build reports
    Basic reports

    """

    # GnuCash account types
    CASH = 'CASH'
    BANK = 'BANK'
    ASSET = 'ASSET'
    STOCK = 'STOCK'
    MUTUAL = 'MUTUAL'
    INCOME = 'INCOME'
    EXPENSE = 'EXPENSE'
    EQUITY = 'EQUITY'
    LIABILITY = 'LIABILITY'
    ROOT = 'ROOT'
    # GNUCash all account assets types
    ALL_ASSET_TYPES = [CASH, BANK, ASSET, STOCK, MUTUAL]

    # All account types for calc yield by xirr
    ALL_XIRR_TYPES = [BANK, ASSET, STOCK, MUTUAL, LIABILITY]
    ASSET_XIRR_TYPES = [BANK, ASSET, LIABILITY]
    STOCK_XIRR_TYPES = [STOCK, MUTUAL]
    INCEXP_XIRR_TYPES = [INCOME, EXPENSE]

    # Данные для генерации тестовых данных и тестирования
    dir_pickle = 'V:/test_data'
    # dir_testdata = 'v:/test_data'

    pickle_prices = 'prices.pkl'
    pickle_splits = 'splits.pkl'
    pickle_accounts = 'accounts.pkl'
    pickle_tr = 'transactions.pkl'
    pickle_commodities = 'commodities.pkl'

    dir_excel = "v:/tables"

    def __init__(self):
        self.df_accounts = pandas.DataFrame()
        self.df_transactions = pandas.DataFrame()
        self.df_commodities = pandas.DataFrame()
        self.df_splits = pandas.DataFrame()
        self.df_prices = pandas.DataFrame()

        self.book_name = None
        self.root_account_guid = None

        # internalization
        self.set_locale()

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

    def open_book_file(self, filename, readonly=True, open_if_lock=False,):
        """
        Open GnuCash database file. Autodetect type: sqlite or xml
        :param filename:
        :param readonly: only for sqlite
        :param open_if_lock: only for sqlite
        :return:
        """
        # Detect version - sql or xml

        # Every valid SQLite database file begins with the following 16 bytes (in hex):
        #  53 51 4c 69 74 65 20 66 6f 72 6d 61 74 20 33 00.
        # This byte sequence corresponds to the UTF-8 string "SQLite format 3"
        # including the nul terminator character at the end.
        # Read sqllite signature
        with open(filename, "rb") as f:
            bytes = f.read(16)
        if bytes == b'SQLite format 3\x00':
            self.open_book_sql(sqlite_file=filename, readonly=readonly, open_if_lock=open_if_lock)
        else:
            self._open_book_xml(filename)

    def _open_book_xml(self, xml_file):
        """
        Opens gnucash book from xml file
        :param xml_file:
        :return:
        """
        self._read_book_xml(xml_file)
        self._after_read()

    def open_book_sql(self,
                      sqlite_file=None,
                      uri_conn=None,
                      readonly=True,
                      open_if_lock=False,
                      do_backup=True,
                      db_type=None,
                      db_user=None,
                      db_password=None,
                      db_name=None,
                      db_host=None,
                      db_port=None,
                       **kwargs):
        """
        Opens gnucash book from sql. See piecash help for sql details
        :param str sqlite_file: a path to an sqlite3 file (only used if uri_conn is None)
        :param str uri_conn: a sqlalchemy connection string
        :param bool readonly: open the file as readonly (useful to play with and avoid any unwanted save)
        :param bool open_if_lock: open the file even if it is locked by another user
            (using open_if_lock=True with readonly=False is not recommended)
        :param bool do_backup: do a backup if the file written in RW (i.e. readonly=False)
            (this only works with the sqlite backend and copy the file with .{:%Y%m%d%H%M%S}.gnucash appended to it)
        :raises GnucashException: if the document does not exist
        :raises GnucashException: if there is a lock on the file and open_if_lock is False
        :return:
        """
        self._read_book_sql(sqlite_file=sqlite_file,
                               uri_conn=uri_conn,
                               readonly=readonly,
                               open_if_lock=open_if_lock,
                               do_backup=do_backup,
                               db_type=db_type,
                               db_user=db_user,
                               db_password=db_password,
                               db_name=db_name,
                               db_host=db_host,
                               db_port=db_port,
                               **kwargs)
        self._after_read()

    def _open_book_pickle(self, folder):
        """
        For test purpose
        Чтение базы из pickle файлов каталога. Если указан год, грузится только этот год (для ускорения)
        Loading from sql --- 6.193211078643799 seconds ---
        Loading from pickle all --- 0.09360003471374512 seconds ---
        Loading from pickle 2016 --- 0.031199932098388672 seconds ---

        :param year: Год для загрузки, None - все данные
        :param folder: Каталог с файлами базы
        :return:
        """

        self._read_book_pickle(folder=folder)
        self._after_read()

    def _read_book_pickle(self, folder=None):
        """
        For testing
        :param folder:
        :return:
        """
        self.df_accounts = self._dataframe_from_pickle(self.pickle_accounts, folder=folder)
        # dataframe_to_excel(self.df_accounts, 'accounts-source')
        self.df_commodities = self._dataframe_from_pickle(self.pickle_commodities, folder=folder)
        self.df_prices = self._dataframe_from_pickle(self.pickle_prices, folder=folder)
        self.df_transactions = self._dataframe_from_pickle(self.pickle_tr, folder=folder)
        self.df_splits = self._dataframe_from_pickle(self.pickle_splits, folder=folder)
        self._get_guid_rootaccount()
        # print(guid)
        # self.root_account_guid = gnucash_book.root_account.guid

    def _get_guid_rootaccount(self):
        """
        Get root account guid from df_accounts
        :return:
        """
        df_root = self.df_accounts[(self.df_accounts['account_type'] == self.ROOT) &
                                   (self.df_accounts['name'] == 'Root Account')]
        self.root_account_guid = df_root.index.values[0]

    def _dataframe_from_pickle(self, filename, folder=None):
        """
        Get dataframe from pickle file
        :param filename: Полное или короткое имя файла
        :param folder: Каталог с файлом
        :return: DataFrame
        """
        if not folder:
            folder = self.dir_pickle
        fullfilename = os.path.join(folder, filename)
        df = pandas.read_pickle(fullfilename)
        return df

    def _read_book_xml(self, xml_file):

        # read contens of the book
        book = GNUCashXMLBook()
        book.read_from_xml(xml_file)

        # Accounts

        fields = ["guid", "name", "actype",
                  "commodity_guid", "commodity_scu",
                  "parent_guid", "description", "hidden"]

        self.df_accounts = self._object_to_dataframe(book.accounts, fields)
        self.df_accounts.rename(columns={'actype': 'account_type'}, inplace=True)
        self.root_account_guid = book.root_account_guid

        # Transactions

        fields = ["guid", "currency_guid", "date", "description"]

        self.df_transactions = self._object_to_dataframe(book.transactions, fields)
        self.df_transactions.rename(columns={'date': 'post_date'}, inplace=True)

        # Splits
        fields = ["guid", "transaction_guid", "account_guid",
                  "memo", "reconcile_state", "value", "quantity"]

        self.df_splits = self._object_to_dataframe(book.splits, fields)

        # commodity

        fields = ["guid", "space", "mnemonic"]
        self.df_commodities = self._object_to_dataframe(book.commodities, fields)
        self.df_commodities.rename(columns={'space': 'namespace'}, inplace=True)
        self.df_commodities = self.df_commodities[self.df_commodities['namespace'] != 'template']

        # Prices
        fields = ["guid", "commodity_guid", "currency_guid",
                  "date", "source", "price_type", "value"]
        self.df_prices = self._object_to_dataframe(book.prices, fields)
        self.df_prices.rename(columns={'price_type': 'type'}, inplace=True)

    def _read_book_sql(self,
                       sqlite_file=None,
                       uri_conn=None,
                       readonly=True,
                       open_if_lock=False,
                       do_backup=True,
                       db_type=None,
                       db_user=None,
                       db_password=None,
                       db_name=None,
                       db_host=None,
                       db_port=None,
                       **kwargs):
        """Open an existing GnuCash sql book, read data to DataFrames

        :param str sqlite_file: a path to an sqlite3 file (only used if uri_conn is None)
        :param str uri_conn: a sqlalchemy connection string
        :param bool readonly: open the file as readonly (useful to play with and avoid any unwanted save)
        :param bool open_if_lock: open the file even if it is locked by another user
            (using open_if_lock=True with readonly=False is not recommended)
        :param bool do_backup: do a backup if the file written in RW (i.e. readonly=False)
            (this only works with the sqlite backend and copy the file with .{:%Y%m%d%H%M%S}.gnucash appended to it)
        :raises GnucashException: if the document does not exist
        :raises GnucashException: if there is a lock on the file and open_if_lock is False
        :return:
        """

        self.book_name = os.path.basename(sqlite_file)
        with piecash.open_book(sqlite_file=sqlite_file,
                               uri_conn=uri_conn,
                               readonly=readonly,
                               open_if_lock=open_if_lock,
                               do_backup=do_backup,
                               db_type=db_type,
                               db_user=db_user,
                               db_password=db_password,
                               db_name=db_name,
                               db_host=db_host,
                               db_port=db_port,
                               **kwargs
                               ) as gnucash_book:
            # Read data tables in dataframes

            # commodities

            t_commodities = gnucash_book.session.query(piecash.Commodity).filter(
                piecash.Commodity.namespace != "template").all()
            fields = ["guid", "namespace", "mnemonic",
                      "fullname", "cusip", "fraction",
                      "quote_flag", "quote_source", "quote_tz"]
            self.df_commodities = self._object_to_dataframe(t_commodities, fields)

            # Accounts

            self.root_account_guid = gnucash_book.root_account.guid
            t_accounts = gnucash_book.session.query(piecash.Account).all()
            fields = ["guid", "name", "type", "placeholder",
                      "commodity_guid", "commodity_scu",
                      "parent_guid", "description", "hidden"]
            self.df_accounts = self._object_to_dataframe(t_accounts, fields)
            # rename to real base name of field from piecash name
            self.df_accounts.rename(columns={'type': 'account_type'}, inplace=True)
            # self.dataframe_to_excel(self.df_accounts, 'acc-sql')

            # Transactions

            t_transactions = gnucash_book.session.query(piecash.Transaction).all()
            fields = ["guid", "currency_guid", "num",
                      "post_date", "description"]
            self.df_transactions = self._object_to_dataframe(t_transactions, fields)

            # Splits

            t_splits = gnucash_book.session.query(piecash.Split).all()
            fields = ["guid", "transaction_guid", "account_guid",
                      "memo", "action", "reconcile_state",
                      "value",
                      "quantity", "lot_guid"]
            self.df_splits = self._object_to_dataframe(t_splits, fields)

            # Prices

            # Get from piecash
            t_prices = gnucash_book.session.query(piecash.Price).all()
            # Some fields not correspond to real names in DB
            fields = ["guid", "commodity_guid", "currency_guid",
                      "date", "source", "type", "value"]
            self.df_prices = self._object_to_dataframe(t_prices, fields)

            # dataframe_to_excel(self.df_accounts, 'accounts-source-sql')

        # BaseTest._save_db_to_pickle(BaseTest.dir_testdata)


    def _after_read(self):
        """
        Some manipulation with dataframes after load data
        :return:
        """

        #  Get fullname of accounts
        self.df_accounts['fullname'] = self.df_accounts.index.map(self._get_fullname_account)

        # Add commodity mnemonic to accounts
        mems = self.df_commodities['mnemonic'].to_frame()
        self.df_accounts = pandas.merge(self.df_accounts, mems, left_on='commodity_guid', right_index=True)

        # Convert datetme to date in transactions (skip time)
        self.df_transactions['post_date'] = self.df_transactions['post_date'].apply(
            lambda x: pandas.to_datetime(x.date()))

        # Merge prices with commodities
        self.df_prices = pandas.merge(self.df_prices, self.df_commodities, left_on='commodity_guid',
                                      right_index=True)
        # Convert datetme to date in prices (skip time)
        self.df_prices['date'] = self.df_prices['date'].apply(lambda x: pandas.to_datetime(x.date()))

        # merge splits and accounts
        df_acc_splits = pandas.merge(self.df_splits, self.df_accounts, left_on='account_guid',
                                     right_index=True)
        df_acc_splits.rename(columns={'description': 'description_account'}, inplace=True)
        # merge splits and accounts with transactions
        self.df_splits = pandas.merge(df_acc_splits, self.df_transactions, left_on='transaction_guid',
                                      right_index=True)
        # Убрать время из даты проводки
        # self.df_splits['post_date'] = self.df_splits['post_date'].dt.date
        # self.df_splits['post_date'] = pandas.to_datetime(self.df_splits['post_date'])

        # Оставляем только одну цену за день в df_prices
        # Установка нового индекса
        self.df_prices.set_index(['commodity_guid', 'date'], inplace=True)
        # отсечение повторов по индексу
        self.df_prices = self.df_prices[~self.df_prices.index.duplicated(keep='last')]

        # Минимальная и максимальная даты в базе
        self.min_date = self.df_splits['post_date'].min()
        self.max_date = self.df_splits['post_date'].max()

        # Цены за каждый день по каждому инструменту
        self.df_prices_days = self._group_prices_by_period(self.min_date, self.max_date, 'D')


        # Сворачиваем df_splits до дней

        # start_time = time.time()
        # Подсчитываем нарастающий итог
        # print('Start calculating cum sum')
        self.df_splits.sort_values(by='post_date', inplace=True)
        # self.df_splits['cum_sum'] = self.df_splits.quantity.cumsum()
        self.df_splits['cum_sum'] = self.df_splits.groupby('fullname')['quantity'].transform(pandas.Series.cumsum)
        # print("Calculating cum sum --- %s seconds ---" % (time.time() - start_time))

        # Пересчет транзакций в валюту учета
        self._splits_currency_calc()

        # Подсчет значений для xirr
        self._add_xirr_info()



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
        cols = dataframe.columns.tolist()
        df_ret = dataframe.copy()
        # Добавление пустого столбца
        if margins.empty_col:
            df_ret[''] = ''
        if margins.total_col:
            df_ret[margins.total_name] = df_ret[cols].sum(axis=1)
        if margins.mean_col:
            df_ret[margins.mean_name] = df_ret[cols].mean(axis=1)

        return df_ret

    def _add_row_total(self, dataframe, margins=None):

        total_name = _('Total')
        if margins:
            total_name = margins.total_name
        if isinstance(dataframe.index, pandas.core.index.MultiIndex):

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

    def equity_by_period(self, from_date, to_date, period='M', glevel=1, margins: Margins = None):
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
        assets_and_liability = copy(GNUCashData.ALL_ASSET_TYPES)
        assets_and_liability.append(GNUCashData.LIABILITY)

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

    def balance_on_date(self, on_date, account_names=None, account_guids=None):
        """
        Возвращает DataFrame со строками балансов выбранных счетов на заданную дату (если баланс 0, строки не будет)
        Баланс в кол-ве бумаг - cum_sum
        Баланс в валюте учета - value_currency
        :param on_date: 
        :param account_names: 
        :param account_guids: 
        :return: DataFrame с балансами
        """

        # df = pandas.DataFrame(self.df_splits,
        #                           columns=['post_date',
        #                                    # 'transaction_guid',
        #                                    'account_guid',
        #                                    'fullname',
        #                                    'commodity_guid',
        #                                    'account_type',
        #                                    # 'value',
        #                                    'cum_sum',
        #                                    'name',
        #                                    # 'mnemonic'
        #                                    ])
        # df = self.df_splits.copy()
        # Сортировка по дате
        df = (self.df_splits[(self.df_splits['post_date'] < on_date)]).copy()
        # Сортировка по счетам
        if account_names:
            df = df[(df['fullname']).isin(account_names)]
        if account_guids:
            df = df[(df['account_guid']).isin(account_guids)]

        # Установка индекса по account_guid
        df['guid'] = df.index
        df.set_index('account_guid', inplace=True, drop=False)
        # отсечение повторов по индексу
        df = df[~df.index.duplicated(keep='last')]
        # Теперь в cum_sum - остаток по счету на дату (если он есть)
        df['post_date'] = numpy.datetime64(on_date)
        df.rename(columns={'cum_sum': 'value'}, inplace=True)
        df = self._currency_calc(df)
        # Теперь в value_currency - остаток в валюте учета (если он есть)
        # df['account_guid'] = df.index
        df.set_index('guid', inplace=True)
        return df

    def yield_calc(self, account_guid=None, account_name=None, account_types=None, from_date=None, to_date=None):

        ar_xirr = self._xirr_child_calc_array(account_guid=account_guid, account_name=account_name,
                                              account_types=account_types, from_date=from_date, to_date=to_date)

        # Колонки в нужной последовательности
        df = pandas.DataFrame(ar_xirr, columns=['name', 'yield_total', 'yield_income', 'yield_expense', 'yield_without_expense'])


        # Добавление MultiIndex по дате и названиям счетов
        # s = df['fullname'].str.split(':', expand=True)
        # cols = s.columns
        # cols = cols.tolist()
        # df = pandas.concat([df, s], axis=1)
        #
        # df.sort_values(by=cols, inplace=True)  # Сортировка по дате и счетам
        #
        # df.drop('fullname', axis=1, inplace=True)  # Удаление колонки fullname
        # df.set_index(cols, inplace=True)

        return df

    def _xirr_child_calc_array(self, account_guid=None, account_name=None, account_types=None, from_date=None, to_date=None):

        root_guid = account_guid

        if not root_guid:
            if account_name:
                root_guid = self._get_account_guid(account_name)
            elif account_types:
                root_guid = self.root_account_guid

        # Теперь в root_guid счет с которого нужно начинать
        # Нужно посчитать его доходность и доходности его потомков

        ar_xirr = []

        if root_guid != self.root_account_guid:
            xirr_root = self._xirr_calc(root_guid, account_types=account_types, from_date=from_date, to_date=to_date)
            ar_xirr += [xirr_root]

        childs = self._get_child_accounts(account_guid=root_guid, account_types=account_types, recurse=False)
        # if root_guid != self.root_account_guid:
        #     childs = [root_guid] + childs

        for child in childs:
            # xirr_current = self._xirr_calc(root_guid, account_types=account_types, from_date=from_date, to_date=to_date)
            # ar_xirr.append(xirr_current)

            sub_xirr = self._xirr_child_calc_array(account_guid=child, account_types=account_types)
            ar_xirr += sub_xirr

        # df_xirr = pandas.DataFrame(ar_xirr)

        return ar_xirr

    def _get_child_accounts(self, account_guid, account_types=None, recurse=True):
        """
        Возвращает список счетов потомков
        recurse=True - Список всех потомков
        recurse=False - Только потомки первого уровня
        :param account_guid: 
        :return: 
        """
        df = self.df_accounts.copy()
        # Фильтрация по типам счетов
        if account_types:
            df = df[(df['account_type']).isin(account_types)]

        df = df[df['parent_guid'] == account_guid]
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
        idx = self.df_accounts[self.df_accounts['fullname'] == fullname].index.tolist()
        if idx:
            return idx[0]
        else:
            return None

    def _xirr_calc(self, account_guid, account_types=None, from_date=None, to_date=None):
        """
        Возвращает доходность итоговую по указанному счету и его потомков за заданный период
        :param from_date: 
        :param to_date: 
        :param accounts: 
        :return: 
        """
        child_guids = self._get_child_accounts(account_guid, account_types=account_types, recurse=True)
        account_guids = [account_guid] + child_guids
        df_values = self._filter_for_xirr(account_guids=account_guids, from_date=from_date, to_date=to_date)
        df_income = self._find_income_for_xirr(df_values, self.INCOME)
        df_expense = self._find_income_for_xirr(df_values, self.EXPENSE)

        # Отбор только не нулевых проводок
        df_values = df_values[df_values['value_currency'] != 0]

        # df_total = pandas.concat([df_values, df_expense, df_income], ignore_index=True)
        # df_total.sort_values(by='post_date', inplace=True)

        # dataframe_to_excel(df_total, 'df_total')

        # Общая доходность
        yield_total = self._xirr_by_dataframe([df_values, df_income, df_expense])
        # Доходность дивидендов
        without_income_yeld = self._xirr_by_dataframe([df_values, df_expense])
        yield_without_expense = self._xirr_by_dataframe([df_values, df_income])

        yield_expense = yield_without_expense - yield_total
        if df_income.empty:
            yield_income = 0
        else:
            yield_income = yield_total - without_income_yeld

        itog = {}
        # itog['account_guid'] = account_guid
        itog['fullname'] = self.df_accounts.loc[account_guid]['fullname']
        itog['name'] = self.df_accounts.loc[account_guid]['name']
        itog['yield_total'] = yield_total
        # itog['yield_total2'] = yield_total
        itog['yield_income'] = yield_income
        itog['yield_expense'] = yield_expense
        itog['yield_without_expense'] = yield_without_expense
        
        # print(yield_total)
        # print(yield_income)
        # print(yield_expense)
        # print(yield_without_expense)

        return itog

        # return df_total

    def _xirr_by_dataframe(self, obj, date_field='post_date', value_field='value_currency'):
        """
        Считает функцию xirr по значениям dataframe. obj может быть просто dataframe или массивом dataframe
        Тогда они сложатся
        :param obj: DataFrame or array of dataframes
        :param date_field: Name of date column
        :param value_field: Name of value column
        :return: annual yield
        """
        if isinstance(obj, pandas.DataFrame):
            df = pandas.DataFrame(obj, columns=[date_field, value_field])
        else:
            df = pandas.concat(obj, ignore_index=True)
            df.sort_values(by=date_field, inplace=True)
            df = pandas.DataFrame(df, columns=[date_field, value_field])
        # df['date'] = df[date_field].astype('O')
        df[date_field] = df[date_field].astype(date)
        tuples = [tuple(x) for x in df.to_records(index=False)]
        a_yield = xirr_simple(tuples)
        a_yield = round(a_yield, 4)
        # print(a_yield)
        return a_yield

    def _add_xirr_info(self):
        # Добавление столбцов для xirr в df_splits
        self.df_splits['xirr_account'] = ''
        self.df_splits['xirr_value'] = ''
        # self.df_splits['tr_acc_names'] = ''
        # Идем по транзакциям
        tr_guids_all = self.df_splits['transaction_guid'].drop_duplicates().tolist()

        for tr_guid in tr_guids_all:
            self._add_xirr_by_transaction(tr_guid)

        # dataframe_to_excel(self.df_splits, 'test-split')

    def _add_xirr_by_transaction(self, transaction_guid):
        """
        Добавляет значения в поля xirr_account и xirr_value в df_splits
        Согласно правил, описанных в excel нике
        Возможно можно оптимизировать быстродействие
        :param transaction_guid: 
        :return: 
        """
        df_tr_splits = self.df_splits[self.df_splits['transaction_guid'] == transaction_guid]
        # для тестовыых целей. Выборочная проверка верна. Пока отключаю
        # self._add_tr_acc_names(df_tr_splits)

        # есть ли счета для xirr
        if not self._has_transaction_for_xirr(df_tr_splits):
            return
        df_incexps = df_tr_splits[df_tr_splits['account_type'].isin([self.INCOME, self.EXPENSE])]
        df_assets = df_tr_splits[df_tr_splits['account_type'].isin(self.ASSET_XIRR_TYPES)]
        df_all_xirr_types = df_tr_splits[df_tr_splits['account_type'].isin(self.ALL_XIRR_TYPES)]
        df_stocks = df_tr_splits[df_tr_splits['account_type'].isin(self.STOCK_XIRR_TYPES)]
        # df_equity = df_tr_splits[df_tr_splits['account_type'] == self.EQUITY]


        # Простая 2-х проводочная транзакция
        if len(df_tr_splits) == 2:

            if (len(df_incexps) == 1) and (len(df_assets) == 1):
                # income or expense to asset
                guid_asset = df_assets.iloc[0]['account_guid']
                self._add_xirr_value(df_incexps, xirr_account=guid_asset)
                return
            elif (len(df_stocks) == 1) and (len(df_incexps) == 1):
                # ignore, gain income, капитальные прибыли или убытки,
                return
            elif (any(df_tr_splits['account_type'].isin([self.EQUITY, self.CASH]))) and (len(df_all_xirr_types) == 1):
                # Остатки
                self._add_xirr_value(df_all_xirr_types)

            elif len(df_all_xirr_types) == 2:
                # asset to asset
                self._add_xirr_value(df_all_xirr_types)
                return
            else:
                # Неясность
                print("Unknown transaction type for xirr. Transaction_guid {tr_guid}".format(tr_guid=transaction_guid))
                return

        # Multi transaction
        if len(df_all_xirr_types) > 0: # Это условие всегда верно
            self._add_xirr_value(df_all_xirr_types)
            # Тут нужно определить счет на который пойдут прибыли или убытки
            asset_guid = self._get_master_asset_guid(df_all_xirr_types)
            self._add_xirr_value(df_incexps, xirr_account=asset_guid)
        else:
            # Неясность
            print("Unknown multi transaction type for xirr. Transaction_guid {tr_guid}".format(tr_guid=transaction_guid))
            return


    def _add_tr_acc_names(self, dataframe):
        """
        Для тестовых целей, пишет в поле tr_acc_names все имена счетов участвующие в транзакции через запятую
        Для поиска всех связанных со счетом split в excel
        :param dataframe: 
        :return: 
        """
        tr_acc_names = dataframe['name'].drop_duplicates().tolist()
        tr_acc_names = ','.join(tr_acc_names)
        self.df_splits.loc[dataframe.index.values, 'tr_acc_names'] = tr_acc_names



    def _get_master_asset_guid(self, dataframe):
        """
        dataframe - отобранные проводки из df_splits
        Находит из них ту, на которую писать доход/убыток
        Возвращает account_guid для отобранного счета
        :param dataframe: 
        :return: account_guid
        """
        if len(dataframe) == 1:
            return dataframe.iloc[0]['account_guid']
        # если есть тип stock, то он главный
        if any(dataframe['account_type'].isin(self.STOCK_XIRR_TYPES)):
            df = dataframe[dataframe['account_type'].isin(self.STOCK_XIRR_TYPES)]
            return df.iloc[0]['account_guid']
        # Главный счет у которого value меньше по модулю
        df = dataframe.copy()
        df['value_sort'] = df['value_currency'].map(lambda x: abs(x))
        df.sort_values('value_sort')
        return df.iloc[0]['account_guid']

    def _add_xirr_value(self, dataframe, xirr_account=None):
        """
        Добавляет в df_splits значения для xirr_value и xirr_account из dataframe
        dataframe - Это отобранные строки из df_splits
        Если xirr_account = None, то записывается account_guid строки, иначе переданный guid
        xirr_value = value_currency * -1
        :param dataframe: 
        :param xirr_account: 
        :return: 
        """

        for index in dataframe.index.values:
            value_currency = self.df_splits.loc[index, 'value_currency']
            if value_currency != 0:
                self.df_splits.loc[index, 'xirr_value'] = value_currency * -1
                if xirr_account:
                    self.df_splits.loc[index, 'xirr_account'] = xirr_account
                else:
                    self.df_splits.loc[index, 'xirr_account'] = self.df_splits.loc[index, 'account_guid']

    def _has_transaction_for_xirr(self, df_tr_splits):
        """
        Проверка, есть ли в транзакции проводки, для которых необходимо считать xirr
        true - есть
        false - нет
        :param df_tr_splits: 
        :return: 
        """
        # return True
        # all_types = df_tr_splits['account_type'].drop_duplicates().tolist()
        # for cur_type in all_types:
        #     if cur_type in self.ALL_XIRR_TYPES:
        #         return True
        if any(df_tr_splits['account_type'].isin(self.ALL_XIRR_TYPES)):
            return True
        else:
            return False

    # def _add_xirr_guids(self):
    #     """
    #     Добавляет новое поле в df_splits для подсчета xirr
    #     :return:
    #     """
    #     self.df_splits['xirr_guid'] = self.df_splits.apply(lambda row: self._func_for_xirr(row), axis=1)
    #     # df = self.df_splits[(self.df_splits['account_type']).isin(self.ALL_XIRR_TYPES)]
    #     # df['xirr_guid'] = df['account_guid']
    #     dataframe_to_excel(self.df_splits, 'splits_xirr')

    # def _func_for_xirr(self, row):
    #     """
    #     Функция для applay для df_splits
    #     Возвращает значение для нового поля xirr_guid
    #     :param row:
    #     :return: xirr_guid строка
    #     """
    #     if row['account_type'] in self.ALL_XIRR_TYPES:
    #         if row['value_currency'] == 0:
    #             return None
    #         else:
    #             # Здесть нужно удалить не нулевые строки, которым соответствует таже сумма INCOME
    #             df_r_splits = self._get_related_splits(row)
    #             if len(df_r_splits) == 1:
    #                 if df_r_splits.iloc[0]['account_type'] == self.INCOME:
    #                     return None
    #             return row['account_guid']
    #     elif row['account_type'] == self.INCOME:
    #         asset_row = self._get_related_asset_account(row)
    #         if asset_row and (asset_row['value_currency'] == 0):
    #             return asset_row['account_guid']
    #         else:
    #             return None
    #     elif row['account_type'] == self.EXPENSE:
    #         # Так получается задвоение расходов
    #         asset_row = self._get_related_asset_account(row)
    #         if asset_row:
    #             return asset_row['account_guid']
    #         else:
    #             return None
    #
    #     return None

    # def _get_related_asset_account(self, row):
    #     """
    #     Возвращает row связанного счета активов для income или expense
    #     :param row: Строка из df_splits, с типом INCOME или EXPENSE
    #     :return: Строка (одна) из df_splits со связанным счетом активов
    #     """
    #     df_r_splits = self._get_related_splits(row)
    #     df_r_splits = df_r_splits[df_r_splits['account_type'].isin(self.ALL_XIRR_TYPES)]
    #     if df_r_splits.empty:
    #         return None
    #     elif len(df_r_splits) == 1:
    #         return df_r_splits.iloc[0]
    #
    #     # Приоритет счетов: stock, mutual, bank, asset
    #     # Первые буквы типов счетов идут в обратном порядке приоритета.
    #     # Поэтому сортируем в по типу счета и берем последнюю строку
    #     df_r_splits.sort_values('account_type', inplace=True)
    #     return df_r_splits.iloc[-1]

    # def _get_related_splits(self, row):
    #     """
    #     Возвращает splits связанные с заданной строкой из df_splits
    #     :param row: строка dataframe
    #     :return: dataframe со связаными splits
    #     """
    #     # tr_guid = row['transaction_guid']
    #     # exclude_guid = row['guid']
    #     df_r_splits = self.df_splits[self.df_splits['transaction_guid'] == row['transaction_guid']]
    #     # df_r_splits.rename(columns={'name': 'name2'}, inplace=True)
    #     df_r_splits.drop(row.name, inplace=True)
    #     return df_r_splits

    def _get_balances_for_xirr(self, account_guids, from_date=None, to_date=None):

        # Конечный баланс
        end_date = to_date
        if not end_date:
            end_date = self.max_date
        df_itog_balances = self.balance_on_date(end_date, account_guids=account_guids)

        # Добавление начального баланса
        if from_date:
            start_balances = self.balance_on_date(from_date, account_guids=account_guids)
            # Начальный баланс - это потрачено
            start_balances['value_currency'] = start_balances['value_currency'] * (-1)

            df_itog_balances = pandas.concat([start_balances, df_itog_balances]) # TODO Эту строку нужно проверить

        # Задать xirr_value и xirr_account
        df_itog_balances['xirr_value'] = df_itog_balances['value_currency']
        df_itog_balances['xirr_account'] = df_itog_balances['account_guid']

        return df_itog_balances


    def _filter_for_xirr(self, account_guids, from_date=None, to_date=None):
        """
        Отбирает проводки для подсчета доходности по xirr
        Возвращает dataframe с полем post_date и value_currency
        Итоговый dataframe может содержать нулевые проводки (для поиска доп доходов и комиссий)
        Для поиска доп доходов и комиссий используйте _find_income_for_xirr
        :param from_date: 
        :param to_date: 
        :param accounts: 
        :return: 
        """

        # if accounts:
            # Выбранные счета
            # if type(accounts) is str:
            #     accounts = [accounts]
        sel_df = (self.df_splits[(self.df_splits['account_guid']).isin(account_guids)]).copy()

        # Фильтрация по времени
        if from_date:
            sel_df = sel_df[(sel_df['post_date'] >= from_date)]
        if to_date:
            sel_df = sel_df[(sel_df['post_date'] <= to_date)]

        # нужно удалить не нулевые строки, которым соответствует таже сумма INCOME
        sel_df = self._xirr_drop_income(sel_df)

        #

        # Нужно добавить начальный и конечный баланс (Если не задана начальная дата, то начальный баланс не нужен)

        # Можно брать баланс на дату предшествующую нужной.
        # Можно ли взять баланс сразу для всех?

        # Конечный баланс это cum_sum (кол-во бумаг) на последнюю дату
        # Его нужно пересчитать в валюту учета

        # Начальный баланс это cum_sum на день раньше from_date
        # Его нужно пересчитать в валюту учета
        # cum_sum может отсутствовать. Если отсутсвует, то = 0, просто ничего не нужно делать

        # Для пересчета в валюту учета, нужно добавить rate на начльную и конечную даты и перемножить
        # теоретически для получения курса на дату можно вызвать функцию _group_prices_by_period
        # с одинаковой датой начала и конца и периодом день

        # Это неправильно, нужно брать все счета, а не по только те по которым были движения
        # all_acc_guids = sel_df['account_guid'].drop_duplicates().tolist()

        # Добавление начального баланса
        if from_date:
            start_balances = self.balance_on_date(from_date, account_guids=account_guids)
            sel_df = pandas.concat([sel_df, start_balances], ignore_index=True)

        # Все что участвует в транзакциях и является начальным балансом мы потратили
        # Поэтому минусуем
        sel_df['value_currency'] = sel_df['value_currency'] * (-1)

        # Добавление конечного баланса
        end_date = to_date
        if not end_date:
            end_date = self.max_date
        end_balances = self.balance_on_date(end_date, account_guids=account_guids)
        # Конечные балансы это то, что мы получим. Поэтому оставляем с плюсом
        # end_balances['value_currency'] = end_balances['value_currency'] * (-1)
        sel_df = pandas.concat([sel_df, end_balances], ignore_index=True)

        # Отбираем нужные колонки
        sel_df = pandas.DataFrame(sel_df,
                                  columns=['post_date',
                                           'transaction_guid',
                                           'account_guid',
                                           'fullname',
                                           'commodity_guid',
                                           'account_type',
                                           # 'value',
                                           'value_currency',
                                           # 'balance_currency',
                                           'name'
                                           # 'mnemonic'
                                           ])

        return sel_df

    def _xirr_drop_income(self, dataframe):
        """
        Удаляет лишние записи по учету прибылей/убытков по счету
        Логика работы:
        Удаляются не нулевые строки у которых есть не нулевой income
        :param dataframe: 
        :return: dataframe с убранными лишними записями
        """
        # нужно удалить не нулевые строки, которым соответствует таже сумма INCOME
        # удалить не нулевые строки у которых есть не нулевой income? Задача попроще, но правильно ли?

        # df = dataframe.copy()
        df = dataframe[dataframe['value_currency'] != 0]

        df_income = self._find_income_for_xirr(df, self.INCOME)

        all_tr_guids = df_income['transaction_guid'].drop_duplicates().tolist()

        dataframe = dataframe[~dataframe['transaction_guid'].isin(all_tr_guids)]

        # dataframe_to_excel(dataframe, 'dataframe')

        return dataframe

    def _find_income_for_xirr(self, dataframe, account_type):
        """
        Находит все связанные проводки для dataframe, по типу счетов (INCOME или EXPENSE)
        :param dataframe: filtered df_splits
        :param account_type: INCOME or EXPENSE
        :return: dataframe with transactions by accounts with account_type (INCOME or EXPENSE)
        """
        # find all income transaq for dataframe



        df = dataframe
        # if account_type == self.INCOME:
        #     df = dataframe[dataframe['value_currency'] == 0] # Возможно нужно брать все и вычитать?
        # else:
        #     df = dataframe[dataframe['value_currency'] != 0]
        all_tr_guids = df['transaction_guid'].drop_duplicates().tolist()
        sel_df = (self.df_splits[((self.df_splits['account_type']).isin([account_type])) &
                                ((self.df_splits['transaction_guid']).isin(all_tr_guids))]).copy()
        # sel_df = sel_df[(sel_df['transaction_guid']).isin(all_tr_guids)]

        # Если не доход, то мы потратили деньги
        if account_type != self.INCOME:
            sel_df['value_currency'] = sel_df['value_currency'] * -1

        # Отбираем нужные колонки
        sel_df = pandas.DataFrame(sel_df,
                                  columns=['post_date',
                                           'transaction_guid',
                                           'account_guid',
                                           'fullname',
                                           'commodity_guid',
                                           'account_type',
                                           # 'value',
                                           'value_currency',
                                           # 'balance_currency',
                                           'name'
                                           # 'mnemonic'
                                           ])

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
                                  columns=['account_guid', 'post_date', 'fullname', 'commodity_guid', 'account_type',
                                           'cum_sum', 'name', 'hidden', 'mnemonic'])
        # Фильтр по типам счетов
        if account_types:
            if type(account_types) is str:
                account_types = [account_types]
            sel_df = sel_df[(sel_df['account_type']).isin(account_types)]

        # Фильтр по именам счетов или guid счетов
        if accounts:
            if is_guid:
                sel_df = sel_df[(sel_df['account_guid']).isin(accounts)]
            else:
                sel_df = sel_df[(sel_df['fullname']).isin(accounts)]

        # Список всех account_guid
        account_guids = sel_df['account_guid'].drop_duplicates().tolist()

        # Добавление колонки нарастающий итог по счетам
        # Будет ли нарастающий итог по порядку возрастания дат???? Нет! Нужно сначала отсортировать
        # sel_df.sort_values(by='post_date', inplace=True)
        # sel_df['value'] = sel_df.groupby('fullname')['quantity'].transform(pandas.Series.cumsum)
        sel_df.rename(columns={'cum_sum': 'value'}, inplace=True)

        # здесь подразумевается, что есть только одна цена за день
        # Поэтому отсекаем повторы
        sel_df.set_index(['account_guid', 'post_date'], inplace=True)
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
                    has_balances = not (df_acc['value'].apply(lambda x: x == 0).all())
                else:
                    has_balances = True
                # Берем только не пустые счета
                if has_balances:
                    acc_info = self.df_accounts.loc[account_guid]
                    df_acc.index.name = 'post_date'
                    df_acc['account_guid'] = account_guid
                    df_acc['fullname'] = acc_info['fullname']
                    df_acc['commodity_guid'] = acc_info['commodity_guid']
                    df_acc['account_type'] = acc_info['account_type']
                    df_acc['name'] = acc_info['name']
                    df_acc['hidden'] = acc_info['hidden']
                    df_acc['mnemonic'] = acc_info['mnemonic']

                    df_acc.set_index('account_guid', append=True, inplace=True)
                    # Меняем местами индексы
                    df_acc = df_acc.swaplevel()

                    group_acc = group_acc.append(df_acc)

        # Сбрасываем один уровень индекса (post_date)
        group_acc = group_acc.reset_index()

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
                                  columns=['post_date',
                                           'transaction_guid',
                                           ACCOUNT_GUID,
                                           'fullname',
                                           'commodity_guid',
                                           'account_type',
                                           'value',
                                           'cum_sum',
                                           'name',
                                           'mnemonic',
                                           'currency_guid'])
        if accounts:
            # Выбранные счета
            if type(accounts) is str:
                accounts = [accounts]
            sel_df = sel_df[(sel_df['fullname']).isin(accounts)]
        else:
            # отбираем все счета с активами
            sel_df = sel_df[(sel_df['account_type']).isin(self.ALL_ASSET_TYPES)]

        # Фильтрация по времени
        # min_date, max_date = self._get_daterange()
        if from_date:
            sel_df = sel_df[(sel_df['post_date'] >= from_date)]

        if to_date:
            sel_df = sel_df[(sel_df['post_date'] <= to_date)]



        # пересчет в нужную валюту
        group = self._currency_calc(sel_df, from_date=from_date, to_date=to_date, period='D', guid_name='currency_guid')

        return group

    def balance_by_period(self, from_date, to_date, period='M', account_types=ALL_ASSET_TYPES, glevel=1,
                          margins:Margins = None, drop_null=False):
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

    def turnover_by_period(self, from_date: date, to_date: date, period='M', account_type=EXPENSE, glevel=1,
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
        if account_type == self.INCOME:
            sel_df['value'] = sel_df['value'].apply(lambda x: -1 * x)

        # пересчет в нужную валюту
        group = self._currency_calc(sel_df)

        # Группировка по счетам
        group = self._group_by_accounts(group, glevel=glevel, drop_null=drop_null)

        # Добавление итогов
        group = self._add_margins(group, margins)

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

        income_and_expense = [GNUCashData.INCOME, GNUCashData.EXPENSE]

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
        group = dataframe.groupby('post_date').value_currency.sum() #.map(lambda x: x * -1)

        if inverse:
            group = group.map(lambda x: x * -1)

        # Переворот дат из строк в колонки
        df = pandas.DataFrame(group).T

        df.index = [total_name]

        # Нужно добавить колонки если Multiindex
        if type(glevel) is int:
            glevel = [glevel]
        # idx_len = len(dataframe.index)
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
        sel_df = self.df_splits[(self.df_splits['post_date'] >= from_date)
                                & (self.df_splits['post_date'] <= to_date)]

        # Отбираем нужные типы счетов
        sel_df = sel_df[(sel_df['account_type']).isin(account_type)]

        # Группировка по месяцу
        sel_df.set_index('post_date', inplace=True)
        sel_df = sel_df.groupby([pandas.TimeGrouper(period), 'fullname', 'commodity_guid']).value.sum().reset_index()

        return sel_df

    def _currency_calc(self, dataframe, guid_name='commodity_guid'):
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
        guid1='commodity_guid'

        guid2='currency_guid'


        df = dataframe.copy()
        # Получаем список всех нужных mnemonic
        # commodity_guids = df[guid_name].drop_duplicates().tolist()
        # Получаем их сгруппированные цены
        # group_prices = self._group_prices_by_period(from_date, to_date, period, guids=commodity_guids)
        group_prices = self.df_prices_days
        # group_prices = group_prices.reset_index()

        # Добавление колонки курс
        if group_prices.empty:
            df['rate'] = 1
        else:
            df = df.merge(group_prices, left_on=[guid_name, 'post_date'], right_index=True,
                          how='left')
        # Заполнить пустые поля еденицей
        df['rate'] = df['rate'].fillna(Decimal(1))

        # Пересчет в валюту представления
        df['value_currency'] = (df['value'] * df['rate']).apply(lambda x: round(x, 2))
        # Теперь в колонке value_currency реальная сумма в рублях

        # Конец пересчета в нужную валюту
        return df

    def _splits_currency_calc(self):
        """
        Подсчитывает сумму сплита транзакции в валюте учета.
        Добавляется колонка 
        value_currency - сумма сплита транзакции в валюте учета
        [cancelled]balance_currency - остаток по счету после транзакции в валюте учета
        rate_currency - курс валюты для колонки value
        [cancelled]rate_commodity - курс валюты для остатка по счету
        :return: DataFrame с добавленными колонками
        """

        # dataframe = self.df_splits
        # df = dataframe.copy()
        # Получаем список всех нужных mnemonic
        # commodity_guids = df['commodity_guid'].drop_duplicates().tolist()
        # currency_guids = df['currency_guid'].drop_duplicates().tolist()
        # Получаем их сгруппированные цены
        # group_prices = self._group_prices_by_period(from_date, to_date, period, guids=commodity_guids)
        # group_prices = group_prices.reset_index()
        group_prices = self.df_prices_days

        # Добавление колонки курс
        if group_prices.empty:
            # self.df_splits['rate_commodity'] = 1
            self.df_splits['rate_currency'] = 1
        else:
            # self.df_splits = self.df_splits.merge(group_prices, left_on=['commodity_guid', 'post_date'], right_index=True,
            #               how='left')
            # self.df_splits.rename(columns={'rate': 'rate_commodity'}, inplace=True)
            self.df_splits = self.df_splits.merge(group_prices, left_on=['currency_guid', 'post_date'], right_index=True,
                          how='left')
            self.df_splits.rename(columns={'rate': 'rate_currency'}, inplace=True)
        # Заполнить пустые поля еденицей
        self.df_splits['rate_currency'] = self.df_splits['rate_currency'].fillna(Decimal(1))
        # self.df_splits['rate_commodity'] = self.df_splits['rate_commodity'].fillna(Decimal(1))

        # Пересчет в валюту представления
        self.df_splits['value_currency'] = (self.df_splits['value'] * self.df_splits['rate_currency']).apply(lambda x: round(x, 2))
        # self.df_splits['balance_currency'] = (self.df_splits['cum_sum'] * self.df_splits['rate_commodity']).apply(lambda x: round(x, 2))
        # Теперь в колонке value_currency реальная сумма в рублях
        # self.df_splits_cur = df
        # Конец пересчета в нужную валюту
        # return df

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
                                  columns=['post_date', 'fullname', 'value_currency']).copy()

        # Добавление MultiIndex по дате и названиям счетов
        s = sel_df['fullname'].str.split(':', expand=True)
        cols = s.columns
        cols = cols.tolist()
        cols = ['post_date'] + cols
        sel_df = pandas.concat([sel_df, s], axis=1)

        sel_df.sort_values(by=cols, inplace=True)  # Сортировка по дате и счетам

        if drop_null:
            sel_df.dropna(subset=['value_currency'], inplace=True)  # Удаление пустых значений
            # sel_df = sel_df[sel_df['value'] != 0]  # Удаление нулевых значений

        sel_df.drop('fullname', axis=1, inplace=True)  # Удаление колонки fullname
        # Пустые колонки не группируются, добавляю тире в пустые названия счетов.
        # for col in cols[1:]:
        #     sel_df[col] = sel_df[col].apply(lambda x: x if x else '-')

        sel_df.set_index(cols, inplace=True)

        # Здесь получается очень интересная таблица, но она не так интересна как в балансах
        # self.dataframe_to_excel(sel_df, 'turnover_split')

        # Переворот дат из строк в колонки
        unst = sel_df.unstack(level='post_date', fill_value=0)

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
                                     account_type=self.EXPENSE, glevel=glevel, margins=margins)

        # Empty Dataframe with same columns and index
        df_inf = pandas.DataFrame(index=df.index, columns=df.columns[1:])

        cols = df.columns

        for i in range(1, len(cols)):

            if not cumulative:
                # Процент к предыдущему
                # df_inf[cols[i]] = ((df[cols[i]]).astype('float64') - (df[cols[i-1]]).astype('float64')).
                # divide((df[cols[i-1]]).astype('float64'))
                df_inf[cols[i]] = self._percent_increase(df[cols[i-1]], df[cols[i]])
            else:
                # Процент к началу
                # df_inf[cols[i]] = (((df[cols[i]]).astype('float64')).divide(
                #                     (df[cols[0]]).astype('float64'))).pow(1 / i) - 1
                df_inf[cols[i]] = self._percent_increase(df[cols[0]], df[cols[i]], i)

        # Average by period
        if not cumulative:
            i2 = len(cols) - 1
            # df_inf[_('Total')] = (((df[cols[i2]]).astype('float64')).divide(
            #     (df[cols[0]]).astype('float64'))).pow(1 / i2) - 1
            df_inf[_('Total')] = self._percent_increase(df[cols[0]], df[cols[i2]], i2)

        return df_inf

    @staticmethod
    def _percent_increase(a_ser:pandas.Series, b_ser:pandas.Series, distance=1):
        """
        Return percent increase between two series
        :param a_ser: First series
        :param b_ser: Last series
        :param distance: time counts between series
        :return: series: percent increase
        """
        # if distance == 1:
        #     i_ser = ((b_ser.astype('float64')) - (a_ser.astype('float64'))).divide(a_ser.astype('float64'))
        # else:
        i_ser = ((b_ser.astype('float64')).divide(
            a_ser.astype('float64'))).pow(1 / distance) - 1
        return i_ser

    def get_empty_dataframe(self, dataframe):
        """
        Возвращает такой же но пустой dataframe
        :param dataframe:
        :return:
        """
        df_new = pandas.DataFrame(data=None, index=dataframe.index, columns=dataframe.columns)
        df_new = df_new.dropna()
        return df_new

    def _group_prices_by_period(self, from_date, to_date, period='M', guids=None):
        """
        Получение курса/цен активов за период
        Возвращает таблицу с ценой каждого актива на конец периода (по последней ближайшей к дате)
        Возвращаемый DataFrame содержит индекс и столбцы
        ['commodity_guid', 'date'] (['mnemonic', 'currency_guid', 'rate'], dtype='object')
        rate - курс
        :param from_date:
        :param to_date:
        :param period:
        :param guids: Список commodities_guids или None для всех
        :return: DataFrame with grouped prices
        """

        all_commodities_guids = set(self.df_prices.index.get_level_values('commodity_guid').drop_duplicates().tolist())

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
                                  columns=['mnemonic', 'currency_guid', 'value'])
                                  # columns=['commodity_guid', 'date', 'mnemonic', 'currency_guid', 'value'])

        # цикл по всем commodity_guid
        group_prices = pandas.DataFrame()
        for commodity_guid in guids_list:

            # DataFrame с датами и значениями
            sel_mnem = sel_df.loc[commodity_guid]
            if not sel_mnem.empty:
                sel_mnem = sel_mnem.resample(period).ffill()
                # sel_mnem = sel_mnem.resample(period).bfill()

                sel_mnem = sel_mnem.reindex(idx, method='nearest')
                sel_mnem.index.name = 'date'
                sel_mnem['commodity_guid'] = commodity_guid
                sel_mnem.set_index('commodity_guid', append=True, inplace=True)
                # Меняем местами индексы
                sel_mnem = sel_mnem.swaplevel()

                group_prices = group_prices.append(sel_mnem)

        # Список guid всех нужных валют
        if group_prices.empty:
            currency_guids=None
        else:
            currency_guids = set(group_prices['currency_guid'].drop_duplicates().tolist()) & all_commodities_guids

        if currency_guids:
            # TODO: Здесь нужен пересчет в валюту представления
            pass

        # Теперь в колонке rate курс ценной бумаги в рублях
        group_prices.rename(columns={'value': 'rate', 'currency_guid': 'price_currency_guid'}, inplace=True)
        return group_prices

    def get_balance(self, account, is_guid=False, on_date=None):
        """
        Возвращает баланс счета на заданную дату
        :param account: Полное имя счета или guid счета в зависимотси от is_guid
        :param is_guid: False - account is fullname, True - account is guid
        :param on_date: Дата на которую считается баланс или None для окончательного баланса
        :return: Баланс в еденицах счета
        """
        if is_guid:
            sel_df = self.df_splits[(self.df_splits[ACCOUNT_GUID] == account)]
        else:
            sel_df = self.df_splits[(self.df_splits[FULLNAME] == account)]
        if not on_date is None:
            sel_df = sel_df[sel_df[POST_DATE] <= on_date]
        balance = sel_df['quantity'].sum()
        return balance

    def _get_fullname_account(self, account_guid):
        """
        Get fullname account by guid. Return semicolon path Expenses:Food:...
        :param account_guid:
        :return:
        """
        if account_guid == self.root_account_guid:
            return 'root'
        fullname = self.df_accounts.ix[account_guid]['name']
        parent_guid = self.df_accounts.ix[account_guid]['parent_guid']
        if parent_guid in self.df_accounts.index:
            if parent_guid == self.root_account_guid:
                return fullname
            else:
                return self._get_fullname_account(parent_guid) + ':' + fullname
        else:
            return 'error'

    @staticmethod
    def _object_to_dataframe(pieobject, fields):
        """
        Преобразовывае объект piecash в DataFrame с заданными полями
        :param pieobject:
        :param fields:
        :return:
        """
        # build dataframe
        fields_getter = [attrgetter(fld) for fld in fields]
        df_obj = pandas.DataFrame([[fg(sp) for fg in fields_getter] for sp in pieobject], columns=fields)
        df_obj.set_index(fields[0], inplace=True)
        return df_obj

    def __to_excel(self, filename):
        """
        Запись таблиц DataFrame в фалй Excel. Для отладки
        :param filename:
        :return:
        """

        writer = pandas.ExcelWriter(filename)
        self.df_accounts.to_excel(writer, "accounts")
        self.df_transactions.to_excel(writer, "transactions")
        self.df_commodities.to_excel(writer, "commodities")
        self.df_splits.to_excel(writer, "splits")
        self.df_prices.to_excel(writer, "prices")

        writer.save()

    @staticmethod
    def _read_dataframe_from_excel(filename, sheet='Sheet1'):
        """
        Чтение dataframe из Excel
        :param filename:
        :param sheet:
        :return: DataFrame
        """
        xls = pandas.ExcelFile(filename)
        df = xls.parse(sheet)
        xls.close()
        return df

    def _read_from_excel(self, filename):
        """
        Чтение данных из Excel, вместо чтения из файла gnucash. Работает дольше sqlite
        :param filename:
        :return:
        """

        self.book_name = os.path.basename(filename)
        xls = pandas.ExcelFile(filename)

        self.df_accounts = xls.parse('accounts')
        self.df_transactions = xls.parse('transactions')
        self.df_commodities = xls.parse('commodities')
        self.df_splits = xls.parse('splits')
        self.df_prices = xls.parse('prices')

        xls.close()
