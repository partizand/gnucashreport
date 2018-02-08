import datetime

from gnucashreport.gnucashdata import GNUCashData
from gnucashreport.xlsxreport import XLSXReport
from test.basetest import BaseTest


class BaseReportTest(BaseTest):
    """
    Тестирование построения отчетов по данным
    All testing data on external resource because it is real data
    """

    rep = GNUCashData()

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

