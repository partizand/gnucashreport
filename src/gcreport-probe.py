import argparse
import datetime
import os
import time
import pandas
from decimal import Decimal

import re

from gnucashreport.gnucashdata import GNUCashData
from xlsxwriter.utility import xl_rowcol_to_cell

# from gnucashreport.gnucashreport import GNUCashReport
import gnucashreport
from gnucashreport.margins import Margins
# from gnucashreport.xlsxreport import OpenpyxlReport
from gnucashreport.utils import dataframe_to_excel
from gnucashreport.xlsxreport import XLSXReport



# regex test
my_str = u'ucourt métrage pour kino session volume 18\nThème: O sombres héros\nContraintes: sous titrés\nAuthor: nicoalabdou\nTags: wakatanka productions court métrage kino session humour cantat bertrand noir désir sombres héros mer medine marie trintignant femme droit des femmes nicoalabdou pute soumise\nPosted: 06 June 2009\nRating: 1.3\nVotes: 3'
my_str = 'CS \nID=123\nHD: CT\nNE: HI THERE'
x = 'CS ID=123 HD=CT NE="HI THERE"'
my_tags = ['\S+'] # gets all tags
# my_tags = ['Tags','Author','Posted'] # selected tags
regex = re.compile(r'''
    \n                     # all key-value pairs are on separate lines
    (                      # start group to return
       (?:{0}):            # placeholder for tags to detect '\S+' == all
        \s                 # the space between ':' and value
       .*                  # the value
    )                      # end group to return
    '''.format('|'.join(my_tags)), re.VERBOSE)

regex2 = re.compile(r'''
     \n                    # all key-value pairs are on separate lines
    (                      # start group to return
       (?:{0})=            # placeholder for tags to detect '\S+' == all
                         # the space between ':' and value
       .*                  # the value
    )                      # end group to return
    '''.format('|'.join(my_tags)), re.VERBOSE)

# other = re.findall("""\w+="[^"]*"|\w+='[^']*'|\w+=\w+|\w+""", x)
# other = re.findall("""\w+="[^"]*"|\w+='[^']*'|\w+=\w+""", x)
# other = list(map(''.join,re.findall("""(\w+=)"([^"]*)"|(\w+=)'([^']*)'|(\w+=\w+)|(\w+)""", x)))
other = list(map(''.join, re.findall("""(\w+=)"([^"]*)"|(\w+=)'([^']*)'|(\w+=\w+)""", x)))
# other = re.findall("""(\w+=)"([^"]*)"|(\w+=)'([^']*)'|(\w+=\w+)""", x)
# dict1 = {map(lambda x1: dict(x1.split('=')), other)}
dict1 = dict(map(lambda x1: x1.split('='), other))
print(dict1)
print(dict1['ID'])
exit()

textin ="LexicalReordering0= -1.88359 0 -1.6864 -2.34184 -3.29584 0 Distortion0= -4 LM0= -85.3898 WordPenalty0= -13 PhrasePenalty0= 11 TranslationModel0= -6.79761 -3.06898 -8.90342 -4.35544"
pat = re.compile(r'''([^\s=]+)=\s*((?:[^\s=]+(?:\s|$))*)''')
c = pat.findall(x)
# print(c)
entries = dict((k, v) for k, v in c)
# print(entries)
# print(entries['ID'])
exit()

# a = regex.sub('',my_str) # return my_str without matching key-vaue lines
# b =  regex.findall(my_str) # return matched key-value lines
b =  regex2.findall(my_str) # return matched key-value lines

# print(a)
print(b)
exit()

# end regex test


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

# gcrep.open_book_sql(bookfile_sql, open_if_lock=True)
# gcrep._open_book_pickle(gcrep.dir_pickle)
# gcrep.open_book_file(bookfile_xml)
gcrep.open_book_file('c:/Temp/andrey/prog/gnucashreport/src/test/data/xirr-test.gnucash')
on_date = datetime.date(2016, 12, 31)
df = gcrep.balance_on_date(on_date=on_date)
dataframe_to_excel(df, 'balance')
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
# account_guid = gcrep._get_account_guid(account)
# xirr = gcrep._xirr_calc(account_guid)
# print(xirr)
account = 'Активы:Долгосрочные активы:Депозиты'
df_return = gcrep.yield_calc(account_name=account)
dataframe_to_excel(df_return, 'df_return_depo2')

account = 'Активы:Долгосрочные активы:Ценные бумаги:Альфа-Директ'
df_return = gcrep.yield_calc(account_name=account)
dataframe_to_excel(df_return, 'df_return_alfa2')
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
