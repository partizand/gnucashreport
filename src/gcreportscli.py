import argparse
import datetime
import os
import time
import pandas
from pandas.util.testing import assert_frame_equal
from gcreports.gcreport import GCReport



def complex_test():

    dir_excel = "U:/tables"
    filename = 'complex'
    datetime_format = 'mmm yyyy'

    sheet = 'Sheet1'



    if not filename.endswith('.xlsx'):
        filename = os.path.join(dir_excel, filename + ".xlsx")

    df_income = pandas.read_pickle('U:/test_data/income.pkl') #  self.turnover_by_period(from_date=from_date, to_date=to_date, period=period, account_type=self.INCOME)
    df_expense = pandas.read_pickle('U:/test_data/expense.pkl')# self.turnover_by_period(from_date=from_date, to_date=to_date, period=period, account_type=self.EXPENSE)

    # Добавить итоги (для теста)
    df_income = df_income.append(df_income.sum(), ignore_index=True)
    df_expense = df_expense.append(df_expense.sum(), ignore_index=True)

    # print(df_income)

    # df_income.to_pickle('u:/tables/inc-2016.pkl')

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pandas.ExcelWriter(filename, engine='xlsxwriter', datetime_format=datetime_format)
    # Get the xlsxwriter objects from the dataframe writer object.
    # workbook = writer.book
    # worksheet = writer.sheets[sheet]
    # worksheet = workbook.add_worksheet(sheet)



    # worksheet.write_blank(row=2, col=1, blank=None, cell_format=frmt_head)

    # Convert the dataframe to an XlsxWriter Excel object.
    income_start_row = 2
    df_income.to_excel(writer, sheet_name=sheet, startrow=income_start_row, header=False)
    income_height = len(df_income)
    income_itog_row = income_start_row + income_height - 1

    expense_start_row = income_start_row + income_height + 3
    expense_height = len(df_expense)
    expense_itog_row = expense_start_row + expense_height - 1
    df_expense.to_excel(writer, sheet_name=sheet, header=False, startrow=expense_start_row)

    # Get the xlsxwriter objects from the dataframe writer object.
    workbook = writer.book
    worksheet = writer.sheets[sheet]

    # Add a number format for cells with money.
    # frmt_money = workbook.add_format({'num_format': '$#,##0'})
    # frmt_money = workbook.add_format({'num_format': '# ##0,00 [$р.-419];[RED]-# ##0,00 [$р.-419]'})
    # frmt_money = workbook.add_format({'num_format': '# ##0,00 [$р.-419];[RED]-# ##0,00 [$р.-419]'})
    frmt_money = workbook.add_format()
    frmt_money.set_num_format(0x08)
    frmt_head_expense = workbook.add_format({'bold': True})
    frmt_head_expense.set_align('center')
    frmt_head_expense.set_bg_color('#FFFF00')
    frmt_income = workbook.add_format({'bold': True})
    frmt_income.set_align('center')
    frmt_income.set_bg_color('#00ff11')
    frmt_date = workbook.add_format()
    frmt_date.set_num_format('mmm yyyy')

    worksheet.write(income_start_row - 1, 0, 'ДОХОДЫ', frmt_income)
    worksheet.write(income_itog_row, 0, 'Итого доходы', frmt_income)
    worksheet.write(expense_start_row - 1, 0, 'Расходы', frmt_head_expense)
    worksheet.write(expense_itog_row, 0, 'Итого расходы', frmt_head_expense)
    # Ширина первой колонки
    # worksheet.set_column(0, 0, 25)
    worksheet.set_column(firstcol=0, lastcol=0, width=25)
    # Ширина остальных колонок
    col_count = len(df_income.columns)
    worksheet.set_column(firstcol=1, lastcol=col_count + 1, width=12, cell_format=frmt_money)

    # Формат итогов

    worksheet.conditional_format(first_row=income_itog_row, first_col=0,
                                 last_row=income_itog_row, last_col=col_count,
                                 options={'type': 'no_blanks', 'format': frmt_income})

    worksheet.conditional_format(first_row=income_itog_row, first_col=0,
                                 last_row=income_itog_row, last_col=col_count,
                                 options={'type': 'no_blanks', 'format': frmt_income})

    # Заголовок таблицы
    cols = df_income.columns.tolist()
    i = 1
    for col in cols:
        worksheet.write(0, i, col, frmt_date)
        i = i + 1


    # worksheet.conditional_format('A6:M6', {'type': 'no_blanks',
    #                                        'format': frmt_income})

    # worksheet.add_table(first_row=income_start_row, first_col=0,
    #                     last_row=income_start_row+income_height, last_col=col_count,
    #                     options={'autofilter':False, 'total_row': True})

    # worksheet.set_column(3, 3, cell_format=frmt_money)

    # set columns width
    # col_count = len(df_income.columns)
    # worksheet.set_column(firstcol=1, lastcol=col_count+1, width=12)
    # width = 12
    # for i in range(1, col_count + 1):
    #     worksheet.set_column(i, i, width)

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    writer.close()

complex_test()
exit()

rep = GCReport()
# from_date = datetime.datetime(2016,1,1,0,0,0,0)
# to_date = datetime.datetime(2016,12,31,23,59,59,0)
from_date = datetime.date(2016, 1, 1)
to_date = datetime.date(2016, 12, 31)
# start_time = time.time()
rep.open_book_sql("u:/sqllite_book/real-2017-01-26.gnucash", open_if_lock=True)
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

# df = rep.balance_by_period(from_date=from_date, to_date=to_date)
# rep.dataframe_to_excel(df, 'balance-exp')
# filename='U:/test_data/assets.pkl'
# df.to_pickle(filename)
# pr = pr.reset_index()

# a = rep.get_balance(acc)
# print(a)

# df = rep.turnover_by_period(from_date=from_date, to_date=to_date, account_type=GCReport.INCOME)
df = rep.complex_report(filename='complex', from_date=from_date, to_date=to_date)
# filename='U:/test_data/income.pkl'
# df.to_pickle(filename)
# rep.dataframe_to_excel(df, "itog-income", datetime_format='mmm yyyy')

#print(df)