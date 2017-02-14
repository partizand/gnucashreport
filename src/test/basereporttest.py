import datetime

from gcreports.gnucashdata import GNUCashData
from gcreports.xlsxreport import XLSXReport
from test.basetest import BaseTest


class BaseReportTest(BaseTest):
    """
    Тестирование построения отчетов по данным
    All testing data on external resource because it is real data
    """

    from_date = GNUCashData.test_from_date
    to_date = GNUCashData.test_to_date
    rep = GNUCashData()
    glevel = GNUCashData.test_glevel

    pickle_assets = GNUCashData.pickle_assets
    pickle_loans = GNUCashData.pickle_loans
    pickle_expense = GNUCashData.pickle_expense
    pickle_income = GNUCashData.pickle_income
    pickle_profit = GNUCashData.pickle_profit
    pickle_equity = GNUCashData.pickle_equity

    def test_assets(self):
        # filename = 'assets.pkl'
        # account_types = GNUCashData.ALL_ASSET_TYPES
        account_types = GNUCashData.ALL_ASSET_TYPES
        df = self.rep.balance_by_period(from_date=self.from_date, to_date=self.to_date,
                                        account_types=account_types, glevel=1)
        self.pickle_control(self.pickle_assets, df, 'Group assets')

    def test_loans(self):
        # filename = 'assets.pkl'
        df = self.rep.balance_by_period(from_date=self.from_date, to_date=self.to_date,
                                         account_types=[GNUCashData.LIABILITY], glevel=0)
        self.pickle_control(self.pickle_loans, df, 'Loans')

    def test_expense(self):
        # filename = 'expense.pkl'
        df = self.rep.turnover_by_period(from_date=self.from_date, to_date=self.to_date, account_type=GNUCashData.EXPENSE,
                                         glevel=self.glevel)
        self.pickle_control(self.pickle_expense, df, 'Group expenses')

    def test_income(self):
        # filename = 'income.pkl'
        df = self.rep.turnover_by_period(from_date=self.from_date, to_date=self.to_date, account_type=GNUCashData.INCOME,
                                         glevel=self.glevel)
        self.pickle_control(self.pickle_income, df, 'Group income')

    def test_profit(self):
        # filename = 'profit.pkl'
        df = self.rep.profit_by_period(from_date=self.from_date, to_date=self.to_date, glevel=self.glevel)
        self.pickle_control(self.pickle_profit, df, 'profit')

    def test_equity(self):
        # filename = 'profit.pkl'
        df = self.rep.equity_by_period(from_date=self.from_date, to_date=self.to_date, glevel=self.glevel)
        self.pickle_control(self.pickle_equity, df, 'equity')

