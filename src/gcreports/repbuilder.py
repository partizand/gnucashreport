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
            # self.df_prices = pandas.merge(self.df_prices, mems, left_on='commodity_guid', right_index=True)
            self.df_prices = pandas.merge(self.df_prices, self.df_commodities, left_on='commodity_guid', right_index=True)
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
        # self.dataframe_to_excel(sel_df, 'sel_df1')
        # return
        sel_df = sel_df[~sel_df.index.duplicated(keep='last')]

        # print(sel_df)
        # return

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
                has_balances = not (df_acc['balance'].apply(lambda x: x == 0).all())
                # print(has_balances)
                # return
                # Берем только не пустые счета
                if has_balances:

                    df_acc.index.name = 'post_date'
                    df_acc['account_guid'] = account_guid
                    df_acc.set_index('account_guid', append=True, inplace=True)
                    # Меняем местами индексы
                    df_acc = df_acc.swaplevel()

                    # if group_prices.empty:
                    #     group_prices = sel_mnem
                    # else:
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
        # print(group_prices)
        # return
        # Добавление колонки курс
        group_acc = group_acc.merge(group_prices, left_on=['commodity_guid', 'post_date'], right_index=True,
                              how='left')

        # Теперь в колонке rate курс ценной бумаги в рублях
        group_acc.rename(columns={'value': 'rate'}, inplace=True)
        # Заполнить пустые поля еденицей
        group_acc['rate'] = group_acc['rate'].fillna(Decimal(1))

        # Пересчет в валюту представления
        group_acc['balance_currency'] = (group_acc['balance'] * group_acc['rate']).apply(lambda x: round(x, 2))
        # Теперь в колонке balance_currency реальная сумма в рублях

        # Конец пересчета в нужную валюту
        # self.dataframe_to_excel(group_acc, 'group_acc')
        # print(group_acc)

        # Отбираем нужные колонки
        group_acc = pandas.DataFrame(group_acc,
                                  columns=['post_date', 'fullname',
                                           'balance_currency', 'rate', 'balance'])
        # self.dataframe_to_excel(group_acc, 'group_acc')

        # return

        # Добавление MultiIndex по дате и названиям счетов
        s = group_acc['fullname'].str.split(':', expand=True)
        cols = s.columns
        cols = cols.tolist()
        cols = ['post_date'] + cols
        group_acc = pandas.concat([group_acc, s], axis=1)
        group_acc.sort_values(by=cols, inplace=True)
        group_acc.dropna(subset=['balance_currency'], inplace=True)
        group_acc.set_index(cols, inplace=True)

        self.dataframe_to_excel(group_acc, 'group_acc_split')

        # print(sel_df.head())

        # Группировка по нужному уровню
        # levels = list(range(0,glevel))

        group_acc = group_acc.groupby(level=[0, glevel]).balance_currency.sum().reset_index()
        self.dataframe_to_excel(group_acc, 'group_acc_gr')

        # print(group_acc)
        # return
        # print(sel_df)

        # Timestap to date
        # sel_df['post_date'] = sel_df['post_date'].apply(lambda x: x.date())

        # inverse income
        # if account_type == 'INCOME':
        #     sel_df['value'] = sel_df['value'].apply(lambda x: -1 * x)

        # Переворот в сводную
        pivot_t = pandas.pivot_table(group_acc, index=(glevel - 1), values='balance_currency', columns='post_date', aggfunc='last',
                                     fill_value=0)

        # self.dataframe_to_excel(pivot_t, 'pivot_t')

        return pivot_t

    def turnover_by_period(self, from_date: date, to_date: date, period='M', account_type=EXPENSE, glevel=2):
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
        # group_prices = group_prices.reset_index()

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
        if not filename.endswith('.xlsx'):
            filename = os.path.join(self.dir_excel, filename + ".xlsx")
        dataframe.to_excel(filename)

    def group_prices_by_period(self, from_date, to_date, period='M', guids=None):
        """
        Получение курса/цен активов за период
        Возвращает таблицу с ценой каждого актива на конец периода (по последней ближайшей к дате)
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
        sel_df = pandas.DataFrame(self.df_prices, columns=['commodity_guid', 'date', 'mnemonic', 'currency_guid', 'value'])
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
        currency_guids = set(group_prices['currency_guid'].drop_duplicates().tolist()) & all_commodities_guids
        # print(currency_guids)
        if currency_guids:
            # TODO: Здесь нужен пересчет в валюту представления
            pass

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
