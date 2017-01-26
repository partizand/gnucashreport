import os

import openpyxl
import piecash
import pandas
from operator import attrgetter
import datetime


class RepBuilder:
    """
    DataFrame implementation of GnuCash database tables for buil reports
    """

    dir_excel = "U:/tables"
    # Имя файла excel по умолчанию для сохранения/чтения данных DataFrame таблиц
    excel_filename="tables.xlsx"

    book_name=None

    # Merged splits and transactions
    # df_m_splits = None

    root_account_guid = None

    def __init__(self):
        self.excel_filename=os.path.join(self.dir_excel,self.excel_filename)
        self.df_accounts = pandas.DataFrame()
        self.df_transactions = pandas.DataFrame()
        self.df_commodities = pandas.DataFrame()
        self.df_splits = pandas.DataFrame()
        self.df_prices = pandas.DataFrame()

    def to_excel(self, filename=None):
        """
        Запись таблиц DataFrame в фалй Excel. Для отладки
        :param filename:
        :return:
        """
        if filename is None:
            filename = self.excel_filename

        writer = pandas.ExcelWriter(self.excel_filename)
        self.df_accounts.to_excel(writer,"accounts")
        self.df_transactions.to_excel(writer, "transactions")
        self.df_commodities.to_excel(writer,"commodities")
        self.df_splits.to_excel(writer,"splits")
        self.df_prices.to_excel(writer,"prices")

        writer.save()

    def read_from_excel(self, filename=None):
        """
        Чтение данных из Excel, вместо чтения из файла gnucash
        :param filename:
        :return:
        """
        if filename is None:
            filename = self.excel_filename

        self.book_name=os.path.basename(filename)

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

    def group_accounts_by_period(self, from_date, to_date, period='M', account_type='EXPENSE', glevel=2):
        """
        Получить сводный DataFrame по счетам типа type за период
        :param from_date:
        :param period:
        :param type:
        :return:
        """
        # select period and account type
        sel_df = self.df_splits[(self.df_splits['post_date'] >= from_date)
                                & (self.df_splits['post_date'] <= to_date)
                                & (self.df_splits['account_type'] == account_type)]

        # Группировка по месяцу
        sel_df.set_index('post_date', inplace=True)
        sel_df = sel_df.groupby([pandas.TimeGrouper(period), 'fullname', 'mnemonic']).value.sum().reset_index()

        # Тестовая запись промежуточных итогов
        self.dataframe_to_excel(sel_df, "grouped_acc1")

        # Добавление MultiIndex по дате и названиям счетов
        s = sel_df['fullname'].str.split(':', expand=True)
        cols = s.columns
        cols = cols.tolist()
        cols = ['post_date'] + cols
        sel_df = pandas.concat([sel_df, s], axis=1)
        sel_df.set_index(cols, inplace=True)
        #print(sel_df.head())




        # Группировка по нужному уровню
        # levels = list(range(0,glevel))
        sel_df = sel_df.groupby(level=[0, glevel]).sum().reset_index()
        #print(sel_df)

        # Timestap to date
        sel_df['post_date'] = sel_df['post_date'].apply(lambda x: x.date())

        # inverse income
        if account_type == 'INCOME':
            sel_df['value'] = sel_df['value'].apply(lambda x: -1 * x)

        # Переворот в сводную
        pivot_t = pandas.pivot_table(sel_df, index=(glevel-1), values='value', columns='post_date',aggfunc='sum', fill_value=0)


        #ndf = sel_df.groupby([pandas.TimeGrouper(period), 'name','fullname', 'account_guid']).value.sum().reset_index()

        return pivot_t

    def dataframe_to_excel(self, dataframe, filename):
        """
        Записывает dataFrame в excel. Указывать только имя файла без расширения!
        :param dataframe:
        :param filename: Указывать только имя файла без расширения
        :return:
        """
        filename = os.path.join(self.dir_excel, filename+".xlsx")
        dataframe.to_excel(filename)

    def group_prices_by_period(self,from_date, to_date, period='M'):
        """
        Получение курса/цен активов за период
        Возвращает таблицу с ценой каждого актива на конец периода (по последней ближайшей к дате)
        :param from_date:
        :param to_date:
        :param period:
        :return:
        """

        # Индекс по периоду
        idx = pandas.date_range(from_date, to_date, freq=period)
        # Список mnemonic
        mnem_list = self.df_prices['mnemonic'].drop_duplicates().tolist()

        # Отбор строк по заданному периоду
        sel_df = self.df_prices[(self.df_prices['date'] >= from_date)
                                & (self.df_prices['date'] <= to_date)]

        sel_df['date'] = pandas.to_datetime(sel_df['date'])
        print(sel_df['date'])
        return
        # цикл по всем mnemonic
        group_prices = None
        for mnemonic in mnem_list:

            # select period and account type
            sel_mnem = sel_df[(sel_df['mnemonic'] == mnemonic)]

            # Группировка по месяцу

            sel_mnem = sel_mnem.set_index('date')
            # sel_mnem['date'] = pandas.to_datetime(sel_mnem['date'])
            # print(sel_mnem)

            #sel_df = sel_df.groupby([pandas.TimeGrouper(period), 'mnemonic']).value.last().reset_index()
            sel_mnem = sel_mnem.groupby([pandas.TimeGrouper(period), 'mnemonic']).value.last().reset_index() # to_frame() #.reset_index()
            # Эти две строки добавляет недостающие периоды и устанавливает в них ближайшее значение
            sel_mnem.set_index(['date'], inplace=True)
            print(sel_mnem)
            sel_mnem = sel_mnem.reindex(idx, method='nearest')
            if group_prices is None:
                group_prices = sel_mnem
            else:
                group_prices = group_prices.append(sel_mnem)

        print(group_prices)
        return group_prices

    def get_balance(self, account_name):
        return self.df_splits.loc[self.df_splits['fullname'] == account_name, 'value'].sum()

    def open_book(self, sqlite_file):
        self.book_name = os.path.basename(sqlite_file)
        with piecash.open_book(sqlite_file) as gnucash_book:

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
            self.df_accounts=pandas.merge(self.df_accounts,mems, left_on='commodity_guid', right_index=True)



            # Transactions

            # Get from piecash
            t_transactions = gnucash_book.session.query(piecash.Transaction).all()
            # fields transactions
            fields = ["guid", "currency_guid", "num",
                      "post_date", "description"]
            self.df_transactions = self.object_to_dataframe(t_transactions, fields)

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
            # Add commodity mnemonic to prices
            self.df_prices = pandas.merge(self.df_prices, mems, left_on='commodity_guid', right_index=True)

            # merge splits and accounts
            df_acc_splits = pandas.merge(self.df_splits, self.df_accounts, left_on='account_guid',
                                         right_index=True)
            df_acc_splits.rename(columns={'description': 'description_account'}, inplace=True)
            # merge splits and accounts with transactions
            self.df_splits = pandas.merge(df_acc_splits, self.df_transactions, left_on='transaction_guid',
                                            right_index=True)



            # self._base_operation()

    # def _base_operation(self):
    #     """
    #     Some base operation on dataframes after get data
    #     :return:
    #     """




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



