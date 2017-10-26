import pandas

from gnucashreport.sqlitereader import SQLiteReader


class GNUCashBook:
    """
    Read GnuCash book tables into pandas dataframes
    df_accounts
    df_splits
    etc
    """

    def __init__(self):
        self.df_accounts = pandas.DataFrame()
        self.df_transactions = pandas.DataFrame()
        self.df_commodities = pandas.DataFrame()
        self.df_splits = pandas.DataFrame()
        self.df_prices = pandas.DataFrame()

        self.book_name = None

        self.root_account_guid = None

    def read_file(self, filename):
        sqlbook = SQLiteReader()
        sqlbook.read_sqlite_book(filename)

        self.df_accounts = sqlbook.df_accounts











