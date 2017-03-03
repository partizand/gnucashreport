import argparse
import datetime
import os
import time
import pandas
from gnucashreport.gnucashdata import GNUCashData
from xlsxwriter.utility import xl_rowcol_to_cell

# from gnucashreport.gnucashreport import GNUCashReport
import gnucashreport
from gnucashreport.margins import Margins
# from gnucashreport.xlsxreport import OpenpyxlReport
from gnucashreport.utils import dataframe_to_excel
from gnucashreport.xlsxreport import XLSXReport

bookfile_sql = 'v:/gnucash-base/sqlite/GnuCash-base.gnucash'
bookfile_xml = 'v:/gnucash-base/xml/GnuCash-base.gnucash'


from_date = datetime.date(2016, 1, 1)
to_date = datetime.date(2016, 12, 31)

filename = 'v:/tables/ex-test.xlsx'
gcrep = gnucashreport.GNUCashReport()
# start_time_sql = time.time()
# rep.open_book_xml()
# rep.save_pickle()
# exit()
# print("Loading from sql --- %s seconds ---" % (time.time() - start_time_sql))

# start_time_pickle = time.time()
# rep.open_pickle()
# print("Loading from pickle all --- %s seconds ---" % (time.time() - start_time_pickle))

# start_time_pickle = time.time()
# rep.open_pickle()
# print("Loading from pickle 2016 --- %s seconds ---" % (time.time() - start_time_pickle))

# gcrep.open_book_sql(bookfile_sql)
gcrep._open_book_pickle(gcrep.dir_pickle)
# gcrep.open_book_file('T:/gnucash-stock/GnuCash-base.gnucash')

accounts = ['Активы:Долгосрочные активы:Ценные бумаги:Альфа-Директ:Аэрофлот а.о.']
df = gcrep._filter_for_xirr(accounts=accounts)
# from_date = datetime.date(2009, 1, 1)
# to_date = datetime.date(2016, 12, 31)
# dataframe_to_excel(df, 'aero')
df_income = gcrep._find_income_for_xirr(df, gcrep.INCOME)
dataframe_to_excel(df_income, 'aero-income')
