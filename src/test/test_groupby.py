import unittest
import datetime
from decimal import Decimal
import pandas
from pandas.util.testing import assert_frame_equal

from gcreports.repbuilder import RepBuilder


class GroupByTest(unittest.TestCase):
    """
    All testing data on external resource because it is real data
    """

    bookfile = "u:/sqllite_book/real-2017-01-26.gnucash"
    from_date = datetime.date(2016, 1, 1)
    to_date = datetime.date(2016, 12, 31)
    rep = RepBuilder()

    def __init__(self, *args, **kwargs):
        super(GroupByTest, self).__init__(*args, **kwargs)
        self.rep.open_book(self.bookfile, open_if_lock=True)

    def test_prices(self):
        filename = 'U:/test_data/prices.pkl'
        df = self.rep.group_prices_by_period(from_date=self.from_date, to_date=self.to_date)
        df_etalon = pandas.read_pickle(filename)
        assert_frame_equal(df, df_etalon, check_like=True, obj='Group Prices')

    def test_balance(self):
        filename = 'U:/test_data/assets.pkl'
        df = self.rep.balance_by_period(from_date=self.from_date, to_date=self.to_date)
        df_etalon = pandas.read_pickle(filename)
        assert_frame_equal(df, df_etalon, check_like=True, obj='Group assets')

    def test_turnover(self):
        filename = 'U:/test_data/expense.pkl'
        df = self.rep.turnover_by_period(from_date=self.from_date, to_date=self.to_date, account_type=RepBuilder.EXPENSE)
        df_etalon = pandas.read_pickle(filename)
        assert_frame_equal(df, df_etalon, check_like=True, obj='Group expenses')


if __name__ == '__main__':
    unittest.main()
