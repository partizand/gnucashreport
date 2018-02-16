import datetime

import piecash
from gnucashreport import cols

from gnucashreport.buildreport import BuildReport
from gnucashreport.rawdata import RawData
from gnucashreport.xlsxreport import XLSXReport

bookfile_sql = 'v:/gnucash-base/sqlite/GnuCash-base.gnucash'
bookfile_xml = 'v:/gnucash-base/xml/GnuCash-base.gnucash'


# from_date = datetime.date(2015, 1, 1)
# to_date = datetime.date(2015, 12, 31)


out_filename = 'v:/tables/ex-test.xlsx'


# pie_book = piecash.open_book(bookfile_sql)

# transaction1 = pie_book.transactions()

# splits = pie_book.splits

# exit()
# BuildReports
raw_data = RawData(bookfile_sql)


# account_guids = df_splits[cols.ACCOUNT_GUID]
# df_accounts = raw_data.df_accounts[raw_data.df_accounts[cols.GUID] in account_guids]
with XLSXReport('v:/tables/df_splits.xlsx') as outputer_excel:
# outputer_excel = XLSXReport('v:/tables/df_splits.xlsx')
    outputer_excel.add_dataframe(df_splits, 'df_splits')
    # outputer_excel.close()

print(df_splits)
exit()
builder = BuildReport(raw_data)
reportset = builder.get_reportset_all(glevel=1)
outputer_excel = XLSXReport(out_filename)
outputer_excel.add_reportset(reportset)
outputer_excel.close()


