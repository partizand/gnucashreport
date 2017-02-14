import os

import piecash
import pandas
import numpy
from operator import attrgetter
from datetime import date, datetime

from decimal import Decimal

from gcreports.gcxmlreader import GNUCashXMLBook
from gcreports.margins import Margins, TOTAL_NAME, MEAN_NAME, PROFIT_NAME, EQUITY_NAME

class GNUCashData:
    """
    DataFrame implementation of GnuCash database tables for build reports

    Exaple use:

    from_date = datetime.date(2016, 1, 1)
    to_date = datetime.date(2016, 12, 31)
    rep = repbuilder.RepBuilder()
    rep.open_book("u:/sqllite_book/real-2017-01-26.gnucash")
    df = rep.turnover_by_period(from_date=from_date, to_date=to_date, account_type='INCOME')
    rep.dataframe_to_excel(df, "itog-income2")
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

    # Название итоговых строк
    # TOTAL_NAME = 'Всего'
    # MEAN_NAME = 'Среднее'

    # Данные для генерации тестовых данных и тестирования
    dir_pickle = 'V:/pickle'
    dir_testdata = 'v:/test_data'

    pickle_prices = 'prices.pkl'
    pickle_splits = 'splits.pkl'
    pickle_accounts = 'accounts.pkl'
    pickle_tr = 'transactions.pkl'
    pickle_commodities = 'commodities.pkl'

    pickle_assets = 'assets.pkl'
    pickle_loans = 'loans.pkl'
    pickle_expense = 'expense.pkl'
    pickle_income = 'income.pkl'
    pickle_profit = 'profit.pkl'
    pickle_equity = 'equity.pkl'

    test_glevel = 1

    test_from_date = date(2016, 1, 1)
    test_to_date = date(2016, 12, 31)
    # Конец тестовых данных

    dir_excel = "v:/tables"

    bookfile_sql = 'v:/gnucash-base/sqlite/GnuCash-base.gnucash'
    bookfile_xml = 'v:/gnucash-base/xml/GnuCash-base.gnucash'

    # bookfile_sql = "u:/sqllite_book/real-2017-01-26.gnucash"
    # bookfile_xml = 'U:/xml_book/GnuCash-base.gnucash'

    # book_name = None

    # root_account_guid = None

    def __init__(self):
        self.df_accounts = pandas.DataFrame()
        self.df_transactions = pandas.DataFrame()
        self.df_commodities = pandas.DataFrame()
        self.df_splits = pandas.DataFrame()
        self.df_prices = pandas.DataFrame()

        self.book_name = None
        self.root_account_guid = None

    def open_book_xml(self, xml_file=None):
        """
        Opens gnucash book from xml file
        :param xml_file:
        :return:
        """
        if not xml_file:
            xml_file = self.bookfile_xml
        self._read_book_xml(xml_file)
        self._after_read()
        # print(self.df_prices)

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
        Opens gnucash book from sql
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
        if not sqlite_file:
            sqlite_file = self.bookfile_sql
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


    def save_testdata(self):
        """
        Запись тестовых pickle для последующей проверки в тестах
        :return:
        """
        from_date = self.test_from_date # date(2016, 1, 1)
        to_date = self.test_to_date  #    date(2016, 12, 31)

        self.save_pickle(folder=self.dir_testdata)

        # filename = self.pickle_assets
        df = self.balance_by_period(from_date=from_date, to_date=to_date, glevel=self.test_glevel)
        self.dataframe_to_pickle(df, filename=self.pickle_assets, folder=self.dir_testdata)

        # filename = 'loans.pkl'
        df = self.balance_by_period(from_date=from_date, to_date=to_date, account_types=[GNUCashData.LIABILITY], glevel=0)
        self.dataframe_to_pickle(df, filename=self.pickle_loans, folder=self.dir_testdata)

        # filename = 'expense.pkl'
        df = self.turnover_by_period(from_date=from_date, to_date=to_date, account_type=GNUCashData.EXPENSE, glevel=self.test_glevel)
        self.dataframe_to_pickle(df, filename=self.pickle_expense, folder=self.dir_testdata)

        # filename = 'income.pkl'
        df = self.turnover_by_period(from_date=from_date, to_date=to_date, account_type=GNUCashData.INCOME,
                                     glevel=self.test_glevel)
        self.dataframe_to_pickle(df, filename=self.pickle_income, folder=self.dir_testdata)

        # filename = 'profit.pkl'
        df = self.profit_by_period(from_date=from_date, to_date=to_date, glevel=0)
        self.dataframe_to_pickle(df, filename=self.pickle_profit, folder=self.dir_testdata)

        # filename = 'equity.pkl'
        df = self.equity_by_period(from_date=from_date, to_date=to_date, glevel=0)
        self.dataframe_to_pickle(df, filename=self.pickle_equity, folder=self.dir_testdata)

    def save_pickle(self, year=None, folder=None):
        """
        For test purpose
        Запись данных базы в pickle файлы каталога. Если указан год, записывается дополнительно этот год
        :param year: дополнительный год для записи
        :param folder: Каталог с файлами базы
        :return:
        """

        self.dataframe_to_pickle(self.df_accounts, self.pickle_accounts, folder=folder)
        self.dataframe_to_pickle(self.df_commodities, self.pickle_commodities, folder=folder)
        self.dataframe_to_pickle(self.df_prices, self.pickle_prices, folder=folder)
        self.dataframe_to_pickle(self.df_transactions, self.pickle_tr, folder=folder)
        self.dataframe_to_pickle(self.df_splits, self.pickle_splits, folder=folder)
        if year:
            df_splits = self.df_splits.copy()
            filename_splits = self.pickle_splits
            from_date = date(year,1,1)
            to_date = date(year, 12, 31)
            df_splits = df_splits[(df_splits['post_date'] >= from_date) & (self.df_splits['post_date'] <= to_date)]
            basename, ext = os.path.splitext(self.pickle_splits)
            filename_splits = basename+str(year)+ext
            self.dataframe_to_pickle(df_splits, filename_splits, folder=folder)

    def open_pickle(self, year=None, folder=None):
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
        self.df_accounts=self.dataframe_from_pickle(self.pickle_accounts, folder=folder)
        self.df_commodities=self.dataframe_from_pickle(self.pickle_commodities, folder=folder)
        self.df_prices=self.dataframe_from_pickle(self.pickle_prices, folder=folder)
        self.df_transactions=self.dataframe_from_pickle(self.pickle_tr, folder=folder)

        filename_splits = self.pickle_splits
        if year:
            basename, ext = os.path.splitext(self.pickle_splits)
            filename_splits = basename + str(year) + ext
        self.df_splits = self.dataframe_from_pickle(filename_splits, folder=folder)

    def dataframe_from_pickle(self, filename, folder=None):
        """
        Читает dataframe из pickle файла
        :param filename: Полное или короткое имя файла
        :param folder: Каталог с файлом
        :return: DataFrame
        """
        if not folder:
            folder = self.dir_pickle
        fullfilename = os.path.join(folder, filename)
        df = pandas.read_pickle(fullfilename)
        return df

    def dataframe_to_pickle(self, dataframe, filename, folder=None):
        """
        Записаывает DataFrame в pickle файл
        :param dataframe:
        :param filename:
        :param folder:
        :return:
        """
        if not folder:
            folder = self.dir_pickle
        fullfilename = os.path.join(folder, filename)
        dataframe.to_pickle(fullfilename)

    def _read_book_xml(self, xml_file):

        # read contens of the book
        book = GNUCashXMLBook()
        book.read_from_xml(xml_file)

        # print(book['prices'])
        # return

        # Accounts

        fields = ["guid", "name", "actype",
                  "commodity_guid", "commodity_scu",
                  "parent_guid", "description", "hidden"]

        self.df_accounts = self.object_to_dataframe(book.accounts, fields)
        self.df_accounts.rename(columns={'actype': 'account_type'}, inplace=True)
        self.root_account_guid = book.root_account_guid
        # self.dataframe_to_excel(self.df_accounts, 'acc-xml')
        # print(df_accounts)
        # return

        # Transactions

        fields = ["guid", "currency_guid", "date", "description"]

        self.df_transactions = self.object_to_dataframe(book.transactions, fields)
        self.df_transactions.rename(columns={'date': 'post_date'}, inplace=True)
        # print(self.df_transactions)
        # return

        # Splits
        fields = ["guid", "transaction_guid", "account_guid",
                  "memo", "reconcile_state", "value", "quantity"]

        self.df_splits = self.object_to_dataframe(book.splits, fields)
        # print(self.df_splits)
        # return

        # commodity

        fields = ["guid", "space", "mnemonic"]
        self.df_commodities = self.object_to_dataframe(book.commodities, fields)
        self.df_commodities.rename(columns={'space': 'namespace'}, inplace=True)
        self.df_commodities = self.df_commodities[self.df_commodities['namespace'] != 'template']
        # print(self.df_commodities)

        # Prices
        fields = ["guid", "commodity_guid", "currency_guid",
                  "date", "source", "price_type", "value"]
        self.df_prices = self.object_to_dataframe(book.prices, fields)
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
            self.df_commodities = self.object_to_dataframe(t_commodities, fields)

            # Accounts

            self.root_account_guid = gnucash_book.root_account.guid
            t_accounts = gnucash_book.session.query(piecash.Account).all()
            fields = ["guid", "name", "type", "placeholder",
                      "commodity_guid", "commodity_scu",
                      "parent_guid", "description", "hidden"]
            self.df_accounts = self.object_to_dataframe(t_accounts, fields)
            # rename to real base name of field from piecash name
            self.df_accounts.rename(columns={'type': 'account_type'}, inplace=True)
            # self.dataframe_to_excel(self.df_accounts, 'acc-sql')

            # Transactions

            t_transactions = gnucash_book.session.query(piecash.Transaction).all()
            fields = ["guid", "currency_guid", "num",
                      "post_date", "description"]
            self.df_transactions = self.object_to_dataframe(t_transactions, fields)

            # Splits

            t_splits = gnucash_book.session.query(piecash.Split).all()
            fields = ["guid", "transaction_guid", "account_guid",
                      "memo", "action", "reconcile_state",
                      "value",
                      "quantity", "lot_guid"]
            self.df_splits = self.object_to_dataframe(t_splits, fields)

            # Prices

            # Get from piecash
            t_prices = gnucash_book.session.query(piecash.Price).all()
            # Some fields not correspond to real names in DB
            fields = ["guid", "commodity_guid", "currency_guid",
                      "date", "source", "type", "value"]
            self.df_prices = self.object_to_dataframe(t_prices, fields)

            #---------------------------------------------------
            # After load



    def _after_read(self):
        """
        Some manipulation with dataframes after load data
        :return:
        """

        # Get root account guid
        # self.df_accounts[self.df_accounts['acc']]

        #  Get fullname of accounts
        self.df_accounts['fullname'] = self.df_accounts.index.map(self._get_fullname_account)

        # Add commodity mnemonic to accounts
        mems = self.df_commodities['mnemonic'].to_frame()
        self.df_accounts = pandas.merge(self.df_accounts, mems, left_on='commodity_guid', right_index=True)

        # Convert datetme to date in transactions (skip time)
        self.df_transactions['post_date'] = self.df_transactions['post_date'].apply(
            lambda x: pandas.to_datetime(x.date()))

        # Merge prices with commodities
        # self.df_prices = pandas.merge(self.df_prices, mems, left_on='commodity_guid', right_index=True)
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

    def add_margins(self, dataframe, margins=None):
        """
        Добавляет итоги в DataFrame
        :param dataframe:
        :margins dataframe:
        :return: DataFrame с итогами
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

        total_name = TOTAL_NAME
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

    def equity_by_period(self, from_date, to_date, period='M', glevel=1,
                           margins: Margins = None):

        """
        Получение капитала за период
        Возвращает DataFrame

        :param from_date: Start date
        :param to_date: Finish date
        :param period: "M" for month, "D" for day...
        :param glevel: group level
        :return: pivot DataFrame
        """
        assets_and_liability = GNUCashData.ALL_ASSET_TYPES
        assets_and_liability.append(GNUCashData.LIABILITY)

        # Группировка по периоду
        group_acc = self._balance_group_by_period(from_date=from_date, to_date=to_date, period=period,
                                                  account_types=assets_and_liability, drop_null=False)

        # пересчет в нужную валюту
        group_acc = self._currency_calc(group_acc, from_date=from_date, to_date=to_date, period=period)

        # Суммируем
        equity_name = EQUITY_NAME
        if margins:
            equity_name = margins.equity_name
        df = self._sum_all(group_acc, total_name=equity_name, glevel=glevel, inverse=False)

        # group = group_acc.groupby('post_date').value_currency.sum()
        #
        # # Переворот дат из строк в колонки
        # df = pandas.DataFrame(group).T
        # equity_name = EQUITY_NAME
        # if margins:
        #     equity_name = margins.equity_name
        # df.index = [equity_name]
        #
        # # Нужно добавить колонки если Multiindex
        # if type(glevel) is int:
        #     glevel = [glevel]
        # idx_len = len(glevel)
        # new_indexes = [str(i) for i in range(1, idx_len)]
        # if new_indexes:
        #     # Нужно добавить уровни
        #     for col_name in new_indexes:
        #         df[col_name] = ''
        #     df.set_index(new_indexes, append=True, inplace=True)

        # Добавление итогов
        df = self.add_margins(df, margins)


        return df

    def _balance_group_by_period(self, from_date, to_date, period, account_types, drop_null):
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
                                           'quantity', 'name', 'hidden', 'mnemonic'])
        # Отбираем нужные типы счетов
        if type(account_types) is str:
            account_types = [account_types]
        sel_df = sel_df[(sel_df['account_type']).isin(account_types)]

        # Список всех account_guid
        account_guids = sel_df['account_guid'].drop_duplicates().tolist()

        # Добавление колонки нарастающий итог по счетам
        # Будет ли нарастающий итог по порядку возрастания дат???? Нет! Нужно сначала отсортировать
        sel_df.sort_values(by='post_date', inplace=True)
        sel_df['value'] = sel_df.groupby('fullname')['quantity'].transform(pandas.Series.cumsum)

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


    def balance_by_period(self, from_date, to_date, period='M', account_types=ALL_ASSET_TYPES, glevel=1,
                          margins:Margins = None, drop_null=False):
        """
        Возвращает сводный баланс по счетам за интервал дат с разбивкой по периодам
        :param from_date:
        :param to_date:
        :param period:
        :param account_types:
        :param glevel:
        :param drop_null: Отбрасывать нулевые значения (итоги могут не содержать всех столбцов)
        :return: DataFrame
        """

        group_acc = self._balance_group_by_period(from_date=from_date, to_date=to_date, period=period,
                                                  account_types=account_types, drop_null=drop_null)

        # Отбираем нужные колонки (почти все и нужны)
        # sel_df = pandas.DataFrame(self.df_splits,
        #                           columns=['account_guid', 'post_date', 'fullname', 'commodity_guid', 'account_type',
        #                                    'quantity', 'name', 'hidden', 'mnemonic'])
        # # Отбираем нужные типы счетов
        # if type(account_types) is str:
        #     account_types = [account_types]
        # sel_df = sel_df[(sel_df['account_type']).isin(account_types)]
        #
        # # Список всех account_guid
        # account_guids = sel_df['account_guid'].drop_duplicates().tolist()
        #
        # # Добавление колонки нарастающий итог по счетам
        # # Будет ли нарастающий итог по порядку возрастания дат???? Нет! Нужно сначала отсортировать
        # sel_df.sort_values(by='post_date', inplace=True)
        # sel_df['value'] = sel_df.groupby('fullname')['quantity'].transform(pandas.Series.cumsum)
        #
        # # здесь подразумевается, что есть только одна цена за день
        # # Поэтому отсекаем повторы
        # sel_df.set_index(['account_guid', 'post_date'], inplace=True)
        # # отсечение повторов по индексу
        # sel_df = sel_df[~sel_df.index.duplicated(keep='last')]
        #
        # # Индекс по периоду
        # idx = pandas.date_range(from_date, to_date, freq=period)
        #
        # # цикл по всем commodity_guid
        # group_acc = pandas.DataFrame()
        # for account_guid in account_guids:
        #
        #     # DataFrame с датами и значениями
        #     df_acc = sel_df.loc[account_guid]
        #     if not df_acc.empty:
        #
        #         df_acc = df_acc.resample(period).ffill()
        #
        #         df_acc = df_acc.reindex(idx, method='ffill')
        #         # Здесь теряются все колонки если начинается с пустой
        #
        #         if drop_null:
        #             # Убрать если все значения 0
        #             has_balances = not (df_acc['value'].apply(lambda x: x == 0).all())
        #         else:
        #             has_balances = True
        #         # Берем только не пустые счета
        #         if has_balances:
        #             acc_info = self.df_accounts.loc[account_guid]
        #             df_acc.index.name = 'post_date'
        #             df_acc['account_guid'] = account_guid
        #             df_acc['fullname'] = acc_info['fullname']
        #             df_acc['commodity_guid'] = acc_info['commodity_guid']
        #             df_acc['account_type'] = acc_info['account_type']
        #             df_acc['name'] = acc_info['name']
        #             df_acc['hidden'] = acc_info['hidden']
        #             df_acc['mnemonic'] = acc_info['mnemonic']
        #
        #             df_acc.set_index('account_guid', append=True, inplace=True)
        #             # Меняем местами индексы
        #             df_acc = df_acc.swaplevel()
        #
        #             group_acc = group_acc.append(df_acc)
        #
        # # Сбрасываем один уровень индекса (post_date)
        # group_acc = group_acc.reset_index()

        # пересчет в нужную валюту
        # Группировка по счетам
        group = self._curcalc_and_accgroup(group_acc, from_date=from_date, to_date=to_date, period=period,
                                           glevel=glevel, margins=margins, drop_null=drop_null)

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

        # Фильтрация по времени
        # sel_df = self.df_splits[(self.df_splits['post_date'] >= from_date)
        #                         & (self.df_splits['post_date'] <= to_date)
        #                         & (self.df_splits['account_type'] == account_type)]

        # Группировка по месяцу
        # sel_df.set_index('post_date', inplace=True)
        # sel_df = sel_df.groupby([pandas.TimeGrouper(period), 'fullname', 'commodity_guid']).value.sum().reset_index()

        # inverse income
        if account_type == self.INCOME:
            sel_df['value'] = sel_df['value'].apply(lambda x: -1 * x)

        # пересчет в нужную валюту
        # Группировка по счетам
        group = self._curcalc_and_accgroup(sel_df, from_date=from_date, to_date=to_date, period=period,
                                            glevel=glevel, margins=margins, drop_null=drop_null)

        return group

    def profit_by_period(self, from_date: date, to_date: date, period='M', glevel=1,
                           margins: Margins = None):

        """
        Получение прибыли за период
        Возвращает DataFrame

        :param from_date: Start date
        :param to_date: Finish date
        :param period: "M" for month, "D" for day...
        :param account_type: INCOME or EXPENSE
        :param glevel: group level
        :return: pivot DataFrame
        """

        income_and_expense = [GNUCashData.INCOME, GNUCashData.EXPENSE]

        # Группировка по периоду
        sel_df = self._turnover_group_by_period(from_date=from_date, to_date=to_date, period=period,
                                                account_type=income_and_expense)

        # пересчет в нужную валюту
        group = self._currency_calc(sel_df, from_date=from_date, to_date=to_date, period=period)
        # Группировка по счетам



        # Суммируем
        profit_name = PROFIT_NAME
        if margins:
            profit_name = margins.profit_name
        df = self._sum_all(group, total_name=profit_name, glevel=glevel, inverse=True)

        # group = group.groupby('post_date').value_currency.sum().map(lambda x: x * -1)
        #
        # # Переворот дат из строк в колонки
        # df = pandas.DataFrame(group).T
        # profit_name = PROFIT_NAME
        # if margins:
        #     profit_name = margins.profit_name
        # df.index = [profit_name]
        #
        # # Нужно добавить колонки если Multiindex
        # if type(glevel) is int:
        #     glevel = [glevel]
        # idx_len = len(glevel)
        # new_indexes = [str(i) for i in range(1, idx_len)]
        # if new_indexes:
        #     # Нужно добавить уровни
        #     for col_name in new_indexes:
        #         df[col_name] = ''
        #     df.set_index(new_indexes, append=True, inplace=True)

        # Добавление итогов
        df = self.add_margins(df, margins)

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

    def _curcalc_and_accgroup(self, dataframe, from_date, to_date, period, glevel,
                              margins:Margins=None, drop_null=False):

        # пересчет в нужную валюту
        group = self._currency_calc(dataframe, from_date=from_date, to_date=to_date, period=period)

        # Группировка по счетам
        group = self._group_by_accounts(group, glevel=glevel, margins=margins, drop_null=drop_null)
        return group

    def _currency_calc(self, dataframe, from_date, to_date, period):
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
        # Тут нужно добавить пересчет в нужную валюту
        df = dataframe.copy()
        # Получаем список всех нужных mnemonic
        commodity_guids = df['commodity_guid'].drop_duplicates().tolist()
        # Получаем их сгруппированные цены
        group_prices = self._group_prices_by_period(from_date, to_date, period, guids=commodity_guids)
        # group_prices = group_prices.reset_index()

        # Добавление колонки курс
        if group_prices.empty:
            df['rate'] = 1
        else:
            df = df.merge(group_prices, left_on=['commodity_guid', 'post_date'], right_index=True,
                          how='left')
        # Заполнить пустые поля еденицей
        df['rate'] = df['rate'].fillna(Decimal(1))

        # Пересчет в валюту представления
        df['value_currency'] = (df['value'] * df['rate']).apply(lambda x: round(x, 2))
        # Теперь в колонке value_currency реальная сумма в рублях

        # Конец пересчета в нужную валюту
        return df

    def _group_by_accounts(self, dataframe, glevel=1,
                           margins: Margins=None, drop_null=False):
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

        # Добавление итогов
        group = self.add_margins(group, margins)

        return group

    def get_empty_dataframe(self, dataframe):
        """
        Возвращает такой же но пустой dataframe
        :param dataframe:
        :return:
        """
        df_new = pandas.DataFrame(data=None, index=dataframe.index, columns=dataframe.columns)
        df_new = df_new.dropna()
        return df_new

    def cashflow(self, from_date: date, to_date: date, period='M', glevel=[0,1]):
        df_income = self.turnover_by_period(from_date=from_date, to_date=to_date, period=period,
                                            account_type=self.INCOME, glevel=glevel)
        df_expense = self.turnover_by_period(from_date=from_date, to_date=to_date, period=period,
                                            account_type=self.EXPENSE, glevel=glevel)



        # Calculate Profit
        profit = df_income.loc['Total'] - df_expense.loc['Total']
        # empty column
        # df_income['1'] = 1
        # df_expense['1'] = 1
        profit[0] = 'Profit'
        idxcols = profit.index.names
        idxcols = [0] + idxcols
        profit.set_index(0, append=True, inplace=True)
        profit = profit.reorder_levels(idxcols)

        # empty line
        df_empty = pandas.DataFrame(index=profit.index, columns=profit.columns)

        df_empty = df_empty.drop('Profit')
        df_empty.loc[' ',' '] = ' '
        # self.dataframe_to_excel(df_empty, 'empty')
        # print(empty.index)
        # print(empty)
        # return

        # concatenate all
        df_cashflow = df_income.append(df_empty)
        df_cashflow = df_cashflow.append(df_expense)
        df_cashflow = df_cashflow.append(df_empty)
        df_cashflow = df_cashflow.append(profit)

        self.dataframe_to_excel(df_cashflow, 'cashflow')

        return df_cashflow

    def complex_report(self, filename, from_date, to_date, period='M', datetime_format='mmmm yyyy'):

        sheet = 'Sheet1'

        if not filename.endswith('.xlsx'):
            filename = os.path.join(self.dir_excel, filename + ".xlsx")

        df_income = self.turnover_by_period(from_date=from_date, to_date=to_date, period=period, account_type=self.INCOME)
        df_expense = self.turnover_by_period(from_date=from_date, to_date=to_date, period=period, account_type=self.EXPENSE)

        df_income.to_pickle('u:/tables/inc-2016.pkl')

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer = pandas.ExcelWriter(filename, engine='xlsxwriter', datetime_format=datetime_format)



        # Convert the dataframe to an XlsxWriter Excel object.
        start_row = 2
        df_income.to_excel(writer, sheet_name=sheet, startrow=start_row)
        offset_income = len(df_income) + 3
        expense_row = start_row + offset_income
        df_expense.to_excel(writer, sheet_name=sheet, header=False, startrow=expense_row)

        # Get the xlsxwriter objects from the dataframe writer object.
        workbook = writer.book
        worksheet = writer.sheets[sheet]

        worksheet.write(0, 0, 'Доходы')
        worksheet.write(expense_row-1, 0, 'Расходы')
        worksheet.set_column(0, 0, 20)



        # Close the Pandas Excel writer and output the Excel file.
        writer.save()


    # def _dataframe_to_writer(self, writer, dataframe, ):

    def dataframe_to_excel(self, dataframe, filename, sheet='Sheet1', datetime_format='dd-mm-yyyy'):
        """
        Записывает dataFrame в excel. Указывать только имя файла без расширения!
        :param dataframe:
        :param filename: Указывать только имя файла без расширения
        :return:
        """
        if not filename.endswith('.xlsx'):
            filename = os.path.join(self.dir_excel, filename + ".xlsx")

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        # writer = pandas.ExcelWriter(filename, engine='xlsxwriter', datetime_format=datetime_format)
        writer = pandas.ExcelWriter(filename, datetime_format=datetime_format)

        # Convert the dataframe to an XlsxWriter Excel object.
        dataframe.to_excel(writer, sheet_name=sheet)

        # Get the xlsxwriter objects from the dataframe writer object.
        workbook = writer.book
        # worksheet = writer.sheets[sheet] # Так работает
        worksheet = workbook.active # Так тоже работает

        # worksheet['A1'] = 'A1'

        # Close the Pandas Excel writer and output the Excel file.
        writer.save()

        # dataframe.to_excel(filename)

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

        all_commodities_guids = set(self.df_prices['commodity_guid'].drop_duplicates().tolist())

        # Индекс по периоду
        idx = pandas.date_range(from_date, to_date, freq=period)

        # Отбор строк по заданному периоду
        # sel_df = self.df_prices[(self.df_prices['date'] <= to_date)]

        # Список commodities guids
        if guids is None:
            guids_list = all_commodities_guids
        else:
            guids_list = set(guids) & all_commodities_guids

        # здесь подразумевается, что есть только одна цена за день
        sel_df = pandas.DataFrame(self.df_prices,
                                  columns=['commodity_guid', 'date', 'mnemonic', 'currency_guid', 'value'])
        # Поэтому отсекаем повторы
        sel_df.set_index(['commodity_guid', 'date'], inplace=True)
        # отсечение повторов по индексу
        sel_df = sel_df[~sel_df.index.duplicated(keep='last')]

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

                # if group_prices.empty:
                #     group_prices = sel_mnem
                # else:
                group_prices = group_prices.append(sel_mnem)

        # Список guid всех нужных валют
        if group_prices.empty:
            currency_guids=None
        else:
            currency_guids = set(group_prices['currency_guid'].drop_duplicates().tolist()) & all_commodities_guids
        # print(currency_guids)
        if currency_guids:
            # TODO: Здесь нужен пересчет в валюту представления
            pass

        # Теперь в колонке rate курс ценной бумаги в рублях
        group_prices.rename(columns={'value': 'rate'}, inplace=True)
        return group_prices

    def get_balance(self, account_name, on_date=None):
        """
        Возвращает баланс счета на заданную дату
        :param account_name: Полное имя счета
        :param on_date: Дата на которую считается баланс или None для окончательного баланса
        :return: Баланс в еденицах счета
        """
        sel_df = self.df_splits[(self.df_splits['fullname'] == account_name)]
        if not on_date is None:
            sel_df = sel_df[sel_df['post_date'] <= on_date]
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
    def object_to_dataframe(pieobject, fields):
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
    def read_dataframe_from_excel(filename, sheet='Sheet1'):
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

    def __read_from_excel(self, filename):
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

        # def get_split(self, account_name):
        #     return self.df_splits[(self.df_splits['fullname'] == account_name)]
        #     # return self.df_splits.loc['fullname' == account_name]
