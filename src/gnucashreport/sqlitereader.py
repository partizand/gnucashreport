import pandas

from gnucashreport.abstractreader import AbstractReader

class SQLiteReader(AbstractReader):



    def read_book(self, filename):

        # Open sqlite base
        uri = 'sqlite:///{}'.format(filename)
        # Read tables
        self.df_accounts = pandas.read_sql_table('accounts', uri)
        self.df_commodities = pandas.read_sql_table('commodities', uri)
        self.df_prices = pandas.read_sql_table('prices', uri)
        self.df_transactions = pandas.read_sql_table('transactions', uri)
        self.df_splits = pandas.read_sql_table('splits', uri)

# Select all accounts and this notes
# select
#     accounts.*,
#     slot_notes.string_val as notes
#
# from accounts
# left join (select obj_guid, name, string_val from slots where slots.name = 'notes') as slot_notes
#     on accounts.guid = slot_notes.obj_guid






if __name__  == "__main__":
    filename = "c:/Temp/andrey/prog/gnucashreport/src/test/data/xirr-test-sql.gnucash"
    book = GnuCashSqlLiteBook()
    book.open_book(filename)

    # df = pandas.DataFrame(columns={'guid', 'name'})
    # df.append()

    print(book.df_accounts)

