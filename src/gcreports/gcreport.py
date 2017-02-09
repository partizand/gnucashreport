import os

import piecash
import pandas
import numpy
from operator import attrgetter
from datetime import date, datetime

from decimal import Decimal

from gcreports.gcxmlreader import GNUCashXMLBook

TOTAL_NAME = 'Всего'
MEAN_NAME = 'Среднее'

class GCReport:
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
    MEAN_NAME = 'Среднее'

    df_accounts = pandas.DataFrame()
    df_transactions = pandas.DataFrame()
    df_commodities = pandas.DataFrame()
    df_splits = pandas.DataFrame()
    df_prices = pandas.DataFrame()

    dir_pickle = 'u:/pickle'
    pickle_prices = 'prices.pkl'
    pickle_splits = 'splits.pkl'
    pickle_accounts = 'accounts.pkl'
    pickle_tr = 'transactions.pkl'
    pickle_commodities = 'commodities.pkl'

    dir_excel = "U:/tables"

    book_name = None

    root_account_guid = None

    # def __init__(self):
        # self.excel_filename = os.path.join(self.dir_excel, self.excel_filename)
        # self.df_accounts = pandas.DataFrame()
        # self.df_transactions = pandas.DataFrame()
        # self.df_commodities = pandas.DataFrame()
        # self.df_splits = pandas.DataFrame()
        # self.df_prices = pandas.DataFrame()

    def open_book_xml(self, xml_file):
        """
        Opens gnucash book from xml file
        :param xml_file:
        :return:
        """
        self._read_book_xml(xml_file)
        self._after_read()
        # print(self.df_prices)

    def open_book_sql(self, sqlite_file, open_if_lock=False):
        """
        Opens gnucash book from sqlite file
        :param sqlite_file:
        :param open_if_lock:
        :return:
        """
        self._read_book_sql(sqlite_file, open_if_lock)
        self._after_read()


    def save_pickle(self, year=None, folder=None):
        """
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


    def _read_book_sql(self, sqlite_file, open_if_lock=False):
        """
        Open gnucash sqlite file, read data to DataFrames
        :param sqlite_file:
        :param open_if_lock:
        :return:
        """

        self.book_name = os.path.basename(sqlite_file)
        with piecash.open_book(sqlite_file, open_if_lock=open_if_lock) as gnucash_book:
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


    def balance_by_period(self, from_date: date, to_date: date, period='M', account_types=ALL_ASSET_TYPES, glevel=2,
                          total_row=False, total_col=False, mean_col=False, total_name=TOTAL_NAME,
                          mean_name=MEAN_NAME, empty_col=False, drop_null=False):
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

        # Отбираем нужные колонки (почти все и нужны)
        sel_df = pandas.DataFrame(self.df_splits,
                                  columns=['account_guid', 'post_date', 'fullname', 'commodity_guid', 'account_type',
                                           'quantity', 'name', 'hidden', 'mnemonic'])
        # Отбираем нужные типы счетов
        sel_df = sel_df[(sel_df['account_type']).isin(account_types)]

        # Список всех account_guid
        account_guids = sel_df['account_guid'].drop_duplicates().tolist()

        # Добавление колонки нарастающий итог по счетам
        # Будет ли нарастающий итог по порядку возрастания дат???? Нет! Нужно сначала отсортировать
        sel_df.sort_values(by='post_date', inplace=True)
        sel_df['balance'] = sel_df.groupby('fullname')['quantity'].transform(pandas.Series.cumsum)

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
                # Убрать если все значения 0
                if drop_null:
                    has_balances = not (df_acc['balance'].apply(lambda x: x == 0).all())
                else:
                    has_balances = True
                # Берем только не пустые счета
                if has_balances:
                    df_acc.index.name = 'post_date'
                    df_acc['account_guid'] = account_guid
                    df_acc.set_index('account_guid', append=True, inplace=True)
                    # Меняем местами индексы
                    df_acc = df_acc.swaplevel()

                    group_acc = group_acc.append(df_acc)

        # Тут нужно добавить пересчет в нужную валюту

        # Получаем список всех нужных commodity_guid
        commodity_guids = group_acc['commodity_guid'].drop_duplicates().tolist()
        # Получаем их сгруппированные цены
        group_prices = self.group_prices_by_period(from_date, to_date, period, guids=commodity_guids)
        # group_prices = group_prices.reset_index()

        # Сбрасываем один уровень индекса (post_date)
        group_acc = group_acc.reset_index()
        # group_acc = group_acc.reset_index(level=1)
        # Добавление колонки курс
        if group_prices.empty:
            group_acc['rate'] = 1
        else:
            group_acc = group_acc.merge(group_prices, left_on=['commodity_guid', 'post_date'], right_index=True,
                                    how='left')

        # Теперь в колонке rate курс ценной бумаги в рублях
        # group_acc.rename(columns={'value': 'rate'}, inplace=True)
        # Заполнить пустые поля еденицей
        group_acc['rate'] = group_acc['rate'].fillna(Decimal(1))

        # Пересчет в валюту представления
        group_acc['balance_currency'] = (group_acc['balance'] * group_acc['rate']).apply(lambda x: round(x, 2))
        # Теперь в колонке balance_currency реальная сумма в рублях

        # Конец пересчета в нужную валюту

        # Отбираем нужные колонки
        group_acc = pandas.DataFrame(group_acc,
                                     columns=['post_date', 'fullname',
                                              'balance_currency', 'rate', 'balance'])

        # Добавление MultiIndex по дате и названиям счетов
        s = group_acc['fullname'].str.split(':', expand=True)
        cols = s.columns
        cols = cols.tolist()
        cols = ['post_date'] + cols
        group_acc = pandas.concat([group_acc, s], axis=1)
        group_acc.sort_values(by=cols, inplace=True)  # Сортировка по дате и счетам

        if drop_null:
            group_acc.dropna(subset=['balance_currency'], inplace=True)  # Удаление пустых значений
            group_acc = group_acc[group_acc['balance'] != 0]  # Удаление нулевых значений

        group_acc.drop('fullname', axis=1, inplace=True)  # Удаление колонки fullname
        # Timestap to date
        # group_acc['post_date'] = group_acc['post_date'].apply(lambda x: x.date())
        # Convert datetme to date (skip time)
        # group_acc['post_date'] = group_acc['post_date'].apply(lambda x: pandas.to_datetime(x.date()))
        group_acc.set_index(cols, inplace=True)

        # Здесь получается очень интересная таблица
        # self.dataframe_to_excel(group_acc, 'group_acc_split')

        # Группировка по нужному уровню
        group_acc = group_acc.groupby(level=[0, glevel]).balance_currency.sum().reset_index()

        # Переворот в сводную
        pivot_t = pandas.pivot_table(group_acc, index=(glevel - 1), values='balance_currency', columns='post_date',
                                     aggfunc='sum',
                                     fill_value=0)

        return pivot_t

    def turnover_by_period(self, from_date: date, to_date: date, period='M', account_type=EXPENSE, glevel=1,
                           total_row=False, total_col=False, mean_col=False, total_name=TOTAL_NAME,
                           mean_name=MEAN_NAME, empty_col=False, drop_null=False):

        """
        Сломана из-за prices
        Получение сводных оборотов по тратам/доходам за промежуток времени с разбивкой на периоды
        Например, ежемесячные траты за год. Возвращает DataFrame

        :param from_date: Start date
        :param to_date: Finish date
        :param period: "M" for month, "D" for day...
        :param account_type: INCOME or EXPENSE
        :param glevel: group level
        :return: pivot DataFrame
        """

        # Фильтрация по времени
        sel_df = self.df_splits[(self.df_splits['post_date'] >= from_date)
                                & (self.df_splits['post_date'] <= to_date)
                                & (self.df_splits['account_type'] == account_type)]

        # Группировка по месяцу
        sel_df.set_index('post_date', inplace=True)
        sel_df = sel_df.groupby([pandas.TimeGrouper(period), 'fullname', 'commodity_guid']).value.sum().reset_index()

        # Тут нужно добавить пересчет в нужную валюту

        # Получаем список всех нужных mnemonic
        commodity_guids = sel_df['commodity_guid'].drop_duplicates().tolist()
        # Получаем их сгруппированные цены
        group_prices = self.group_prices_by_period(from_date, to_date, period, guids=commodity_guids)
        # group_prices = group_prices.reset_index()

        # Добавление колонки курс
        sel_df = sel_df.merge(group_prices, left_on=['commodity_guid', 'post_date'], right_index=True,
                              how='left')
        # Заполнить пустые поля еденицей
        sel_df['rate'] = sel_df['rate'].fillna(Decimal(1))

        # inverse income
        if account_type == self.INCOME:
            sel_df['value'] = sel_df['value'].apply(lambda x: -1 * x)
        # Пересчет в валюту представления
        sel_df['value_currency'] = (sel_df['value'] * sel_df['rate']).apply(lambda x: round(x, 2))
        # Теперь в колонке value_currency реальная сумма в рублях

        # Конец пересчета в нужную валюту

        # Отбираем нужные колонки
        sel_df = pandas.DataFrame(sel_df,
                                  columns=['post_date', 'fullname', 'value_currency'])
                                           # 'value_currency', 'rate', 'value'])

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
        for col in cols[1:]:
            sel_df[col] = sel_df[col].apply(lambda x: x if x else '-')
        sel_df.set_index(cols, inplace=True)
        # sel_df = sel_df.reset_index()

        # Здесь получается очень интересная таблица, но она не так интересна как в балансах
        # self.dataframe_to_excel(sel_df, 'turnover_split')

        # Переворот дат из строк в колонки
        unst = sel_df.unstack(level='post_date', fill_value=0)
        unst.columns = unst.columns.droplevel()

        # self.dataframe_to_excel(unst, 'unst-')

        # Группировка по нужному уровню
        group = unst.groupby(level=glevel).sum()

        # Список полей для подсчета среднего
        cols = group.columns.tolist()
        # group.loc['All', ''] = group.sum(level=0)

        # group = group.append([group, pandas.DataFrame(group.sum(axis=0), columns=['Grand Total']).T])


        # Добавление итогов
        if total_row or total_col or mean_col:
            group = self.add_totals(group, total_row=total_row, total_col=total_col, mean_col=mean_col,
                   total_name=total_name, mean_name=mean_name,
                   empty_col=empty_col)




        # print(group.index)
        # self.dataframe_to_excel(group, 'group')

        # return


        # pivot_t = pandas.pivot_table(sel_df, index=glevel, values='value_currency', columns='post_date',
        #                              fill_value=0, aggfunc='sum', margins=margins, margins_name=self.TOTAL_NAME
        #                              )

        # Подсчет среднего
        # if margins:
            # Список полей для подсчета среднего
            # cols = pivot_t.columns.tolist()
            # cols.remove(self.TOTAL_NAME)
            # pivot_t[self.TOTAL_MEAN] = pivot_t[cols].mean(axis=1)

        # print(pivot_t)
        # pivot_t = pivot_t.reset_index()

        return group

    def _after_group(self, dataframe, glevel=1,
                           total_row=False, total_col=False, mean_col=False, total_name=TOTAL_NAME,
                           mean_name=MEAN_NAME, empty_col=False, drop_null=False):
        # Добавление MultiIndex по дате и названиям счетов
        df = dataframe.copy()
        s = df['fullname'].str.split(':', expand=True)
        cols = s.columns
        cols = cols.tolist()
        cols = ['post_date'] + cols
        df = pandas.concat([df, s], axis=1)

        df.sort_values(by=cols, inplace=True)  # Сортировка по дате и счетам

        if drop_null:
            df.dropna(subset=['value_currency'], inplace=True)  # Удаление пустых значений
            # sel_df = sel_df[sel_df['value'] != 0]  # Удаление нулевых значений

        df.drop('fullname', axis=1, inplace=True)  # Удаление колонки fullname
        # Пустые колонки не группируются, добавляю тире в пустые названия счетов.
        for col in cols[1:]:
            df[col] = df[col].apply(lambda x: x if x else '-')
        df.set_index(cols, inplace=True)
        # sel_df = sel_df.reset_index()

        # Здесь получается очень интересная таблица, но она не так интересна как в балансах
        # self.dataframe_to_excel(sel_df, 'turnover_split')

        # Переворот дат из строк в колонки
        unst = df.unstack(level='post_date', fill_value=0)
        unst.columns = unst.columns.droplevel()

        # self.dataframe_to_excel(unst, 'unst-')

        # Группировка по нужному уровню
        group = unst.groupby(level=glevel).sum()

        # Список полей для подсчета среднего
        cols = group.columns.tolist()
        # group.loc['All', ''] = group.sum(level=0)

        # group = group.append([group, pandas.DataFrame(group.sum(axis=0), columns=['Grand Total']).T])


        # Добавление итогов
        if total_row or total_col or mean_col:
            group = self.add_totals(group, total_row=total_row, total_col=total_col, mean_col=mean_col,
                                    total_name=total_name, mean_name=mean_name,
                                    empty_col=empty_col)




            # print(group.index)
            # self.dataframe_to_excel(group, 'group')

            # return


            # pivot_t = pandas.pivot_table(sel_df, index=glevel, values='value_currency', columns='post_date',
            #                              fill_value=0, aggfunc='sum', margins=margins, margins_name=self.TOTAL_NAME
            #                              )

            # Подсчет среднего
            # if margins:
            # Список полей для подсчета среднего
            # cols = pivot_t.columns.tolist()
            # cols.remove(self.TOTAL_NAME)
            # pivot_t[self.TOTAL_MEAN] = pivot_t[cols].mean(axis=1)

        # print(pivot_t)
        # pivot_t = pivot_t.reset_index()

        return group

    @staticmethod
    def add_totals(dataframe, total_row=True, total_col=False, mean_col=False,
                   total_name=TOTAL_NAME, mean_name=MEAN_NAME,
                   empty_col=False):
        """
        Добавляет итоги в DataFrame
        :param dataframe:
        :param total_row: Добавить строку итогов
        :param total_col: Добавить колонку итогов
        :param mean_col: Добавить колонку среднее
        :param total_name: Имя итогов
        :param mean_name: Имя среднего
        :param empty_col: Добавить пустую колонку перед итогами
        :return: DataFrame с итогами
        """
        df = dataframe.copy()
        if total_row:
            df = GCReport.add_row_total(df,total_name=total_name)

        if total_col or mean_col:
            df = GCReport.add_col_total(df, total=total_col, mean=mean_col,
                                        total_name=total_name, mean_name=mean_name,
                                        empty_col=empty_col)
        return df



    @staticmethod
    def add_row_total(dataframe, total_name=TOTAL_NAME):

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

    @staticmethod
    def add_col_total(dataframe, total=True, mean=True, total_name=TOTAL_NAME, mean_name=MEAN_NAME, empty_col=False):
        # Список полей для подсчета среднего
        cols = dataframe.columns.tolist()
        df_ret = dataframe.copy()
        # Добавление пустого столбца
        if empty_col:
            df_ret[''] = ''
        if total:
            df_ret[total_name] = df_ret[cols].sum(axis=1)
        if mean:
            df_ret[mean_name] = df_ret[cols].mean(axis=1)

        return df_ret

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
        profit = df_income.loc[self.TOTAL_NAME] - df_expense.loc[self.TOTAL_NAME]
        # empty column
        # df_income['1'] = 1
        # df_expense['1'] = 1
        profit[0] = PROFIT_NAME
        idxcols = profit.index.names
        idxcols = [0] + idxcols
        profit.set_index(0, append=True, inplace=True)
        profit = profit.reorder_levels(idxcols)

        # empty line
        df_empty = pandas.DataFrame(index=profit.index, columns=profit.columns)

        df_empty = df_empty.drop(PROFIT_NAME)
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

    def dataframe_to_excel(self, dataframe, filename, sheet='Sheet1', datetime_format='dd-mm-yyyy hh:mm:ss'):
        """
        Записывает dataFrame в excel. Указывать только имя файла без расширения!
        :param dataframe:
        :param filename: Указывать только имя файла без расширения
        :return:
        """
        if not filename.endswith('.xlsx'):
            filename = os.path.join(self.dir_excel, filename + ".xlsx")

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer = pandas.ExcelWriter(filename, engine='xlsxwriter', datetime_format=datetime_format)

        # Convert the dataframe to an XlsxWriter Excel object.
        dataframe.to_excel(writer, sheet_name=sheet)

        # Get the xlsxwriter objects from the dataframe writer object.
        workbook = writer.book
        worksheet = writer.sheets[sheet]

        # Close the Pandas Excel writer and output the Excel file.
        writer.save()

        # dataframe.to_excel(filename)

    def group_prices_by_period(self, from_date, to_date, period='M', guids=None):
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
