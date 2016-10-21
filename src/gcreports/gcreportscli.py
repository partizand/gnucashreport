import argparse

import gcreports.repbuilder as repbuilder


rep = repbuilder.RepBuilder()

rep.open_book("u:/gnucash_book/test.gnucash")

# print(rep.root_account_guid)q

print(rep.df_m_splits.head())