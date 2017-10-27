import pandas

from gnucashreport.abstractreader import AbstractReader
from gnucashreport.gnucashbook import GNUCashBook
import gnucashreport.cols as cols


class GNUCashBookSQLite(GNUCashBook):



    def read_book(self, filename):

        # Open sqlite base
        uri = 'sqlite:///{}'.format(filename)
        # Read tables
        # self.df_accounts = pandas.read_sql_table('accounts', uri)
        self.df_commodities = pandas.read_sql_table('commodities', uri)

        self.df_prices = pandas.read_sql_table('prices', uri)
        self.df_prices[cols.VALUE] = self.df_prices['value_num'] / self.df_prices['value_denom']

        self.df_transactions = pandas.read_sql_table('transactions', uri)

        self.df_splits = pandas.read_sql_table('splits', uri)
        self.df_splits[cols.VALUE] = self.df_splits['value_num'] / self.df_splits['value_denom']
        self.df_splits[cols.QUANTITY] = self.df_splits['quantity_num'] / self.df_splits['quantity_denom']

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

        self._get_guid_rootaccount()






if __name__  == "__main__":
    filename = "c:/Temp/andrey/prog/gnucashreport/src/test/data/xirr-test-sql.gnucash"
    book = GNUCashBookSQLite()
    book.open_book(filename)

    # df = pandas.DataFrame(columns={'guid', 'name'})
    # df.append()

    print(book.df_accounts)

