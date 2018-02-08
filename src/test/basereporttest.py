import datetime

from gnucashreport.gnucashbook import GNUCashBook
from gnucashreport.gnucashdata import GNUCashData

from gnucashreport.xlsxreport import XLSXReport
from test.basetest import BaseTest

from test.testinfo import TestInfo


class BaseReportTest(BaseTest):
    """
    Тестирование построения отчетов по данным
    All testing data on external resource because it is real data
    """

    PICKLE_ASSETS = 'assets.pkl'
    PICKLE_LOANS = 'loans.pkl'
    PICKLE_EXPENSE = 'expense.pkl'
    PICKLE_INCOME = 'income.pkl'
    PICKLE_PROFIT = 'profit.pkl'
    PICKLE_EQUITY = 'equity.pkl'
    PICKLE_INFLATION = 'inflation.pkl'

    rep = GNUCashData()

    #--------------------
    # base functions

    @classmethod
    def save_testdata(cls):
        """
        Запись тестовых pickle для последующей проверки в тестах
        :return:
        """

        # cls.open_sql()

        cls.rep.open_book_file(TestInfo.BOOKFILE_SQL)

        # save reports
        # Assets
        df = cls.get_assets()
        cls._dataframe_to_pickle(df, filename=cls.pickle_assets, folder=cls.dir_testdata)
        # Assets multi
        df = cls.get_assets(glevel=cls.test_glevel2)
        filename = cls._add_suffix(cls.pickle_assets, cls.test_level2_suffix)
        cls._dataframe_to_pickle(df, filename=filename, folder=cls.dir_testdata)

        # Loans
        df = cls.get_loans()
        cls._dataframe_to_pickle(df, filename=cls.pickle_loans, folder=cls.dir_testdata)
        # Loans multi
        df = cls.get_loans(glevel=cls.test_glevel2)
        filename = cls._add_suffix(cls.pickle_loans, cls.test_level2_suffix)
        cls._dataframe_to_pickle(df, filename=filename, folder=cls.dir_testdata)

        # Expense
        filename = cls.pickle_expense
        df = cls.get_expense()
        cls._dataframe_to_pickle(df, filename=filename, folder=cls.dir_testdata)
        # Expense multi
        df = cls.get_expense(glevel=cls.test_glevel2)
        filename = cls._add_suffix(filename, cls.test_level2_suffix)
        cls._dataframe_to_pickle(df, filename=filename, folder=cls.dir_testdata)

        # Income
        filename = cls.pickle_income
        df = cls.get_income()
        cls._dataframe_to_pickle(df, filename=filename, folder=cls.dir_testdata)
        # Income multi
        df = cls.get_income(glevel=cls.test_glevel2)
        filename = cls._add_suffix(filename, cls.test_level2_suffix)
        cls._dataframe_to_pickle(df, filename=filename, folder=cls.dir_testdata)

        # Profit
        filename = cls.pickle_profit
        df = cls.get_profit()
        cls._dataframe_to_pickle(df, filename=filename, folder=cls.dir_testdata)
        # Profit multi
        df = cls.get_profit(glevel=cls.test_glevel2)
        filename = cls._add_suffix(filename, cls.test_level2_suffix)
        cls._dataframe_to_pickle(df, filename=filename, folder=cls.dir_testdata)

        # Equity
        filename = cls.pickle_equity
        df = cls.get_equity()
        cls._dataframe_to_pickle(df, filename=filename, folder=cls.dir_testdata)
        # Equity multi
        df = cls.get_equity(glevel=cls.test_glevel2)
        filename = cls._add_suffix(filename, cls.test_level2_suffix)
        cls._dataframe_to_pickle(df, filename=filename, folder=cls.dir_testdata)

        # Inflation annual
        filename = cls.pickle_inflation
        df = cls.get_inflation(cumulative=False)
        cls._dataframe_to_pickle(df, filename=filename, folder=cls.dir_testdata)
        # Inflation cumulative
        df = cls.get_inflation(cumulative=True)
        filename = cls._add_suffix(filename, cls.test_level2_suffix)
        cls._dataframe_to_pickle(df, filename=filename, folder=cls.dir_testdata)

        # save sql to pickle book
        cls.rep._read_book_sql(BaseTest.bookfile_sql)  # Получаем сырые данные
        cls._save_db_to_pickle(folder=cls.dir_testdata)

        # save xml to pickle book
        cls.rep._read_book_xml(BaseTest.bookfile_xml)  # Вроде по тестам перезапись данных и все ок
        cls._save_db_to_pickle(folder=cls.dir_testdata, suffix='-xml')

    @classmethod
    def get_assets(cls, glevel=None):
        """
        Get assets dataframe for testing or saving
        :return:
        """
        if not glevel:
            glevel = cls.test_glevel
        df = cls.rep.balance_by_period(from_date=cls.test_from_date, to_date=cls.test_to_date,
                                       period=cls.test_period, glevel=glevel)
        return df

    @classmethod
    def get_loans(cls, glevel=None):
        """
        Get assets dataframe for testing or saving
        :return:
        """
        if not glevel:
            glevel = 0
        df = cls.rep.balance_by_period(from_date=cls.test_from_date, to_date=cls.test_to_date,
                                       account_types=[GNUCashBook.LIABILITY], period=cls.test_period, glevel=glevel)
        return df

    @classmethod
    def get_expense(cls, glevel=None):
        """
        Get assets dataframe for testing or saving
        :return:
        """
        if not glevel:
            glevel = cls.test_glevel
        df = cls.rep.turnover_by_period(from_date=cls.test_from_date, to_date=cls.test_to_date,
                                        account_type=GNUCashBook.EXPENSE,
                                        glevel=glevel)
        return df

    @classmethod
    def get_income(cls, glevel=None):
        """
        Get assets dataframe for testing or saving
        :return:
        """
        if not glevel:
            glevel = cls.test_glevel
        df = cls.rep.turnover_by_period(from_date=cls.test_from_date, to_date=cls.test_to_date,
                                        account_type=GNUCashBook.INCOME,
                                        glevel=glevel)
        return df

    @classmethod
    def get_profit(cls, glevel=None):
        """
        Get assets dataframe for testing or saving
        :return:
        """
        if not glevel:
            glevel = cls.test_glevel
        df = cls.rep.profit_by_period(from_date=cls.test_from_date, to_date=cls.test_to_date,
                                      glevel=glevel)
        return df

    @classmethod
    def get_equity(cls, glevel=None):
        """
        Get assets dataframe for testing or saving
        :return:
        """
        if not glevel:
            glevel = cls.test_glevel
        df = cls.rep.equity_by_period(from_date=cls.test_from_date, to_date=cls.test_to_date,
                                      glevel=glevel)
        return df

    @classmethod
    def get_inflation(cls, cumulative=False, glevel=None):
        """
        Get assets dataframe for testing or saving
        :return:
        """
        if not glevel:
            glevel = cls.test_glevel
        df = cls.rep.inflation_by_period(from_date=cls.test_from_date_y, to_date=cls.test_to_date_y, period='A',
                                         glevel=glevel, cumulative=cumulative)
        return df

    #---------------------

    def test_assets(self):
        df = self.get_assets()
        self.pickle_control(self.pickle_assets, df, 'Assets')

    def test_assets_multi(self):
        df = self.get_assets(glevel=self.test_glevel2)
        filename = self._add_suffix(self.pickle_assets, self.test_level2_suffix)
        self.pickle_control(filename, df, 'Assets multiindex')

    def test_loans(self):
        df = self.get_loans()
        self.pickle_control(self.pickle_loans, df, 'Loans')

    def test_loans_multi(self):
        df = self.get_loans(glevel=self.test_glevel2)
        filename = self._add_suffix(self.pickle_loans, self.test_level2_suffix)
        self.pickle_control(filename, df, 'Loans multiindex')

    def test_expense(self):
        df = self.get_expense()
        self.pickle_control(self.pickle_expense, df, 'Expenses')

    def test_expense_multi(self):
        df = self.get_expense(glevel=self.test_glevel2)
        filename = self._add_suffix(self.pickle_expense, self.test_level2_suffix)
        self.pickle_control(filename, df, 'Expenses multiindex')

    def test_income(self):
        df = self.get_income()
        self.pickle_control(self.pickle_income, df, 'Income')

    def test_income_multi(self):
        df = self.get_income(glevel=self.test_glevel2)
        filename = self._add_suffix(self.pickle_income, self.test_level2_suffix)
        self.pickle_control(filename, df, 'Income multiindex')

    def test_profit(self):
        df = self.get_profit()
        self.pickle_control(self.pickle_profit, df, 'Profit')

    def test_profit_multi(self):
        df = self.get_profit(glevel=self.test_glevel2)
        filename = self._add_suffix(self.pickle_profit, self.test_level2_suffix)
        self.pickle_control(filename, df, 'Profit multiindex')

    def test_equity(self):
        df = self.get_equity()
        self.pickle_control(self.pickle_equity, df, 'Equity')

    def test_equity_multi(self):
        df = self.get_equity(glevel=self.test_glevel2)
        filename = self._add_suffix(self.pickle_equity, self.test_level2_suffix)
        self.pickle_control(filename, df, 'Equity multiindex')

    def test_inflation_annual(self):
        df = self.get_inflation(cumulative=False)
        self.pickle_control(self.pickle_inflation, df, 'Inflation')

    def test_inflation_cumulative(self):
        # Inflation cumulative
        df = self.get_inflation(cumulative=True)
        filename = self._add_suffix(self.pickle_inflation, self.test_level2_suffix)
        self.pickle_control(filename, df, 'Inflation cumulative')

