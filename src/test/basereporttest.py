import datetime

from gcreports.gcreport import GCReport
from test.basetest import BaseTest


class BaseReportTest(BaseTest):
    """
    Тестирование построения отчетов по данным
    All testing data on external resource because it is real data
    """

    # bookfile = "u:/sqllite_book/real-2017-01-26.gnucash"
    # bookfile_xml = 'U:/xml_book/GnuCash-base.gnucash'
    from_date = datetime.date(2016, 1, 1)
    to_date = datetime.date(2016, 12, 31)
    rep = GCReport()
    # rep_xml = RepBuilder()

    def test_balance_sql(self):
        filename = 'assets.pkl'
        df = self.rep.balance_by_period(from_date=self.from_date, to_date=self.to_date)
        self.pickle_control(filename, df, 'Group assets')

    def test_turnover_expense_sql(self):
        filename = 'expense.pkl'
        df = self.rep.turnover_by_period(from_date=self.from_date, to_date=self.to_date, account_type=GCReport.EXPENSE)
        # df_etalon = pandas.read_pickle(filename)
        # assert_frame_equal(df, df_etalon, check_like=True, obj='Group expenses')
        self.pickle_control(filename, df, 'Group expenses')

    def test_turnover_income_sql(self):
        filename = 'income.pkl'
        df = self.rep.turnover_by_period(from_date=self.from_date, to_date=self.to_date, account_type=GCReport.INCOME)
        # df_etalon = pandas.read_pickle(filename)
        # assert_frame_equal(df, df_etalon, check_like=True, obj='Group income')
        self.pickle_control(filename, df, 'Group income')
