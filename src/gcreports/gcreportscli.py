import argparse
import datetime
import gcreports.repbuilder as repbuilder


rep = repbuilder.RepBuilder()
from_date = datetime.date(2016,1,1)
to_date = datetime.date(2016,12,31)
# rep.open_book("u:/gnucash_book/test.gnucash")
# rep.save2excel()
rep.read_from_excel()
print(rep.df_prices)
# RUB GUID b2532663368050adfeb100f2887a56f8
# eur = rep.df_prices.loc[rep.df_prices['mnemonic'] == 'EUR', ['date', 'value']]
# print(eur)
#
# pr = rep.group_prices_by_period(from_date=from_date, to_date=to_date)
# print(pr.head())


# df = rep.group_accounts_by_period(from_date=from_date, to_date=to_date, account_type='INCOME')
# df.to_excel('test2.xlsx')

#print(df)