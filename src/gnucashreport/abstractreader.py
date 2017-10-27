import abc

class AbstractReader:

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.df_accounts = None
        self.df_transactions = None
        self.df_commodities = None
        self.df_splits = None
        self.df_prices = None

    @abc.abstractmethod
    def read_book(self, filename):
        return
