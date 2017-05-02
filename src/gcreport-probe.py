import argparse
import datetime
import os
import time
import pandas
from decimal import Decimal

import re

from gnucashreport.formatreport import FormatBalance, FormatIncome, FormatAssets
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

# a = 0.14
# print('{:0.2f}%'.format(a))
# exit()

# from_date = datetime.date(2016, 1, 1)
# to_date = datetime.date(2016, 1, 1)
# idx = pandas.date_range(from_date, to_date, freq='D')
# print(idx)
# exit()

filename = 'v:/tables/ex-test.xlsx'
gcrep = gnucashreport.GCReport()



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

gcrep.open_book_sql(bookfile_sql, open_if_lock=True)
# gcrep._open_book_pickle(gcrep.dir_pickle)
# gcrep.open_book_file(bookfile_xml)
# gcrep.open_book_file('test/data/xirr-test.gnucash')

# exit()
# on_date = datetime.date(2016, 12, 31)
# df = gcrep.balance_on_date(on_date=on_date)
# dataframe_to_excel(gcrep.df_splits, 'splits')
# gcrep.returns_report_excel('v:/tables/returns.xlsx', from_date=from_date, to_date=to_date)
# gcrep.returns_report_excel('v:/tables/returns.xlsx')
gcrep.all_reports_excel('v:/tables/all.xlsx')

exit()



# dataframe_to_excel(gcrep.df_splits, 'all-splits')
# exit()

# df = gcrep._splits_currency_calc()
# dataframe_to_excel(gcrep.df_splits, 'splits')
# exit()

# account = 'Активы:Долгосрочные активы:Ценные бумаги:Альфа-Директ:Аэрофлот а.о.'
# account = 'Активы:Долгосрочные активы:Ценные бумаги:Альфа-Директ'

# account = 'Активы:Долгосрочные активы:ПИФы:ТД Илья Муромец'
# account = 'Активы:Долгосрочные активы:ПИФы'
account = 'Долги:Кредит ВТБ24 (потреб)'
# account = 'Активы:Долгосрочные активы:Депозиты'
df_return = gcrep.yield_calc(account_name=account)
# df_return = gcrep.yield_calc()
# dataframe_to_excel(df_return, 'df_depo')
exit()
# account = 'Активы:Долгосрочные активы:Ценные бумаги:Альфа-Директ'
account = 'Активы:Долгосрочные активы:Ценные бумаги:Альфа-Директ'
# df_return = gcrep.yield_calc(account_name=account)
df_return = gcrep.yield_calc()
dataframe_to_excel(df_return, 'df_return_all')
exit()



# df = gcrep.balance_on_date(on_date=on_date, account_names=accounts)
# dataframe_to_excel(df, 'bal_on_date')
# exit()
# to_date = datetime.date(2016, 1, 1)
# df = gcrep._filter_for_xirr(accounts=accounts)
df = gcrep._add_xirr_info()
df = gcrep._xirr_calc(account_guids=accounts)
dataframe_to_excel(df, 'aero-total')
exit()

# accounts = ['Активы:Текущие активы:Наличные Евро']
# df = gcrep._filter_for_xirr(accounts=accounts)
# dataframe_to_excel(df, 'euro-currency')
# exit()

df_income = gcrep._find_income_for_xirr(df, gcrep.INCOME)
dataframe_to_excel(df_income, 'aero-income')

df_income = gcrep._find_income_for_xirr(df, gcrep.EXPENSE)
dataframe_to_excel(df_income, 'aero-expense')
