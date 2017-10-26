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







if __name__  == "__main__":
    filename = "c:/Temp/andrey/prog/gnucashreport/src/test/data/xirr-test-sql.gnucash"
    book = GnuCashSqlLiteBook()
    book.open_book(filename)

    # df = pandas.DataFrame(columns={'guid', 'name'})
    # df.append()

    print(book.df_accounts)

