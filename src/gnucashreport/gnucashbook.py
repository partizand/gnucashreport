import pandas

import abc

import time

import gnucashreport.cols as cols


class GNUCashBook:
    """
    Read GnuCash book tables into pandas dataframes
    df_accounts
    df_splits
    etc
    """

    __metaclass__ = abc.ABCMeta

    # book types
    BOOKTYPE_XML = 'xml'
    BOOKTYPE_SQLITE = 'sqlite'

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

    def __init__(self, timeing=False):

        # self.book = None

        self.df_accounts = pandas.DataFrame()
        self.df_transactions = pandas.DataFrame()
        self.df_commodities = pandas.DataFrame()
        self.df_splits = pandas.DataFrame()
        self.df_prices = pandas.DataFrame()

        # self.book_name = None

        self.root_account_guid = None

        self.timeing = timeing
        self._startTime = None

    def _start_timing(self, message=None):
        if self.timeing:
            self._startTime = time.time()
        if message:
            print(message)

    def _end_timing(self, message=''):
        if self.timeing:
            print("{}: {:.3f} sec".format(message, time.time() - self._startTime))


    @abc.abstractmethod
    def read_book(self, filename):
        """
        Open GnuCash database file. Autodetect type: sqlite or xml
        :param filename:
        :param readonly: only for sqlite
        :param open_if_lock: only for sqlite
        :return:
        """

        return

    @staticmethod
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
            return GNUCashBook.BOOKTYPE_SQLITE
        else:
            return GNUCashBook.BOOKTYPE_XML

    def _get_guid_rootaccount(self):
        """
        Get root account guid from df_accounts
        :return:
        """
        df_root = self.df_accounts[(self.df_accounts[cols.ACCOUNT_TYPE] == self.ROOT) &
                                   (self.df_accounts[cols.SHORTNAME] == 'Root Account')]
        self.root_account_guid = df_root.index.values[0]













