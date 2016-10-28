import argparse
import datetime
import gcreports.repbuilder as repbuilder


rep = repbuilder.RepBuilder()

rep.open_book("u:/gnucash_book/test.gnucash")

# print(rep.root_account_guid)q
from_date = datetime.date(2016,1,1)
to_date = datetime.date(2016,12,31)
df = rep.group_by_period(from_date=from_date, to_date=to_date, account_type='INCOME')
df.to_excel('test2.xlsx')

print(df)