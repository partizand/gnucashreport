import os

import piecash
import pandas
import numpy
from operator import attrgetter
from datetime import datetime, date, time

from decimal import Decimal


class RepBuilder:
    """
    DataFrame implementation of GnuCash database tables for buil reports

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
    ASSETS = 'ASSETS'
    STOCK = 'STOCK'
    MUTUAL = 'MUTUAL'
    INCOME = 'INCOME'
    EXPENSE = 'EXPENSE'
    EQUITY = 'EQUITY'
    LIABILITY = 'LIABILITY'
    ROOT = 'ROOT'
    # GNUCash all account assets types
    ALL_ASSET_TYPES = [CASH, BANK, ASSETS, STOCK, MUTUAL]


    df_accounts = pandas.DataFrame()

    dir_excel = "U:/tables"
    # Имя файла excel по умолчанию для сохранения/чтения данных DataFrame таблиц
    excel_filename = "tables.xlsx"

    book_name = None

    # Merged splits and transactions
    # df_m_splits = None

    root_account_guid = None

    def __init__(self):
        self.excel_filename = os.path.join(self.dir_excel, self.excel_filename)
        self.df_accounts = pandas.DataFrame()
        self.df_transactions = pandas.DataFrame()
        self.df_commodities = pandas.DataFrame()
        self.df_splits = pandas.DataFrame()
        self.df_prices = pandas.DataFrame()

    def open_book(self, sqlite_file, open_if_lock=False):
        """
        Open gnucash sqlite file
        :param sqlite_file:
        :param open_if_lock:
        :return:
        """

        self.book_name = os.path.basename(sqlite_file)
        with piecash.open_book(sqlite_file, open_if_lock=open_if_lock) as gnucash_book:
            # Read data tables in dataframes

            # commodities

            # preload list of commodities
            t_commodities = gnucash_book.session.query(piecash.Commodity).filter(
                piecash.Commodity.namespace != "template").all()
            fields = ["guid", "namespace", "mnemonic",
                      "fullname", "cusip", "fraction",
                      "quote_flag", "quote_source", "quote_tz"]
            self.df_commodities = self.object_to_dataframe(t_commodities, fields)

            # Accounts

            # Get from piecash
            self.root_account_guid = gnucash_book.root_account.guid
            t_accounts = gnucash_book.session.query(piecash.Account).all()
            # fields accounts
            fields = ["guid", "name", "type", "placeholder",
                      "commodity_guid", "commodity_scu",
                      "parent_guid", "description", "hidden"]
            self.df_accounts = self.object_to_dataframe(t_accounts, fields)
            # rename to real base name of field from piecash name
            self.df_accounts.rename(columns={'type': 'account_type'}, inplace=True)
            # Get fullname of accounts
            self.df_accounts['fullname'] = self.df_accounts.index.map(self._get_fullname_account)
            # Add commodity mnemonic to accounts
            mems = self.df_commodities['mnemonic'].to_frame()
            self.df_accounts = pandas.merge(self.df_accounts, mems, left_on='commodity_guid', right_index=True)

            # Transactions

            # Get from piecash
            t_transactions = gnucash_book.session.query(piecash.Transaction).all()
            # fields transactions
            fields = ["guid", "currency_guid", "num",
                      "post_date", "description"]
            self.df_transactions = self.object_to_dataframe(t_transactions, fields)
            # Convert datetme to date (skip time)
            self.df_transactions['post_date'] = self.df_transactions['post_date'].apply(lambda x: pandas.to_datetime(x.date()))

            # Splits

            # load all splits
            t_splits = gnucash_book.session.query(piecash.Split).all()
            # Some fields not correspond to real names in DB
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
            # print(self.df_prices['date'].dtype.tz)
            # Add commodity mnemonic to prices
            self.df_prices = pandas.merge(self.df_prices, mems, left_on='commodity_guid', right_index=True)
            # Convert datetme to date (skip time)
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

    def balance_by_period(self, from_date: date, to_date: date, period='M', account_types=ALL_ASSET_TYPES, glevel=2):

        # Отбор проводок по типам счетов
        # self.df_splits['quantity'] = self.df_splits['quantity'].astype(numpy.dtype(Decimal))
        # self.df_splits['quantity'] = self.df_splits['quantity'].astype(numpy.float)
        sel_df = self.df_splits[(self.df_splits['account_type']).isin(account_types)].copy()

        # a = sel_df['quantity'][0]
        # print(type(a))

        # Почему-то cumsum не работает с Decimal, но работает с float
        # преобразовываем во float
        # sel_df['quantity'] = sel_df['quantity'].astype(numpy.float)
        # sel_df['quantity'] = sel_df['quantity'].astype(numpy.dtype(Decimal))
        # self.df_splits['quantity'] = self.df_splits['quantity'].astype(numpy.float)
        # df['value'] = df['value'].astype(numpy.dtype(Decimal))

        # Добавление колонки нарастающий итог по счетам
        # Будет ли нарастающий итог по порядку возрастания дат???? Нет! Нужно сначала отсортировать
        sel_df.sort_values(by='post_date', inplace=True)
        sel_df['balance'] = sel_df.groupby('fullname')['quantity'].transform(pandas.Series.cumsum)

        # Для каждого актива берем баланс на конец каждого периода

        # Индекс по периоду
        idx = pandas.date_range(from_date, to_date, freq=period)

        # цикл по всем fullname
        fullname_list = sel_df['fullname'].drop_duplicates().tolist()
        group_splits = None
        for fullname in fullname_list:

            # select period and account type
            sel_fullname = sel_df[(sel_df['fullname'] == fullname)]
            if not sel_fullname.empty:

                # Группировка по месяцу

                sel_fullname = sel_fullname.set_index('post_date')

                sel_fullname = sel_fullname.groupby([pandas.TimeGrouper(period), 'fullname']).value.last().reset_index()
                # Эти две строки добавляет недостающие периоды и устанавливает в них ближайшее значение
                sel_fullname.set_index(['post_date'], inplace=True)
                sel_fullname = sel_fullname.reindex(idx, method='nearest')
                if group_splits is None:
                    group_splits = sel_fullname
                else:
                    group_splits = group_splits.append(sel_fullname)

        # print(group_prices)
        # Сброс индекса и переименование полей (?)
        group_splits = group_splits.reset_index()

        self.dataframe_to_excel(group_splits, 'group_splits')
        return


        # Берем нужный интервал
        # start_datetime, finish_datetime = self.get_startfinish_date(from_date, to_date, self.df_splits['post_date'].dtype.tz)
        sel_df = sel_df[(self.df_splits['post_date'] >= from_date) & (self.df_splits['post_date'] <= to_date)]


        # Группировка по месяцу
        sel_df.set_index('post_date', inplace=True)
        sel_df = sel_df.groupby([pandas.TimeGrouper(period), 'fullname', 'mnemonic']).balance.last().reset_index()
        # Здесь нет счетов по которым не было оборотов
        self.dataframe_to_excel(sel_df, 'bal-month')

        # Тут нужно добавить пересчет в нужную валюту

        # Получаем список всех нужных mnemonic
        mnem_list = sel_df['mnemonic'].drop_duplicates().tolist()
        # Получаем их сгруппированные цены
        group_prices = self.group_prices_by_period(from_date, to_date, period, mnem_list)

        # Добавление колонки курс
        sel_df = sel_df.merge(group_prices, left_on=['post_date', 'mnemonic'], right_on=['date', 'mnemonic'],
                              how='left')
        # Заполнить пустые поля еденицей
        sel_df['course'] = sel_df['course'].fillna(Decimal(1))

        # Пересчет в валюту представления
        sel_df['value'] = (sel_df['balance'] * sel_df['course']).apply(lambda x: round(x, 2))
        # sel_df.drop('course', axis=1, inplace=True)  # Удаление колонки курс
        # Теперь в колонке value реальная сумма в рублях
        self.dataframe_to_excel(sel_df, 'after-course')

        # Конец пересчета в нужную валюту

        # Добавление MultiIndex по дате и названиям счетов
        s = sel_df['fullname'].str.split(':', expand=True)
        cols = s.columns
        cols = cols.tolist()
        cols = ['post_date'] + cols
        sel_df = pandas.concat([sel_df, s], axis=1)
        sel_df.set_index(cols, inplace=True)



        # print(sel_df)

        # Группировка по нужному уровню
        # levels = list(range(0,glevel))
        sel_df = sel_df.groupby(level=[0, glevel]).sum().reset_index()

        # Переворот в сводную
        pivot_t = pandas.pivot_table(sel_df, index=(glevel - 1), values='value', columns='post_date', aggfunc='sum',
                                     fill_value=0)

        # Проверка на счете Газпрома
        # acc = 'Активы:Долгосрочные активы:Ценные бумаги:Промсвязь ИИС:Газпром а.о.'
        # acc = 'Активы:Долгосрочные активы:Ценные бумаги:Альфа-Директ:Югра Рентный Фонд'
        # sel_df = sel_df[(sel_df['fullname'] == acc)]


        # sel_df = sel_df.groupby(['fullname', 'post_date', 'mnemonic']).quantity.sum() #.groupby(level=[0]).cumsum() #.reset_index()
        # Возвращаем назад decimal
        # sel_df = sel_df.apply(lambda x: Decimal(repr(x)))
        # sel_df = sel_df.groupby(level=[0]).cumsum()

        # print(sel_df.columns.values)
        # a = sel_df[0]
        # print(type(a))

        # sel_df = sel_df.groupby(level=[0]).cumsum()

        # self.df_splits.loc[self.df_splits['fullname'] == account_name, 'quantity'].sum()

        # sel_df['CumValue']=sel_df['quantity'].cumsum()

        # print(pivot_t)
        return pivot_t

    def turnover_by_period(self, from_date: date, to_date: date, period='M', account_type=EXPENSE, glevel=2):
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

        # select period and account type
        # Здесь можно еще добавить часы вмсето добавления колонки
        # Добавление к дате времени в нужном поясе
        # start_time = time(0, 0, 0, 0, tzinfo=self.df_splits['post_date'].dtype.tz)
        # finish_time = time(23, 59, 59, 999999, tzinfo=self.df_splits['post_date'].dtype.tz)
        # start_datetime = datetime.combine(from_date, start_time)
        # finish_datetime = datetime.combine(to_date, finish_time)

        # Timestap to date
        # self.df_splits['post_date'] = self.df_splits['post_date'].apply(lambda x: pandas.to_datetime(x.date()))
        # self.df_splits['post_date'] = self.df_splits['post_date'].date #apply(lambda x: x.date())
        # x.astype('M8[m]')

        # print(self.df_splits)
        # print(self.df_splits.dtypes)
        # return

        # start_datetime, finish_datetime = self.get_startfinish_date(from_date, to_date, self.df_splits['post_date'].dtype.tz)

        # Фильтрация по времени
        # sel_df = self.df_splits[(self.df_splits['post_date'] >= start_datetime)
        #                         & (self.df_splits['post_date'] <= finish_datetime)
        #                         & (self.df_splits['account_type'] == account_type)]

        sel_df = self.df_splits[(self.df_splits['post_date'] >= from_date)
                                & (self.df_splits['post_date'] <= to_date)
                                & (self.df_splits['account_type'] == account_type)]

        # Добавление колонки только дата и поиск по ней
        # self.df_splits['only_date'] = self.df_splits['post_date'].dt.normalize()
        # sel_df = self.df_splits[(self.df_splits['only_date'] >= from_date)
        #                         & (self.df_splits['only_date'] <= to_date)
        #                         & (self.df_splits['account_type'] == account_type)]

        # Группировка по месяцу
        sel_df.set_index('post_date', inplace=True)
        sel_df = sel_df.groupby([pandas.TimeGrouper(period), 'fullname', 'mnemonic']).value.sum().reset_index()

        # Тестовая запись промежуточных итогов
        # self.dataframe_to_excel(sel_df, "grouped_acc1")

        # Тут нужно добавить пересчет в нужную валюту

        # Получаем список всех нужных mnemonic
        mnem_list = sel_df['mnemonic'].drop_duplicates().tolist()
        # Получаем их сгруппированные цены
        group_prices = self.group_prices_by_period(from_date, to_date, period, mnem_list)

        # Добавление колонки курс
        sel_df = sel_df.merge(group_prices, left_on=['post_date', 'mnemonic'], right_on=['date', 'mnemonic'],
                              how='left')
        # Заполнить пустые поля еденицей
        sel_df['course'] = sel_df['course'].fillna(Decimal(1))

        # Пересчет в валюту представления
        sel_df['value'] = (sel_df['value'] * sel_df['course']).apply(lambda x: round(x, 2))
        sel_df.drop('course', axis=1, inplace=True)  # Удаление колонки курс
        # Теперь в колонке value реальная сумма в рублях

        # Конец пересчета в нужную валюту

        # Добавление MultiIndex по дате и названиям счетов
        s = sel_df['fullname'].str.split(':', expand=True)
        cols = s.columns
        cols = cols.tolist()
        cols = ['post_date'] + cols
        sel_df = pandas.concat([sel_df, s], axis=1)
        sel_df.set_index(cols, inplace=True)
        # print(sel_df.head())

        # Группировка по нужному уровню
        # levels = list(range(0,glevel))
        sel_df = sel_df.groupby(level=[0, glevel]).sum().reset_index()
        # print(sel_df)

        # Timestap to date
        # sel_df['post_date'] = sel_df['post_date'].apply(lambda x: x.date())

        # inverse income
        if account_type == 'INCOME':
            sel_df['value'] = sel_df['value'].apply(lambda x: -1 * x)

        # Переворот в сводную
        pivot_t = pandas.pivot_table(sel_df, index=(glevel - 1), values='value', columns='post_date', aggfunc='sum',
                                     fill_value=0)

        # ndf = sel_df.groupby([pandas.TimeGrouper(period), 'name','fullname', 'account_guid']).value.sum().reset_index()

        return pivot_t

    def get_startfinish_date(self, start_date: date, finish_date: date, tzinfo=None):
        """
        Добавляет к датам начала и конца периода время, для правильной фильрации
        :param start_date:
        :param finish_date:
        :param tzinfo:
        :return: [start_datetime, finish_datetime]
        """
        start_time = time(0, 0, 0, 0, tzinfo=tzinfo)
        finish_time = time(23, 59, 59, 999999, tzinfo=tzinfo)
        start_datetime = datetime.combine(start_date, start_time)
        finish_datetime = datetime.combine(finish_date, finish_time)
        return [start_datetime, finish_datetime]

    def dataframe_to_excel(self, dataframe, filename):
        """
        Записывает dataFrame в excel. Указывать только имя файла без расширения!
        :param dataframe:
        :param filename: Указывать только имя файла без расширения
        :return:
        """
        filename = os.path.join(self.dir_excel, filename + ".xlsx")
        dataframe.to_excel(filename)

    def group_prices_by_period(self, from_date, to_date, period='M', mnemonics=None):
        """
        Получение курса/цен активов за период
        Возвращает таблицу с ценой каждого актива на конец периода (по последней ближайшей к дате)
        :param from_date:
        :param to_date:
        :param period:
        :param mnemonics: Список названий или None для всех
        :return:
        """

        # Индекс по периоду c учетом timezone
        # idx = pandas.date_range(from_date, to_date, freq=period, tz=self.df_prices['date'].dtype.tz)
        idx = pandas.date_range(from_date, to_date, freq=period)
        # Список mnemonic
        if mnemonics is None:
            mnem_list = self.df_prices['mnemonic'].drop_duplicates().tolist()
        else:
            mnem_list = mnemonics

        # Отбор строк по заданному периоду
        # TODO: Тут если котировка начинается перед интервалом, она не попадет в расчет
        sel_df = self.df_prices[(self.df_prices['date'] >= from_date)
                                & (self.df_prices['date'] <= to_date)]

        # цикл по всем mnemonic
        group_prices = None
        for mnemonic in mnem_list:

            # select period and account type
            sel_mnem = sel_df[(sel_df['mnemonic'] == mnemonic)]
            if not sel_mnem.empty:

                # Группировка по месяцу

                sel_mnem = sel_mnem.set_index('date')

                sel_mnem = sel_mnem.groupby([pandas.TimeGrouper(period), 'mnemonic']).value.last().reset_index()
                # Эти две строки добавляет недостающие периоды и устанавливает в них ближайшее значение
                sel_mnem.set_index(['date'], inplace=True)
                sel_mnem = sel_mnem.reindex(idx, method='nearest')
                if group_prices is None:
                    group_prices = sel_mnem
                else:
                    group_prices = group_prices.append(sel_mnem)

        # print(group_prices)
        # Сброс индекса и переименование полей (?)
        group_prices = group_prices.reset_index()
        group_prices.rename(columns={'index': 'date'}, inplace=True)
        group_prices.rename(columns={'value': 'course'}, inplace=True)
        return group_prices

    def get_balance(self, account_name):
        return self.df_splits.loc[self.df_splits['fullname'] == account_name, 'value'].sum()

    def get_balance_stock(self, account_name):
        return self.df_splits.loc[self.df_splits['fullname'] == account_name, 'quantity'].sum()

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
        df_obj = pandas.DataFrame([[fg(sp) for fg in fields_getter]
                                   for sp in pieobject], columns=fields)
        df_obj.set_index(fields[0], inplace=True)
        return df_obj

    def to_excel(self, filename=None):
        """
        Запись таблиц DataFrame в фалй Excel. Для отладки
        :param filename:
        :return:
        """
        if filename is None:
            filename = self.excel_filename

        writer = pandas.ExcelWriter(filename)
        self.df_accounts.to_excel(writer, "accounts")
        self.df_transactions.to_excel(writer, "transactions")
        self.df_commodities.to_excel(writer, "commodities")
        self.df_splits.to_excel(writer, "splits")
        self.df_prices.to_excel(writer, "prices")

        writer.save()

    def read_from_excel(self, filename=None):
        """
        Чтение данных из Excel, вместо чтения из файла gnucash. Работает дольше sqlite
        :param filename:
        :return:
        """
        if filename is None:
            filename = self.excel_filename

        self.book_name = os.path.basename(filename)
        xls = pandas.ExcelFile(filename)

        self.df_accounts = xls.parse('accounts')
        self.df_transactions = xls.parse('transactions')
        self.df_commodities = xls.parse('commodities')
        self.df_splits = xls.parse('splits')
        self.df_prices = xls.parse('prices')

        xls.close()

    def get_split(self, account_name):
        return self.df_splits[(self.df_splits['fullname'] == account_name)]
        # return self.df_splits.loc['fullname' == account_name]
