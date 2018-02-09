import datetime
import unittest

import os
import pandas

from gnucashreport.gnucashbook import GNUCashBook
from gnucashreport.gnucashdata import GNUCashData

from pandas.util.testing import assert_frame_equal

from test.testinfo import TestInfo


class ReportTest(unittest.TestCase):
    """
    Тестирование построения отчетов по данным
    All testing data on external resource because it is real data
    """

    # Данные для генерации тестовых данных и тестирования
    # Test info, change before generate test data!
    BOOKFILE_SQL = 'v:/gnucash-base/sqlite/GnuCash-base.gnucash'
    BOOKFILE_XML = 'v:/gnucash-base/xml/GnuCash-base.gnucash'
    DIR_TESTDATA = 'v:/test_data'


    # end folder options---------------------------------------
    TEST_FROM_DATE = datetime.date(2016, 1, 1)
    TEST_TO_DATE = datetime.date(2016, 12, 31)
    TEST_FROM_DATE_Y = datetime.date(2009, 1, 1)
    TEST_TO_DATE_Y = datetime.date(2016, 12, 31)
    TEST_PERIOD = 'M'
    TEST_GLEVEL = 1
    TEST_GLEVEL2 = [0, 1]
    TEST_LEVEL2_SUFFIX = '-2'

    PICKLE_ASSETS = 'assets.pkl'
    PICKLE_ASSETS_M = 'assets-2.pkl'
    PICKLE_LOANS = 'loans.pkl'
    PICKLE_LOANS_M = 'loans-2.pkl'
    PICKLE_EXPENSE = 'expense.pkl'
    PICKLE_EXPENSE_M = 'expense-2.pkl'
    PICKLE_INCOME = 'income.pkl'
    PICKLE_INCOME_M = 'income-2.pkl'
    PICKLE_PROFIT = 'profit.pkl'
    PICKLE_PROFIT_M = 'profit-2.pkl'
    PICKLE_EQUITY = 'equity.pkl'
    PICKLE_EQUITY_M = 'equity-2.pkl'
    PICKLE_INFLATION = 'inflation.pkl'
    PICKLE_INFLATION_M = 'inflation-2.pkl'

    # rep = GNUCashData()

    @classmethod
    def setUpClass(cls):
        # set fullnames
        # cls.BOOKFILE_XML = os.path.join(cls.DIR_TESTDATA, cls.BOOKFILE_XML)
        # cls.BOOKFILE_SQL = os.path.join(cls.DIR_TESTDATA, cls.BOOKFILE_SQL)
        cls.BOOKFILE_SQL = os.path.join(cls.DIR_TESTDATA, cls.BOOKFILE_SQL)

        # gcrep_xml = GNUCashData()
        # gcrep_sql = GNUCashData()
        # base_path = os.path.dirname(os.path.realpath(__file__))
        # xml_book = os.path.join(base_path, TestInfo.GNUCASH_TESTBASE_XML)
        # sql_book = os.path.join(base_path, TestInfo.GNUCASH_TESTBASE_SQL)
        # gcrep_xml.open_book_file(cls.BOOKFILE_XML)
        # gcrep_sql.open_book_file(cls.BOOKFILE_SQL)

        # cls.test_array = [gcrep_xml, gcrep_sql]
        cls.test_array = cls._get_test_array()

    #--------------------
    # base functions

    @classmethod
    def _get_test_array(cls):
        return [GNUCashData(cls.BOOKFILE_XML), GNUCashData(cls.BOOKFILE_SQL)]

    @classmethod
    def save_testdata(cls):
        """
        Запись тестовых pickle для последующей проверки в тестах
        :return:
        """

        # cls.open_sql()

        # cls.rep.open_book_file(TestInfo.BOOKFILE_SQL)

        # test_array = cls._get_test_array()
        rep = GNUCashData(cls.BOOKFILE_SQL)

        # save reports

        # Assets
        df = cls.get_assets(rep)
        cls._dataframe_to_pickle(df, filename=cls.PICKLE_ASSETS, folder=cls.DIR_TESTDATA)
        # Assets multi
        df = cls.get_assets(rep, glevel=cls.TEST_GLEVEL2)
        # filename = cls._add_suffix(cls.PICKLE_ASSETS, cls.TEST_LEVEL2_SUFFIX)
        cls._dataframe_to_pickle(df, filename=cls.PICKLE_ASSETS_M, folder=cls.DIR_TESTDATA)

        # Loans
        df = cls.get_loans(rep)
        cls._dataframe_to_pickle(df, filename=cls.PICKLE_LOANS, folder=cls.DIR_TESTDATA)
        # Loans multi
        df = cls.get_loans(rep, glevel=cls.TEST_GLEVEL2)
        # filename = cls._add_suffix(cls.PICKLE_LOANS, cls.TEST_LEVEL2_SUFFIX)
        cls._dataframe_to_pickle(df, filename=cls.PICKLE_LOANS_M, folder=cls.DIR_TESTDATA)

        # Expense
        # filename = cls.PICKLE_EXPENSE
        df = cls.get_expense(rep)
        cls._dataframe_to_pickle(df, filename=cls.PICKLE_EXPENSE, folder=cls.DIR_TESTDATA)
        # Expense multi
        df = cls.get_expense(rep, glevel=cls.TEST_GLEVEL2)
        # filename = cls._add_suffix(filename, cls.TEST_LEVEL2_SUFFIX)
        cls._dataframe_to_pickle(df, filename=cls.PICKLE_EXPENSE_M, folder=cls.DIR_TESTDATA)

        # Income
        # filename = cls.PICKLE_INCOME
        df = cls.get_income(rep)
        cls._dataframe_to_pickle(df, filename=cls.PICKLE_INCOME, folder=cls.DIR_TESTDATA)
        # Income multi
        df = cls.get_income(rep, glevel=cls.TEST_GLEVEL2)
        # filename = cls._add_suffix(filename, cls.TEST_LEVEL2_SUFFIX)
        cls._dataframe_to_pickle(df, filename=cls.PICKLE_INCOME_M, folder=cls.DIR_TESTDATA)

        # Profit
        # filename = cls.PICKLE_PROFIT
        df = cls.get_profit(rep)
        cls._dataframe_to_pickle(df, filename=cls.PICKLE_PROFIT, folder=cls.DIR_TESTDATA)
        # Profit multi
        df = cls.get_profit(rep, glevel=cls.TEST_GLEVEL2)
        # filename = cls._add_suffix(filename, cls.TEST_LEVEL2_SUFFIX)
        cls._dataframe_to_pickle(df, filename=cls.PICKLE_PROFIT_M, folder=cls.DIR_TESTDATA)

        # Equity
        # filename = cls.PICKLE_EQUITY
        df = cls.get_equity(rep)
        cls._dataframe_to_pickle(df, filename=cls.PICKLE_EQUITY, folder=cls.DIR_TESTDATA)
        # Equity multi
        df = cls.get_equity(rep, glevel=cls.TEST_GLEVEL2)
        # filename = cls._add_suffix(filename, cls.TEST_LEVEL2_SUFFIX)
        cls._dataframe_to_pickle(df, filename=cls.PICKLE_EQUITY_M, folder=cls.DIR_TESTDATA)

        # Inflation annual
        # filename = cls.PICKLE_INFLATION
        df = cls.get_inflation(rep, cumulative=False)
        cls._dataframe_to_pickle(df, filename=cls.PICKLE_INFLATION, folder=cls.DIR_TESTDATA)
        # Inflation cumulative
        df = cls.get_inflation(rep, cumulative=True)
        # filename = cls._add_suffix(filename, cls.TEST_LEVEL2_SUFFIX)
        cls._dataframe_to_pickle(df, filename=cls.PICKLE_INFLATION_M, folder=cls.DIR_TESTDATA)

        # save sql to pickle book
        # cls.rep._read_book_sql(BaseTest.bookfile_sql)  # Получаем сырые данные
        # cls._save_db_to_pickle(folder=cls.DIR_TESTDATA)

        # save xml to pickle book
        # cls.rep._read_book_xml(BaseTest.bookfile_xml)  # Вроде по тестам перезапись данных и все ок
        # cls._save_db_to_pickle(folder=cls.DIR_TESTDATA, suffix='-xml')

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


    # @staticmethod
    # def _add_suffix(filename, suffix):
    #     """
    #     Adds suffix to filename
    #     :param filename:
    #     :param suffix:
    #     :return:
    #     """
    #     if not suffix:
    #         return filename
    #     return "{0}{2}.{1}".format(*filename.rsplit('.', 1) + [suffix])


    @classmethod
    def get_assets(cls, rep, glevel=None):
        """
        Get assets dataframe for testing or saving
        :return:
        """
        if not glevel:
            glevel = TestInfo.TEST_GLEVEL
        df = rep.balance_by_period(from_date=TestInfo.TEST_FROM_DATE, to_date=cls.TEST_TO_DATE,
                                       period=cls.TEST_PERIOD, glevel=glevel)
        return df

    @classmethod
    def get_loans(cls, rep, glevel=None):
        """
        Get assets dataframe for testing or saving
        :return:
        """
        if not glevel:
            glevel = 0
        df = rep.balance_by_period(from_date=cls.TEST_FROM_DATE, to_date=cls.TEST_TO_DATE,
                                       account_types=[GNUCashBook.LIABILITY], period=cls.TEST_PERIOD, glevel=glevel)
        return df

    @classmethod
    def get_expense(cls, rep, glevel=None):
        """
        Get assets dataframe for testing or saving
        :return:
        """
        if not glevel:
            glevel = cls.TEST_GLEVEL
        df = rep.turnover_by_period(from_date=cls.TEST_FROM_DATE, to_date=cls.TEST_TO_DATE,
                                        account_type=GNUCashBook.EXPENSE,
                                        glevel=glevel)
        return df

    @classmethod
    def get_income(cls, rep, glevel=None):
        """
        Get assets dataframe for testing or saving
        :return:
        """
        if not glevel:
            glevel = cls.TEST_GLEVEL
        df = rep.turnover_by_period(from_date=cls.TEST_FROM_DATE, to_date=cls.TEST_TO_DATE,
                                        account_type=GNUCashBook.INCOME,
                                        glevel=glevel)
        return df

    @classmethod
    def get_profit(cls, rep, glevel=None):
        """
        Get assets dataframe for testing or saving
        :return:
        """
        if not glevel:
            glevel = cls.TEST_GLEVEL
        df = rep.profit_by_period(from_date=cls.TEST_FROM_DATE, to_date=cls.TEST_TO_DATE,
                                      glevel=glevel)
        return df

    @classmethod
    def get_equity(cls, rep, glevel=None):
        """
        Get assets dataframe for testing or saving
        :return:
        """
        if not glevel:
            glevel = cls.TEST_GLEVEL
        df = rep.equity_by_period(from_date=cls.TEST_FROM_DATE, to_date=cls.TEST_TO_DATE,
                                      glevel=glevel)
        return df

    @classmethod
    def get_inflation(cls, rep, cumulative=False, glevel=None):
        """
        Get assets dataframe for testing or saving
        :return:
        """
        if not glevel:
            glevel = cls.TEST_GLEVEL
        df = rep.inflation_by_period(from_date=cls.TEST_FROM_DATE_Y, to_date=cls.TEST_TO_DATE_Y, period='A',
                                         glevel=glevel, cumulative=cumulative)
        return df

    def pickle_control(self, pickle_file, df_to_test, test_name=None):
        """
        Сверка dataframe c эталонным Pickle файлом
        :param pickle_file:
        :param df_to_test:
        :param test_name:
        :return:
        """
        filename = os.path.join(self.DIR_TESTDATA, pickle_file)
        df_etalon = pandas.read_pickle(filename)
        assert_frame_equal(df_to_test, df_etalon, check_like=True, obj=test_name)
        self.assertEqual(len(df_to_test), len(df_etalon), 'length of dataframe')


    #---------------------

    def test_assets(self):
        for rep in self.test_array:
            with self.subTest(rep):
                df = self.get_assets(rep)
                self.pickle_control(self.PICKLE_ASSETS, df, 'Assets')

    def test_assets_multi(self):
        for rep in self.test_array:
            with self.subTest(rep):
                df = self.get_assets(rep, glevel=self.TEST_GLEVEL2)
                # filename = self._add_suffix(self.PICKLE_ASSETS, self.TEST_LEVEL2_SUFFIX)
                self.pickle_control(self.PICKLE_ASSETS_M, df, 'Assets multiindex')

    def test_loans(self):
        for rep in self.test_array:
            with self.subTest(rep):
                df = self.get_loans(rep)
                self.pickle_control(self.PICKLE_LOANS, df, 'Loans')

    def test_loans_multi(self):
        for rep in self.test_array:
            with self.subTest(rep):
                df = self.get_loans(rep, glevel=self.TEST_GLEVEL2)
                # filename = self._add_suffix(self.PICKLE_LOANS, self.TEST_LEVEL2_SUFFIX)
                self.pickle_control(self.PICKLE_LOANS_M, df, 'Loans multiindex')

    def test_expense(self):
        for rep in self.test_array:
            with self.subTest(rep):
                df = self.get_expense(rep)
                self.pickle_control(self.PICKLE_EXPENSE, df, 'Expenses')

    def test_expense_multi(self):
        for rep in self.test_array:
            with self.subTest(rep):
                df = self.get_expense(rep, glevel=self.TEST_GLEVEL2)
                # filename = self._add_suffix(self.PICKLE_EXPENSE, self.TEST_LEVEL2_SUFFIX)
                self.pickle_control(self.PICKLE_EXPENSE_M, df, 'Expenses multiindex')

    def test_income(self):
        for rep in self.test_array:
            with self.subTest(rep):
                df = self.get_income(rep)
                self.pickle_control(self.PICKLE_INCOME, df, 'Income')

    def test_income_multi(self):
        for rep in self.test_array:
            with self.subTest(rep):
                df = self.get_income(rep, glevel=self.TEST_GLEVEL2)
                # filename = self._add_suffix(self.PICKLE_INCOME, self.TEST_LEVEL2_SUFFIX)
                self.pickle_control(self.PICKLE_INCOME_M, df, 'Income multiindex')

    def test_profit(self):
        for rep in self.test_array:
            with self.subTest(rep):
                df = self.get_profit(rep)
                self.pickle_control(self.PICKLE_PROFIT, df, 'Profit')

    def test_profit_multi(self):
        for rep in self.test_array:
            with self.subTest(rep):
                df = self.get_profit(rep, glevel=self.TEST_GLEVEL2)
                # filename = self._add_suffix(self.PICKLE_PROFIT, self.TEST_LEVEL2_SUFFIX)
                self.pickle_control(self.PICKLE_PROFIT_M, df, 'Profit multiindex')

    def test_equity(self):
        for rep in self.test_array:
            with self.subTest(rep):
                df = self.get_equity(rep)
                self.pickle_control(self.PICKLE_EQUITY, df, 'Equity')

    def test_equity_multi(self):
        for rep in self.test_array:
            with self.subTest(rep):
                df = self.get_equity(rep, glevel=self.TEST_GLEVEL2)
                # filename = self._add_suffix(self.PICKLE_EQUITY, self.TEST_LEVEL2_SUFFIX)
                self.pickle_control(self.PICKLE_EQUITY_M, df, 'Equity multiindex')

    def test_inflation_annual(self):
        for rep in self.test_array:
            with self.subTest(rep):
                df = self.get_inflation(rep, cumulative=False)
                self.pickle_control(self.PICKLE_INFLATION, df, 'Inflation')

    def test_inflation_cumulative(self):
        # Inflation cumulative
        for rep in self.test_array:
            with self.subTest(rep):
                df = self.get_inflation(rep, cumulative=True)
                # filename = self._add_suffix(self.PICKLE_INFLATION, self.TEST_LEVEL2_SUFFIX)
                self.pickle_control(self.PICKLE_INFLATION_M, df, 'Inflation cumulative')

