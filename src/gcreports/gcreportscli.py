import argparse

import gcreports.repbuilder as repbuilder


rep = repbuilder.RepBuilder()

rep.open_book("u:/gnucash_book/test.gnucash")

# print(rep.root_account_guid)q
df = rep.get_balance('Активы:Резервы:ВТБ накопителный счет')
print(df)