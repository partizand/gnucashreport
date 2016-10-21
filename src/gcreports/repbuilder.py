import piecash
import pandas
from operator import attrgetter


class RepBuilder:
    """
    DataFrame implementation of GnuCash database tables
    """
    df_accounts = None
    df_transactions = None
    df_commodities = None
    df_splits = None
    df_prices = None

    root_account_guid = None

    def __init__(self):
        pass

    def open_book(self, sqlite_file):
        with piecash.open_book(sqlite_file) as gnucash_book:

            # Accounts

            # Get from piecash
            self.root_account_guid = gnucash_book.root_account.guid
            t_accounts = gnucash_book.session.query(piecash.Account).all()
            # fields accounts
            fields = ["guid", "name", "type",
                      "commodity_guid", "commodity_scu", "non_std_scu",
                      "parent_guid", "code", "description"]
            self.df_accounts = self.object_to_dataframe(t_accounts, fields)
            # rename to real base name of field from piecash name
            self.df_accounts.rename(columns={'type': 'account_type'}, inplace=True)

            # commodities

            # preload list of commodities
            t_commodities = gnucash_book.session.query(piecash.Commodity).filter(
                 piecash.Commodity.namespace != "template").all()
            fields = ["guid", "namespace", "mnemonic",
                      "fullname", "cusip", "fraction",
                      "quote_flag", "quote_source", "quote_tz"]
            self.df_commodities = self.object_to_dataframe(t_commodities, fields)

            # Transactions

            # Get from piecash
            t_transactions = gnucash_book.session.query(piecash.Transaction).all()
            # fields transactions
            fields = ["guid", "currency_guid", "num",
                      "post_date", "enter_date", "description"]
            self.df_transactions = self.object_to_dataframe(t_transactions, fields)

            # Splits

            # load all splits
            t_splits = gnucash_book.session.query(piecash.Split).all()
            # Some fields not correspond to real names in DB
            fields = ["guid", "transaction_guid", "account_guid",
                      "memo", "action", "reconcile_state",
                      "reconcile_date", "value",
                      "quantity", "lot_guid"]
            self.df_splits = self.object_to_dataframe(t_splits, fields)

            # Prices

            # Get from piecash
            t_prices = gnucash_book.session.query(piecash.Price).all()
            # Some fields not correspond to real names in DB
            fields = ["guid", "commodity_guid", "currency_guid",
                      "date", "source", "type", "value"]
            self.df_prices = self.object_to_dataframe(t_prices, fields)

    @staticmethod
    def object_to_dataframe(pieobject, fields):

        # build dataframe
        fields_getter = [attrgetter(fld) for fld in fields]
        df_obj = pandas.DataFrame([[fg(sp) for fg in fields_getter]
                                             for sp in pieobject], columns=fields)

        # self.df_accounts = pandas.DataFrame(accounts)
        df_obj.set_index(fields[0], inplace=True)
        return df_obj



