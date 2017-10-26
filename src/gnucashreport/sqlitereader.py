import sqlite3

from gnucashreport.gnucashbook import GNUCashBook

import pandas

class GnuCashSqlLiteBook(GNUCashBook):

    def open_book(self, filename):
        try:
            # Open sqlite base
            uri = 'sqlite:///{}'.format(filename)
            self.df_accounts = pandas.read_sql_table('accounts', uri)

            conn = sqlite3.connect(filename)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Read accounts
            sql_text = "Select * from accounts"
            self.accounts = []
            for row in cursor.execute(sql_text):
                account = self.Account(name=row['name'],
                                       guid=row['guid'],
                                       actype=row['account_type'],
                                       description=row['description'],
                                       parent_guid=row['parent_guid'],
                                       commodity_guid=row['commodity_guid'],
                                       commodity_scu=row['commodity_scu'],
                                       hidden=row['hidden'],
                                       )
                self.accounts.append(account)

            # Read commodities
            sql_text = "Select * from commodities"
            self.accounts = []
            for row in cursor.execute(sql_text):
                commodity = self.Commodity(guid=row['guid'],
                                           name=row['mnemonic'],
                                           space=row['namespace'],
                                           )
                self.commodities.append(commodity)

            # Read prices
            sql_text = "Select * from prices"
            self.accounts = []
            for row in cursor.execute(sql_text):
                price = self.Price(guid=row['guid'],
                                       commodity_guid=row['commodity_guid'],
                                       currency_guid=row['currency_guid'],
                                       date=row['date'],  # TODO: this is text, not date
                                       source=row['source'],
                                       price_type=row['type'],
                                       value=row['value_num'],
                                           )
                self.prices.append(price)

        except sqlite3.DatabaseError as err:
            print("Sqlite database error: {}".format(err))
        else:
            conn.close()

if __name__  == "__main__":
    filename = "c:/Temp/andrey/prog/gnucashreport/src/test/data/xirr-test-sql.gnucash"
    book = GnuCashSqlLiteBook()
    book.open_book(filename)

    # df = pandas.DataFrame(columns={'guid', 'name'})
    # df.append()

    print(book.df_accounts)

