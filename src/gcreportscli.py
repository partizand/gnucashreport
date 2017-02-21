import argparse
import datetime
import os
import time
import pandas
from gnucashreport.gnucashdata import GNUCashData
from xlsxwriter.utility import xl_rowcol_to_cell

from gnucashreport.gnucashreport import GNUCashReport
from gnucashreport.margins import Margins
# from gnucashreport.xlsxreport import OpenpyxlReport
from gnucashreport.utils import dataframe_to_excel
from gnucashreport.xlsxreport import XLSXReport

bookfile_sql = 'v:/gnucash-base/sqlite/GnuCash-base.gnucash'
bookfile_xml = 'v:/gnucash-base/xml/GnuCash-base.gnucash'


from_date = datetime.date(2016, 1, 1)
to_date = datetime.date(2016, 12, 31)

filename = 'v:/tables/ex-test.xlsx'
gcrep = GNUCashReport()
# gcrep._detect_filebook_type(bookfile_xml)
# exit()
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
# gcrep.open_book_sql(bookfile_sql)

# rep.open_book_xml('U:/xml_book/GnuCash-base.gnucash')
# rep.save_pickle()
# rep.save_testdata()
# df = rep.balance_by_period(from_date=from_date, to_date=to_date, glevel=1)
# XLSXReport.dataframe_to_excel(df, 'asset-sql')
# exit()


# df = gcrep.turnover_by_period(from_date=from_date, to_date=to_date, account_type=GNUCashData.EXPENSE)
# gcrep.complex_report_excel(filename, from_date=from_date, to_date=to_date, period='M', glevel=1)
# exit()
from_date = datetime.date(2009, 1, 1)
to_date = datetime.date(2016, 12, 31)
# gcrep.inflation_excel(filename=filename, from_date=from_date, to_date=to_date, period='A', glevel=1)
# dataframe_to_excel(df, 'inf')
# rep._open_pickle()
# rep.profit_by_period(from_date=from_date, to_date=to_date)
# gcrep.complex_report_excel(filename, from_date=from_date, to_date=to_date, period='M', glevel=1)
gcrep.all_reports_excel(filename, glevel=1)
# gcrep.complex_report(from_date=from_date, to_date=to_date, period='M')
# gcrep.inflation()
# gcrep.complex_report_years(filename)
# exit()
# gcrep.
# print(gcrep.gcdata.tu)

# excel_report = XLSXReport(filename)
# excel_report.complex_report(rep, from_date=from_date, to_date=to_date)
# excel_report.save()
# rep.open_book_xml('U:/xml_book/GnuCash-base.gnucash')
# print("Loading from xml --- %s seconds ---" % (time.time() - start_time))
# rep.dataframe_to_excel(rep.df_accounts, 'acc-xml')
# start_time = time.time()
# rep.open_book("u:/sqllite_book/real-2017-01-26.gnucash", open_if_lock=True)
# print("Loading from sqlite --- %s seconds ---" % (time.time() - start_time))

# rep.to_excel()

# start_time = time.time()
# rep.read_from_excel()
# print("Loading from excel --- %s seconds ---" % (time.time() - start_time))

# print(rep.df_prices)
# RUB GUID b2532663368050adfeb100f2887a56f8
# eur = rep.df_prices.loc[rep.df_prices['mnemonic'] == 'EUR', ['date', 'value']]
# print(eur)
#
# filename='U:/test_data/prices.pkl'
# pr = rep.group_prices_by_period(from_date=from_date, to_date=to_date)
# pr.to_pickle(filename)
# pr = pr.reset_index()
# rep.dataframe_to_excel(pr, filename)

# pr_etalon = pandas.read_pickle(filename)

# pr_etalon = RepBuilder.read_dataframe_from_excel(filename)
# pr_etalon.set_index(['commodity_guid', 'date'], inplace=True)

# print(pr_etalon['date'].dtype)
# print(pr['date'].dtype)
# pr = pandas.DataFrame()
# print(pr_etalon.columns)
# print(pr_etalon.index)
# assert_frame_equal(pr, pr_etalon, check_like=True) #, check_names=False)
# a = pr_etalon == pr
# print(a)


# print(pr.head())

# acc = 'Активы:Текущие активы:Карта ВТБ'
# acc = 'Активы:Долгосрочные активы:Ценные бумаги:Промсвязь ИИС:Газпром а.о.'
# acc = 'Активы:Долгосрочные активы:Ценные бумаги:Промсвязь ИИС:МТС'
# acc = 'Активы:Долгосрочные активы:Ценные бумаги:Альфа-Директ:Югра Рентный Фонд'
# balance = rep.get_balance_stock(acc)
# print(balance)

# df = rep.balance_by_period(from_date=from_date, to_date=to_date, account_types=[GCReport.LIABILITY], glevel=1)
# rep.dataframe_to_excel(df, 'loans')
# filename='U:/test_data/loans.pkl'
# df.to_pickle(filename)
# pr = pr.reset_index()

# a = rep.get_balance(acc)
# print(a)

# df = rep.turnover_by_period(from_date=from_date, to_date=to_date, account_type=GCReport.INCOME)
# df = rep.complex_report(filename='complex', from_date=from_date, to_date=to_date)
# filename='U:/test_data/income.pkl'
# df.to_pickle(filename)
# rep.dataframe_to_excel(df, "itog-income", datetime_format='mmm yyyy')

# rep.dataframe_to_excel(rep.df_splits, 'all-splits')

#print(df)