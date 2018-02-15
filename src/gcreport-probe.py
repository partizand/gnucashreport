import argparse
import datetime
import os
import time
import pandas
from decimal import Decimal

from dateutil import parser, tz

import re

from gnucashreport import formatreport
from gnucashreport.formatreport import _FormatBalance, FormatIncome, FormatAssets
from gnucashreport.rawdata import RawData
from xlsxwriter.utility import xl_rowcol_to_cell

# from gnucashreport.gnucashreport import GNUCashReport
import gnucashreport
from gnucashreport.margins import Margins
# from gnucashreport.xlsxreport import OpenpyxlReport
from gnucashreport.utils import dataframe_to_excel
from gnucashreport.xlsxreport import XLSXReport




bookfile_sql = 'v:/gnucash-base/sqlite/GnuCash-base.gnucash'
bookfile_xml = 'v:/gnucash-base/xml/GnuCash-base.gnucash'


from_date = datetime.date(2015, 1, 1)

to_date = datetime.date(2015, 12, 31)


out_filename = 'v:/tables/ex-test.xlsx'
gcrep = gnucashreport.GCReport()

