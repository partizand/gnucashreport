import unittest
import os
from datetime import date

import pandas
from pandas.util.testing import assert_frame_equal

from gcreports.gnucashdata import GNUCashData


class BaseTest(object):
    """
    Базовый шаблон для тестирования
    """
    # Данные для генерации тестовых данных и тестирования
    # Test info, change before generate test data!
    bookfile_sql = 'v:/gnucash-base/sqlite/GnuCash-base.gnucash'
    bookfile_xml = 'v:/gnucash-base/xml/GnuCash-base.gnucash'
    dir_testdata = 'v:/test_data'
    test_from_date = date(2016, 1, 1)
    test_to_date = date(2016, 12, 31)
    test_period = 'M'
    test_glevel = 1
    # end test info

    rep = GNUCashData()

    test_name = 'abstract_test'

    # dir_testdata = GNUCashData.dir_testdata

    # pickle_prices = 'prices.pkl'
    # pickle_splits = 'splits.pkl'
    # pickle_accounts = 'accounts.pkl'
    # pickle_tr = 'transactions.pkl'
    # pickle_commodities = 'commodities.pkl'

    pickle_prices = GNUCashData.pickle_prices  # 'prices.pkl'
    pickle_splits = GNUCashData.pickle_splits  # 'splits.pkl'
    pickle_accounts = GNUCashData.pickle_accounts  # 'accounts.pkl'
    pickle_tr = GNUCashData.pickle_tr  # 'transactions.pkl'
    pickle_commodities = GNUCashData.pickle_commodities  # 'commodities.pkl'

    pickle_assets = 'assets.pkl'
    pickle_loans = 'loans.pkl'
    pickle_expense = 'expense.pkl'
    pickle_income = 'income.pkl'
    pickle_profit = 'profit.pkl'
    pickle_equity = 'equity.pkl'

    # Конец тестовых данных

    @classmethod
    def save_testdata(cls):
        """
        Запись тестовых pickle для последующей проверки в тестах
        :return:
        """

        # from_date = BaseTest.test_from_date  # date(2016, 1, 1)
        # to_date = BaseTest.test_to_date  # date(2016, 12, 31)
        # glevel = BaseTest.test_glevel
        # period = BaseTest.test_period
        # dir_testdata = BaseTest.dir_testdata

        # open sql book
        # gcdata = GNUCashData()
        # gcdata.open_book_sql(BaseTest.bookfile_sql, open_if_lock=True)

        cls.open_sql()

        # btest.open_sql()

        # save reports
        # df = gcdata.balance_by_period(from_date=from_date, to_date=to_date, period=period, glevel=glevel)
        df = BaseTest.get_assets()
        cls._dataframe_to_pickle(df, filename=BaseTest.pickle_assets, folder=cls.dir_testdata)

        # df = gcdata.balance_by_period(from_date=from_date, to_date=to_date, account_types=[GNUCashData.LIABILITY],
        #                               period=period, glevel=0)
        df = BaseTest.get_loans()
        cls._dataframe_to_pickle(df, filename=BaseTest.pickle_loans, folder=cls.dir_testdata)
        # df = gcdata.turnover_by_period(from_date=from_date, to_date=to_date, period=period,
        #                                account_type=GNUCashData.EXPENSE, glevel=glevel)
        df = BaseTest.get_expense()
        cls._dataframe_to_pickle(df, filename=BaseTest.pickle_expense, folder=cls.dir_testdata)

        # df = gcdata.turnover_by_period(from_date=from_date, to_date=to_date, period=period,
        #                                account_type=GNUCashData.INCOME, glevel=glevel)
        df = BaseTest.get_income()
        cls._dataframe_to_pickle(df, filename=BaseTest.pickle_income, folder=cls.dir_testdata)

        # df = gcdata.profit_by_period(from_date=from_date, to_date=to_date, period=period, glevel=0)
        df = BaseTest.get_profit()
        cls._dataframe_to_pickle(df, filename=BaseTest.pickle_profit, folder=cls.dir_testdata)

        # df = gcdata.equity_by_period(from_date=from_date, to_date=to_date, period=period, glevel=0)
        df = BaseTest.get_equity()
        cls._dataframe_to_pickle(df, filename=BaseTest.pickle_equity, folder=cls.dir_testdata)
        # save sql to pickle book


        cls._save_db_to_pickle(folder=cls.dir_testdata)
        # gcdata = GNUCashData()
        # open xml book
        cls.open_xml() # TODO Будет ли перезапись данных или дозапись?
        # save xml to pickle book
        cls._save_db_to_pickle(folder=cls.dir_testdata, suffix='-xml')

    @classmethod
    def open_sql(cls):
        cls.rep.open_book_sql(BaseTest.bookfile_sql, open_if_lock=True)

    @classmethod
    def open_xml(cls):
        cls.rep.open_book_xml(BaseTest.bookfile_xml)

    @classmethod
    def open_pickle(cls):
        cls.rep._open_book_pickle(folder=BaseTest.dir_testdata)

    @classmethod
    def _save_db_to_pickle(cls, folder, suffix=None):
        """
        For test purpose
        Save book to pickle files
        Запись данных базы в pickle файлы каталога.
        :param folder: Каталог с файлами базы
        :return:
        """
        cls._dataframe_to_pickle(cls.rep.df_accounts, cls._add_suffix(cls.pickle_accounts, suffix), folder=folder)
        cls._dataframe_to_pickle(cls.rep.df_commodities, cls._add_suffix(cls.pickle_commodities, suffix), folder=folder)
        cls._dataframe_to_pickle(cls.rep.df_prices, cls._add_suffix(cls.pickle_prices, suffix), folder=folder)
        cls._dataframe_to_pickle(cls.rep.df_transactions, cls._add_suffix(cls.pickle_tr, suffix), folder=folder)
        cls._dataframe_to_pickle(cls.rep.df_splits, cls._add_suffix(cls.pickle_splits, suffix), folder=folder)

    @classmethod
    def _dataframe_to_pickle(cls, dataframe, filename, folder):
        """
        Записаывает DataFrame в pickle файл
        :param dataframe:
        :param filename:
        :return:
        """
        fullfilename = os.path.join(folder, filename)
        dataframe.to_pickle(fullfilename)


    @staticmethod
    def _add_suffix(filename, suffix):
        if not suffix:
            return filename
        return "{0}{2}.{1}".format(*filename.rsplit('.', 1) + [suffix])

    @classmethod
    def get_assets(cls):
        """
        Get assets dataframe for testing or saving
        :return:
        """
        df = cls.rep.balance_by_period(from_date=cls.test_from_date, to_date=cls.test_to_date,
                                        period=cls.test_period, glevel=cls.test_glevel)
        return df

    @classmethod
    def get_loans(cls):
        """
        Get assets dataframe for testing or saving
        :return:
        """
        df = cls.rep.balance_by_period(from_date=cls.test_from_date, to_date=cls.test_to_date,
                                       account_types=[GNUCashData.LIABILITY],  period=cls.test_period, glevel=0)
        return df

    @classmethod
    def get_expense(cls):
        """
        Get assets dataframe for testing or saving
        :return:
        """
        df = cls.rep.turnover_by_period(from_date=cls.test_from_date, to_date=cls.test_to_date,
                                         account_type=GNUCashData.EXPENSE,
                                         glevel=cls.test_glevel)
        return df

    @classmethod
    def get_income(cls):
        """
        Get assets dataframe for testing or saving
        :return:
        """
        df = cls.rep.turnover_by_period(from_date=cls.test_from_date, to_date=cls.test_to_date,
                                         account_type=GNUCashData.INCOME,
                                         glevel=cls.test_glevel)
        return df

    @classmethod
    def get_profit(cls):
        """
        Get assets dataframe for testing or saving
        :return:
        """
        df = cls.rep.profit_by_period(from_date=cls.test_from_date, to_date=cls.test_to_date,
                                       glevel=cls.test_glevel)
        return df

    @classmethod
    def get_equity(cls):
        """
        Get assets dataframe for testing or saving
        :return:
        """
        df = cls.rep.equity_by_period(from_date=cls.test_from_date, to_date=cls.test_to_date,
                                       glevel=cls.test_glevel)
        return df

    def pickle_control(self, pickle_file, df_to_test, test_name=None):
        """
        Сверка dataframe c эталонным Pickle файлом
        :param pickle_file:
        :param df_to_test:
        :param test_name:
        :return:
        """
        filename = os.path.join(self.dir_testdata, pickle_file)
        df_etalon = pandas.read_pickle(filename)
        assert_frame_equal(df_to_test, df_etalon, check_like=True, obj=test_name)
        self.assertEqual(len(df_to_test), len(df_etalon), 'length of dataframe')

    def dataframe_fields_control(self, df, etalon_fields, df_name):
        """
        Проверка что dataframe содержит колонки с заданными именами
        :param df:
        :param etalon_fields:
        :param df_name:
        :return:
        """
        cols = df.columns.values.tolist()
        for field in etalon_fields:
            self.assertIn(field, cols, 'DataFrame {} contain field {}. {}'.format(df_name, field, self.test_name))


