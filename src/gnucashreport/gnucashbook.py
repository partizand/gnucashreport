import pandas

from gnucashreport.sqlitereader import SQLiteReader
from gnucashreport.gcxmlreader import GNUCashXMLBook

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

    def open_book_file(self, filename):
        """
        Open GnuCash database file. Autodetect type: sqlite or xml
        :param filename:
        :param readonly: only for sqlite
        :param open_if_lock: only for sqlite
        :return:
        """
        # Detect version - sql or xml

        # Every valid SQLite database file begins with the following 16 bytes (in hex):
        #  53 51 4c 69 74 65 20 66 6f 72 6d 61 74 20 33 00.
        # This byte sequence corresponds to the UTF-8 string "SQLite format 3"
        # including the nul terminator character at the end.
        # Read sqllite signature
        with open(filename, "rb") as f:
            bytes = f.read(16)
        if bytes == b'SQLite format 3\x00':
            book = SQLiteReader()
            # self.open_book_sql(sqlite_file=filename, readonly=readonly, open_if_lock=open_if_lock)
        else:
            book = GNUCashXMLBook()

        book.read_book(filename)

        self.df_accounts = book.df_accounts

    def _get_guid_rootaccount(self):
        """
        Get root account guid from df_accounts
        :return:
        """
        df_root = self.df_accounts[(self.df_accounts[cols.ACCOUNT_TYPE] == self.ROOT) &
                                   (self.df_accounts[cols.SHORTNAME] == 'Root Account')]
        self.root_account_guid = df_root.index.values[0]













