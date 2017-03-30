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


# from_date = datetime.date(2016, 1, 1)
# to_date = datetime.date(2016, 1, 1)
# idx = pandas.date_range(from_date, to_date, freq='D')
# print(idx)
# exit()

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

on_date = datetime.date(2012, 9, 1)
# dataframe_to_excel(gcrep.df_splits, 'all-splits')
# exit()

# df = gcrep._splits_currency_calc()
# dataframe_to_excel(df, 'splits_cur')
# exit()

accounts = ['Активы:Долгосрочные активы:Ценные бумаги:Альфа-Директ:Аэрофлот а.о.']

# df = gcrep.balance_on_date(on_date=on_date, account_names=accounts)
# dataframe_to_excel(df, 'bal_on_date')
# exit()
# to_date = datetime.date(2016, 1, 1)
df = gcrep._filter_for_xirr(accounts=accounts, to_date=on_date) #balance_to_currency(accounts=accounts)
dataframe_to_excel(df, 'aero-currency')
# accounts = ['Активы:Текущие активы:Наличные Евро']
accounts = ['Активы:Текущие активы:Наличные Евро']
df = gcrep._filter_for_xirr(accounts=accounts) #balance_to_currency(accounts=accounts)
dataframe_to_excel(df, 'euro-currency')
exit()


# df = gcrep._filter_for_xirr(accounts=accounts)
# dataframe_to_excel(df, 'aero')

prices = gcrep.balance_to_currency(accounts=accounts)
dataframe_to_excel(prices, 'euro-currency')
exit()

df_income = gcrep._find_income_for_xirr(df, gcrep.INCOME)
dataframe_to_excel(df_income, 'aero-income')
