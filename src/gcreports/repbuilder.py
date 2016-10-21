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
    # Merged splits and transactions
    # df_m_splits = None

    root_account_guid = None

    def __init__(self):
        pass

    def get_split(self, account_name):
        return self.df_splits[(self.df_splits['fullname'] == account_name)]
        # return self.df_splits.loc['fullname' == account_name]

    def get_balance(self, account_name):
        return self.df_splits.loc[self.df_splits['fullname'] == account_name, 'value'].sum()
    def open_book(self, sqlite_file):
        with piecash.open_book(sqlite_file) as gnucash_book:

            # Read data tables in dataframes

            # Accounts

            # Get from piecash
            self.root_account_guid = gnucash_book.root_account.guid
            t_accounts = gnucash_book.session.query(piecash.Account).all()
            # fields accounts
            fields = ["guid", "name", "type", "placeholder",
                      "commodity_guid", "commodity_scu",
                      "parent_guid", "description", "hidden"]
            self.df_accounts = self.object_to_dataframe(t_accounts, fields)
            # rename to real base name of field from piecash name
            self.df_accounts.rename(columns={'type': 'account_type'}, inplace=True)
            # Get fullname of accounts
            self.df_accounts['fullname'] = self.df_accounts.index.map(self._get_fullname_account)

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
                      "post_date", "description"]
            self.df_transactions = self.object_to_dataframe(t_transactions, fields)

            # Splits

            # load all splits
            t_splits = gnucash_book.session.query(piecash.Split).all()
            # Some fields not correspond to real names in DB
            fields = ["guid", "transaction_guid", "account_guid",
                      "memo", "action", "reconcile_state",
                      "value",
                      "quantity", "lot_guid"]
            self.df_splits = self.object_to_dataframe(t_splits, fields)

            # Prices

            # Get from piecash
            t_prices = gnucash_book.session.query(piecash.Price).all()
            # Some fields not correspond to real names in DB
            fields = ["guid", "commodity_guid", "currency_guid",
                      "date", "source", "type", "value"]
            self.df_prices = self.object_to_dataframe(t_prices, fields)

            # merge splits and accounts
            df_acc_splits = pandas.merge(self.df_splits, self.df_accounts, left_on='account_guid',
                                         right_index=True)
            df_acc_splits.rename(columns={'description': 'description_account'}, inplace=True)
            # merge splits and accounts with transactions
            self.df_splits = pandas.merge(df_acc_splits, self.df_transactions, left_on='transaction_guid',
                                            right_index=True)



            # self._base_operation()

    # def _base_operation(self):
    #     """
    #     Some base operation on dataframes after get data
    #     :return:
    #     """




    def _get_fullname_account(self, account_guid):
        """
        Get fullname account by guid. Return semicolon path Expenses:Food:...
        :param account_guid:
        :return:
        """
        if account_guid == self.root_account_guid:
            return 'root'
        fullname = self.df_accounts.ix[account_guid]['name']
        parent_guid = self.df_accounts.ix[account_guid]['parent_guid']
        if parent_guid in self.df_accounts.index:
            if parent_guid == self.root_account_guid:
                return fullname
            else:
                return self._get_fullname_account(parent_guid) + ':' + fullname
        else:
            return 'error'

    @staticmethod
    def object_to_dataframe(pieobject, fields):
        """
        Преобразовывае объект piecash в DataFrame с заданными полями
        :param pieobject:
        :param fields:
        :return:
        """
        # build dataframe
        fields_getter = [attrgetter(fld) for fld in fields]
        df_obj = pandas.DataFrame([[fg(sp) for fg in fields_getter]
                                             for sp in pieobject], columns=fields)
        df_obj.set_index(fields[0], inplace=True)
        return df_obj



