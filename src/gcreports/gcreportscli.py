import argparse

import gcreports.repbuilder as repbuilder


rep = repbuilder.RepBuilder()

rep.open_book("u:/gnucash_book/test.gnucash")

# print(rep.root_account_guid)q
df = rep.group_by_period(from_date='20160101', to_date='20160131')
df.to_excel('test.xlsx')
print(df)