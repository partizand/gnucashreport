import pandas

import abc

from gnucashreport.gnucashbooksqlite import GNUCashBookSQLite
from gnucashreport.gnucashbookxml import GNUCashBookXML
import gnucashreport.cols as cols


BOOKTYPE_XML = 'xml'
BOOKTYPE_SQLITE = 'sqlite'


def get_gnucashbook_type(filename):
    """
    Detect type of gnucash file
    sqlite or xml
    return BOOKTYPE_XML or BOOKTYPE_SQLITE
    :param filename:
    :return:
    """
    with open(filename, "rb") as f:
        bytes = f.read(16)
    if bytes == b'SQLite format 3\x00':
        return BOOKTYPE_SQLITE
    else:
        return BOOKTYPE_XML

class GNUCashBook:
    """
    Read GnuCash book tables into pandas dataframes
    df_accounts
    df_splits
    etc
    """

    __metaclass__ = abc.ABCMeta

    # GnuCash account types
    CASH = 'CASH'
    BANK = 'BANK'
    ASSET = 'ASSET'
    STOCK = 'STOCK'
    MUTUAL = 'MUTUAL'
    INCOME = 'INCOME'
    EXPENSE = 'EXPENSE'
    EQUITY = 'EQUITY'
    LIABILITY = 'LIABILITY'
    ROOT = 'ROOT'
    # GNUCash all account assets types
    ALL_ASSET_TYPES = [CASH, BANK, ASSET, STOCK, MUTUAL]

    # All account types for calc yield by xirr
    ALL_XIRR_TYPES = [BANK, ASSET, STOCK, MUTUAL, LIABILITY]
    ASSET_XIRR_TYPES = [BANK, ASSET, LIABILITY]
    STOCK_XIRR_TYPES = [STOCK, MUTUAL]
    INCEXP_XIRR_TYPES = [INCOME, EXPENSE]

    def __init__(self):

        # self.book = None

        self.df_accounts = pandas.DataFrame()
        self.df_transactions = pandas.DataFrame()
        self.df_commodities = pandas.DataFrame()
        self.df_splits = pandas.DataFrame()
        self.df_prices = pandas.DataFrame()

        # self.book_name = None

        self.root_account_guid = None

    @abc.abstractmethod
    def read_book(self, filename):
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
        # with open(filename, "rb") as f:
        #     bytes = f.read(16)
        # if bytes == b'SQLite format 3\x00':
        #     self.book = GNUCashBookSQLite()
        #     # self.open_book_sql(sqlite_file=filename, readonly=readonly, open_if_lock=open_if_lock)
        # else:
        #     self.book = GNUCashBookXML()
        #
        # self.book.read_book(filename)

        # self.df_accounts = self.book.df_accounts
        # self.df_commodities = self.book.df_commodities
        # self.df_prices = self.book.df_prices
        # self.df_transactions = self.book.df_transactions
        # self.df_splits = self.book.df_splits
        return


    def _get_guid_rootaccount(self):
        """
        Get root account guid from df_accounts
        :return:
        """
        df_root = self.df_accounts[(self.df_accounts[cols.ACCOUNT_TYPE] == self.ROOT) &
                                   (self.df_accounts[cols.SHORTNAME] == 'Root Account')]
        self.root_account_guid = df_root.index.values[0]













