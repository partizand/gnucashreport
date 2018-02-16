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

# Unknown multi transaction for xirr calculate. Transaction info: guid=3723d09d9b1d0a555bbc8bb6a57a1cb3. Date=2009-07-12 00:00:00. Descr=None
# Unknown multi transaction for xirr calculate. Transaction info: guid=3723d09d9b1d0a555bbc8bb6a57a1cb3. Date=2009-07-12 00:00:00. Descr=


# pie_book = piecash.open_book(bookfile_sql)

# transaction1 = pie_book.transactions()

# splits = pie_book.splits

# exit()
# BuildReports
raw_data = RawData(bookfile_sql)

print ('3723d09d9b1d0a555bbc8bb6a57a1cb3' == '3723d09d9b1d0a555bbc8bb6a57a1cb3')

df_splits = raw_data.df_splits[raw_data.df_splits[cols.TRANSACTION_GUID] == '3723d09d9b1d0a555bbc8bb6a57a1cb3']
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


