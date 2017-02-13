import datetime

from gcreports.gcreport import GCReport
from test.basetest import BaseTest


class BaseReportTest(BaseTest):
    """
    Тестирование построения отчетов по данным
    All testing data on external resource because it is real data
    """

    from_date = GCReport.test_from_date
    to_date = GCReport.test_to_date
    rep = GCReport()
    glevel = GCReport.test_glevel

    pickle_assets = GCReport.pickle_assets
    pickle_loans = GCReport.pickle_loans
    pickle_expense = GCReport.pickle_expense
    pickle_income = GCReport.pickle_income
    pickle_profit = GCReport.pickle_profit
    pickle_equity = GCReport.pickle_equity

    def test_assets(self):
        # filename = 'assets.pkl'
        df = self.rep.balance_by_period(from_date=self.from_date, to_date=self.to_date, glevel=self.glevel)
        self.pickle_control(self.pickle_assets, df, 'Group assets')

    def test_loans(self):
        # filename = 'assets.pkl'
        df = self.rep.balance_by_period(from_date=self.from_date, to_date=self.to_date,
                                        account_types=[GCReport.LIABILITY], glevel=self.glevel)
        self.pickle_control(self.pickle_loans, df, 'Loans')

    def test_expense(self):
        # filename = 'expense.pkl'
        df = self.rep.turnover_by_period(from_date=self.from_date, to_date=self.to_date, account_type=GCReport.EXPENSE,
                                         glevel=self.glevel)
        self.pickle_control(self.pickle_expense, df, 'Group expenses')

    def test_income(self):
        # filename = 'income.pkl'
        df = self.rep.turnover_by_period(from_date=self.from_date, to_date=self.to_date, account_type=GCReport.INCOME,
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

