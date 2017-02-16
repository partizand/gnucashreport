import datetime

from gcreports.gnucashdata import GNUCashData
from gcreports.xlsxreport import XLSXReport
from test.basetest import BaseTest


class BaseReportTest(BaseTest):
    """
    Тестирование построения отчетов по данным
    All testing data on external resource because it is real data
    """

    # from_date = GNUCashData.test_from_date
    # to_date = GNUCashData.test_to_date
    rep = GNUCashData()
    # glevel = GNUCashData.test_glevel

    # pickle_assets = GNUCashData.pickle_assets
    # pickle_loans = GNUCashData.pickle_loans
    # pickle_expense = GNUCashData.pickle_expense
    # pickle_income = GNUCashData.pickle_income
    # pickle_profit = GNUCashData.pickle_profit
    # pickle_equity = GNUCashData.pickle_equity

    def test_assets(self):
        df = self.get_assets()
        self.pickle_control(self.pickle_assets, df, 'Assets')

    def test_assets_multi(self):
        df = self.get_assets(glevel=self.test_glevel2)
        filename = self._add_suffix(self.pickle_assets, self.test_level2_suffix)
        self.pickle_control(self.pickle_assets, df, 'Assets multiindex')

    def test_loans(self):
        df = self.get_loans()
        self.pickle_control(self.pickle_loans, df, 'Loans')

    def test_loans_multi(self):
        df = self.get_loans(glevel=self.test_glevel2)
        filename = self._add_suffix(self.pickle_loans, self.test_level2_suffix)
        self.pickle_control(self.pickle_loans, df, 'Loans')

    def test_expense(self):
        # filename = 'expense.pkl'
        # df = self.rep.turnover_by_period(from_date=self.test_from_date, to_date=self.test_to_date, account_type=GNUCashData.EXPENSE,
        #                                  glevel=self.test_glevel)
        df = self.get_expense()
        self.pickle_control(self.pickle_expense, df, 'Group expenses')

    def test_income(self):
        # filename = 'income.pkl'
        # df = self.rep.turnover_by_period(from_date=self.test_from_date, to_date=self.test_to_date, account_type=GNUCashData.INCOME,
        #                                  glevel=self.test_glevel)
        df = self.get_income()
        self.pickle_control(self.pickle_income, df, 'Group income')

    def test_profit(self):
        # filename = 'profit.pkl'
        # df = self.rep.profit_by_period(from_date=self.test_from_date, to_date=self.test_to_date, glevel=self.test_glevel)
        df = self.get_profit()
        self.pickle_control(self.pickle_profit, df, 'profit')

    def test_equity(self):
        # filename = 'profit.pkl'
        # df = self.rep.equity_by_period(from_date=self.test_from_date, to_date=self.test_to_date, glevel=self.test_glevel)
        df = self.get_equity()
        self.pickle_control(self.pickle_equity, df, 'equity')

