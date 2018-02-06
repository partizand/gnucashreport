import pandas

from gnucashreport.gnucashbook import GNUCashBook
import gnucashreport.cols as cols
# from gnucashreport.gnucashbook import G

class GNUCashBookSQLite(GNUCashBook):

    def read_book(self, filename):

        # Open sqlite base
        uri = 'sqlite:///{}'.format(filename)
        # Read tables

        # commodities
        self.df_commodities = pandas.read_sql_table('commodities', uri)
        # set index
        self.df_commodities.set_index(cols.GUID, inplace=True)

        self.df_prices = pandas.read_sql_table('prices', uri)
        self.df_prices[cols.VALUE] = self.df_prices['value_num'] / self.df_prices['value_denom']
        # Convert sqlite date strings to date
        self.df_prices['date'] = pandas.to_datetime(self.df_prices['date'])

        # Transactions
        self.df_transactions = pandas.read_sql_table('transactions', uri)
        # Convert sqlite date strings to date
        self.df_transactions[cols.POST_DATE] = pandas.to_datetime(self.df_transactions[cols.POST_DATE])
        self.df_transactions[cols.ENTER_DATE] = pandas.to_datetime(self.df_transactions[cols.ENTER_DATE])
        # set index
        self.df_transactions.set_index(cols.GUID, inplace=True)


        self.df_splits = pandas.read_sql_table('splits', uri)
        self.df_splits[cols.VALUE] = self.df_splits['value_num'] / self.df_splits['value_denom']
        self.df_splits[cols.QUANTITY] = self.df_splits['quantity_num'] / self.df_splits['quantity_denom']
        # rename column to standard name
        self.df_splits.rename(columns={'tx_guid': cols.TRANSACTION_GUID}, inplace=True)

        # Read accounts notes from slots
        sql_text = """
            select
                accounts.*,
                slot_notes.string_val as notes
            from accounts
                left join (select obj_guid, name, string_val from slots where slots.name = 'notes') as slot_notes
                    on accounts.guid = slot_notes.obj_guid
            """
        self.df_accounts = pandas.read_sql(sql_text, uri)
        # set index
        self.df_accounts.set_index(cols.GUID, inplace=True)

        self._get_guid_rootaccount()






if __name__  == "__main__":
    filename = "c:/Temp/andrey/prog/gnucashreport/src/test/data/xirr-test-sql.gnucash"
    book = GNUCashBookSQLite()
    book.open_book(filename)

    # df = pandas.DataFrame(columns={'guid', 'name'})
    # df.append()

    print(book.df_accounts)

