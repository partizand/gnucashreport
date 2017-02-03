import unittest
import datetime
import pandas
from pandas.util.testing import assert_frame_equal

from gcreports.repbuilder import RepBuilder



class BaseDataTest(object):
    """
    All testing data on external resource because it is real data
    """

    # bookfile = "u:/sqllite_book/real-2017-01-26.gnucash"
    # bookfile_xml = 'U:/xml_book/GnuCash-base.gnucash'
    from_date = datetime.date(2016, 1, 1)
    to_date = datetime.date(2016, 12, 31)
    rep = RepBuilder()
    # rep_xml = RepBuilder()

    account_fields = ["name", "account_type", 'mnemonic',
                      "commodity_guid", "commodity_scu",
                      "parent_guid", "description", "hidden"]

    comm_fields = ["namespace", "mnemonic"]
    tr_fields = ["currency_guid", "post_date", "description"]
    split_fields = ["transaction_guid", "account_guid",
                    "memo", "reconcile_state", "value", "quantity"]
    price_fields = ["commodity_guid", "currency_guid",
              "date", "source", "type", "value"]

    # def __init__(self, *args, **kwargs):
    #     super(BaseDataTest, self).__init__(*args, **kwargs)
    #     self.rep.open_book_sql(self.bookfile, open_if_lock=True)
    #     self.rep_xml.open_book_xml(self.bookfile_xml)

    def test_fields_sql(self):
        self.dataframe_fields_control(self.rep.df_accounts, self.account_fields, 'df_account sql')
        self.dataframe_fields_control(self.rep.df_commodities, self.comm_fields, 'df_commodities sql')
        self.dataframe_fields_control(self.rep.df_transactions, self.tr_fields, 'df_transactions sql')
        self.dataframe_fields_control(self.rep.df_prices, self.price_fields, 'df_prices sql')
        self.dataframe_fields_control(self.rep.df_splits, self.split_fields, 'df_splits sql')

    # def test_fields_xml(self):
    #     self.dataframe_fields_control(self.rep_xml.df_accounts, self.account_fields, 'df_account xml')
    #     self.dataframe_fields_control(self.rep_xml.df_commodities, self.comm_fields, 'df_commodities xml')
    #     self.dataframe_fields_control(self.rep_xml.df_transactions, self.tr_fields, 'df_transactions xml')
    #     self.dataframe_fields_control(self.rep_xml.df_prices, self.price_fields, 'df_prices xml')
    #     self.dataframe_fields_control(self.rep_xml.df_splits, self.split_fields, 'df_splits xml')

    def dataframe_fields_control(self, df, etalon_fields, df_name):
        cols = df.columns.values.tolist()
        for field in etalon_fields:
            self.assertIn(field, cols, 'DataFrame {} contain field {}'.format(df_name, field))

    # def test_prices_sql(self):
    #     filename = 'U:/test_data/prices.pkl'
    #     df = self.rep.group_prices_by_period(from_date=self.from_date, to_date=self.to_date)
    #     df_etalon = pandas.read_pickle(filename)
    #     assert_frame_equal(df, df_etalon, check_like=True, obj='Group Prices')

    def test_balance_sql(self):
        filename = 'U:/test_data/assets.pkl'
        df = self.rep.balance_by_period(from_date=self.from_date, to_date=self.to_date)
        df_etalon = pandas.read_pickle(filename)
        assert_frame_equal(df, df_etalon, check_like=True, obj='Group assets')

    def test_turnover_expense_sql(self):
        filename = 'U:/test_data/expense.pkl'
        df = self.rep.turnover_by_period(from_date=self.from_date, to_date=self.to_date, account_type=RepBuilder.EXPENSE)
        df_etalon = pandas.read_pickle(filename)
        assert_frame_equal(df, df_etalon, check_like=True, obj='Group expenses')

    def test_turnover_income_sql(self):
        filename = 'U:/test_data/income.pkl'
        df = self.rep.turnover_by_period(from_date=self.from_date, to_date=self.to_date, account_type=RepBuilder.INCOME)
        df_etalon = pandas.read_pickle(filename)
        assert_frame_equal(df, df_etalon, check_like=True, obj='Group income')


class SQLDataTest(unittest.TestCase, BaseDataTest):

    bookfile = "u:/sqllite_book/real-2017-01-26.gnucash"

    def __init__(self, *args, **kwargs):
        super(SQLDataTest, self).__init__(*args, **kwargs)
        self.rep.open_book_sql(self.bookfile, open_if_lock=True)


class XMLDataTest(unittest.TestCase, BaseDataTest):

    bookfile_xml = 'U:/xml_book/GnuCash-base.gnucash'

    def __init__(self, *args, **kwargs):
        super(XMLDataTest, self).__init__(*args, **kwargs)
        self.rep.open_book_xml(self.bookfile_xml)

# def suite():
#     suite = unittest.TestSuite()
#     suite.addTest(XMLDataTest)
#     suite.addTest(SQLDataTest)
#     return suite

if __name__ == '__main__':
    # suite()
    unittest.main()
