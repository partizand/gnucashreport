import datetime

from gnucashreport.buildreport import BuildReport
from gnucashreport.rawdata import RawData
from gnucashreport.xlsxreport import XLSXReport

bookfile_sql = 'v:/gnucash-base/sqlite/GnuCash-base.gnucash'
bookfile_xml = 'v:/gnucash-base/xml/GnuCash-base.gnucash'


# from_date = datetime.date(2015, 1, 1)
# to_date = datetime.date(2015, 12, 31)


out_filename = 'v:/tables/ex-test.xlsx'

# BuildReports
raw_data = RawData(bookfile_sql)
builder = BuildReport(raw_data)
reportset = builder.get_reportset_all(glevel=1)
outputer_excel = XLSXReport(out_filename)
outputer_excel.add_reportset(reportset)
outputer_excel.close()


