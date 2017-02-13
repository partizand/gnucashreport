import datetime

from gcreports.gcreport import GCReport
from test.basetest import BaseTest


class BaseReportTest(BaseTest):
    """
    Тестирование построения отчетов по данным
    All testing data on external resource because it is real data
    """

    from_date = datetime.date(2016, 1, 1)
    to_date = datetime.date(2016, 12, 31)
    rep = GCReport()
    glevel = 1

    def test_balance(self):
        filename = 'assets.pkl'
        df = self.rep.balance_by_period(from_date=self.from_date, to_date=self.to_date)
        self.pickle_control(filename, df, 'Group assets')

    def test_turnover_expense(self):
        filename = 'expense.pkl'
        df = self.rep.turnover_by_period(from_date=self.from_date, to_date=self.to_date, account_type=GCReport.EXPENSE,
                                         glevel=self.glevel)
        self.pickle_control(filename, df, 'Group expenses')

    def test_turnover_income(self):
        filename = 'income.pkl'
        df = self.rep.turnover_by_period(from_date=self.from_date, to_date=self.to_date, account_type=GCReport.INCOME,
                                         glevel=self.glevel)
        self.pickle_control(filename, df, 'Group income')

    def test_profit(self):
        filename = 'profit.pkl'
        df = self.rep.profit_by_period(from_date=self.from_date, to_date=self.to_date, glevel=self.glevel)
        self.pickle_control(filename, df, 'profit')
