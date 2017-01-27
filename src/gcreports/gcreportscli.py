import argparse
import datetime
import time
import gcreports.repbuilder as repbuilder


rep = repbuilder.RepBuilder()
from_date = datetime.date(2016,1,1)
to_date = datetime.date(2016,12,31)
# start_time = time.time()
rep.open_book("u:/sqllite_book/real-2017-01-26.gnucash")
# print("Loading from sqlite --- %s seconds ---" % (time.time() - start_time))
# rep.to_excel()

# start_time = time.time()
# rep.read_from_excel()
# print("Loading from excel --- %s seconds ---" % (time.time() - start_time))

# print(rep.df_prices)
# RUB GUID b2532663368050adfeb100f2887a56f8
# eur = rep.df_prices.loc[rep.df_prices['mnemonic'] == 'EUR', ['date', 'value']]
# print(eur)
#

pr = rep.group_prices_by_period(from_date=from_date, to_date=to_date)
rep.dataframe_to_excel(pr, "prices")
# print(pr.head())


# df = rep.group_accounts_by_period(from_date=from_date, to_date=to_date, account_type='EXPENSE')
# rep.dataframe_to_excel(df,"itog-expense")

#print(df)