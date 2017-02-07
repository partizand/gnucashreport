import argparse
import datetime
import os
import time
import pandas
from pandas.util.testing import assert_frame_equal
from gcreports.gcreport import GCReport
from xlsxwriter.utility import xl_rowcol_to_cell
from gcreports.xlsxreport import XlSXReport


def _dataframe_to_writer(writer, dataframe, row, color, name, itog_name, sheet='Sheet1', h_total=False):
    # income_start_row = 2
    # income_height = len(dataframe)
    if row<1:
        row = 1
    height = len(dataframe)
    itog_row = row + height
    dataframe.to_excel(writer, sheet_name=sheet, startrow=row, header=False)
    # Get the xlsxwriter objects from the dataframe writer object.
    workbook = writer.book
    worksheet = writer.sheets[sheet]

    frmt_money = workbook.add_format()
    frmt_money.set_num_format(0x08)

    frmt_head = workbook.add_format({'bold': True})
    frmt_head.set_align('center')
    frmt_head.set_bg_color(color)
    frmt_head.set_num_format(0x08)

    worksheet.write(row - 1, 0, name, frmt_head)
    worksheet.write(itog_row, 0, itog_name, frmt_head)

    col_count = len(dataframe.columns)

    # total itog
    for i in range(1, col_count+1):
        sum1_cell = xl_rowcol_to_cell(row, i)
        sum2_cell = xl_rowcol_to_cell(itog_row-1, i)
        formula = '=SUM({}:{})'.format(sum1_cell, sum2_cell)
        worksheet.write_formula(itog_row, i, formula, frmt_head)

    # right itog sum
    if h_total:
        for i in range(row, itog_row+1):
            sum1_cell = xl_rowcol_to_cell(i, 1)
            sum2_cell = xl_rowcol_to_cell(i, col_count)
            formula = '=SUM({}:{})'.format(sum1_cell, sum2_cell)
            worksheet.write_formula(i, col_count + 2, formula, cell_format=frmt_money)

        # right itog average
        for i in range(row, itog_row + 1):
            # sum1_cell = xl_rowcol_to_cell(i, 1)
            sum_cell = xl_rowcol_to_cell(i, col_count+2)
            formula = '={}/{}'.format(sum_cell, col_count)
            worksheet.write_formula(i, col_count + 3, formula, cell_format=frmt_money)

    # Format money
    worksheet.set_column(firstcol=1, lastcol=col_count + 1, cell_format=frmt_money)

    # Format itog line
    # worksheet.conditional_format(first_row=itog_row, first_col=0,
    #                              last_row=itog_row, last_col=col_count,
    #                              options={'type': 'no_blanks', 'format': frmt_head})

    return itog_row + 3

def _total_row(workbook, worksheet, row, len, formula_row1, formula_row2, name, color, formula='={}-{}', h_total=False):
    # Прибыль

    frmt_profit = workbook.add_format({'bold': True})
    frmt_profit.set_align('center')
    frmt_profit.set_bg_color(color)
    frmt_profit.set_num_format(0x08)

    frmt_money = workbook.add_format()
    frmt_money.set_num_format(0x08)

    worksheet.write_string(row=row, col=0, string=name, cell_format=frmt_profit)
    # profit
    for i in range(1, len + 1):
        sum1_cell = xl_rowcol_to_cell(formula_row1, i)
        sum2_cell = xl_rowcol_to_cell(formula_row2, i)
        str_formula = formula.format(sum1_cell, sum2_cell)
        worksheet.write_formula(row, i, str_formula, frmt_profit)

    # right itog sum
    if h_total:
        sum1_cell = xl_rowcol_to_cell(row, 1)
        sum2_cell = xl_rowcol_to_cell(row, len)
        formula = '=SUM({}:{})'.format(sum1_cell, sum2_cell)
        worksheet.write_formula(row, len + 2, formula, cell_format=frmt_money)

        # right itog average
        sum_cell = xl_rowcol_to_cell(row, len + 2)
        formula = '={}/{}'.format(sum_cell, len)
        worksheet.write_formula(row, len + 3, formula, cell_format=frmt_money)

    return row + 2


def complex_test():

    dir_excel = "U:/tables"
    filename = 'complex'
    datetime_format = 'mmm yyyy'

    sheet = 'Sheet1'

    start_row = 2



    if not filename.endswith('.xlsx'):
        filename = os.path.join(dir_excel, filename + ".xlsx")

    df_income = pandas.read_pickle('U:/test_data/income.pkl') #  self.turnover_by_period(from_date=from_date, to_date=to_date, period=period, account_type=self.INCOME)
    df_expense = pandas.read_pickle('U:/test_data/expense.pkl')# self.turnover_by_period(from_date=from_date, to_date=to_date, period=period, account_type=self.EXPENSE)
    df_assets = pandas.read_pickle('U:/test_data/assets.pkl')# self.turnover_by_period(from_date=from_date, to_date=to_date, period=period, account_type=self.EXPENSE)
    df_loans = pandas.read_pickle('U:/test_data/loans.pkl')# self.turnover_by_period(from_date=from_date, to_date=to_date, period=period, account_type=self.EXPENSE)
    # Добавить итоги (для теста)
    # df_income = df_income.append(df_income.sum(), ignore_index=True)
    # df_expense = df_expense.append(df_expense.sum(), ignore_index=True)
    # df_assets = df_assets.append(df_assets.sum(), ignore_index=True)

    # Ширина остальных колонок
    col_count = len(df_income.columns)

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pandas.ExcelWriter(filename, engine='xlsxwriter', datetime_format=datetime_format)

    # Income
    # income_start_row = 2
    # income_height = len(df_income)
    # income_itog_row = income_start_row + income_height - 1
    # df_income.to_excel(writer, sheet_name=sheet, startrow=income_start_row, header=False)
    income_row = start_row
    next_row = _dataframe_to_writer(writer=writer, dataframe=df_income, row=start_row, color='#00ff11',
                                    name='ДОХОДЫ', itog_name='ИТОГО ДОХОДЫ', sheet=sheet, h_total=True)

    # Get the xlsxwriter objects from the dataframe writer object.
    workbook = writer.book
    worksheet = writer.sheets[sheet]

    # Expense
    # expense_start_row = income_start_row + income_height + 2
    # expense_height = len(df_expense)
    # expense_itog_row = expense_start_row + expense_height - 1
    # df_expense.to_excel(writer, sheet_name=sheet, header=False, startrow=expense_start_row)
    expense_row = next_row
    next_row = _dataframe_to_writer(writer=writer, dataframe=df_expense, row=next_row, color='#FFFF00',
                                    name='РАСХОДЫ', itog_name='ИТОГО РАСХОДЫ', sheet=sheet, h_total=True)

    # Прибыль

    next_row = next_row - 1
    profit_row = next_row
    next_row = _total_row(workbook=workbook, worksheet=worksheet, row=next_row, len=col_count,
               formula_row1=income_row + len(df_income), formula_row2=expense_row + len(df_expense),
               name='ПРИБЫЛЬ', color='#00ff11', h_total=True)

    # Assets
    # assets_start_row = expense_itog_row + 3
    # assets_height = len(df_assets)
    # assets_itog_row = assets_start_row + assets_height - 1
    # df_assets.to_excel(writer, sheet_name=sheet, header=False, startrow=assets_start_row)
    next_row = next_row + 1
    asset_row = next_row
    next_row = _dataframe_to_writer(writer=writer, dataframe=df_assets, row=next_row, color='#3d6ef7',
                                    name='АКТИВЫ', itog_name='ИТОГО АКТИВЫ', sheet=sheet)

    # Loans
    loans_row = next_row
    next_row = _dataframe_to_writer(writer=writer, dataframe=df_loans, row=next_row, color='#FFFF00',
                                    name='ДОЛГИ', itog_name='ИТОГО ДОЛГИ', sheet=sheet)

    # Собственные средства

    next_row = next_row - 1
    itog_row = next_row
    next_row = _total_row(workbook=workbook, worksheet=worksheet, row=next_row, len=col_count,
                          formula_row1=asset_row + len(df_assets), formula_row2=loans_row + len(df_loans),
                          name='СОБСТВЕННЫЕ СРЕДСТВА', color='#00ff11', formula='={}+{}')

    # last_row = next_row - 1



    # Add a number format for cells with money.
    frmt_money = workbook.add_format()
    frmt_money.set_num_format(0x08)
    # frmt_head_expense = workbook.add_format({'bold': True})
    # frmt_head_expense.set_align('center')
    # frmt_head_expense.set_bg_color('#FFFF00')
    # frmt_head_assets = workbook.add_format({'bold': True})
    # frmt_head_assets.set_align('center')
    # frmt_head_assets.set_bg_color('#3d6ef7')
    frmt_profit = workbook.add_format({'bold': True})
    frmt_profit.set_align('center')
    frmt_profit.set_bg_color('#00ff11')
    frmt_profit.set_num_format(0x08)
    frmt_date = workbook.add_format()
    frmt_date.set_num_format('mmm yyyy')
    frmt_date.set_bold()
    frmt_date.set_align('center')
    frmt_bold = workbook.add_format({'bold': True})
    frmt_bold.set_align('center')
    #
    # worksheet.write(income_start_row - 1, 0, 'ДОХОДЫ', frmt_income)
    # worksheet.write(income_itog_row, 0, 'Итого доходы', frmt_income)
    # worksheet.write(expense_start_row - 1, 0, 'Расходы', frmt_head_expense)
    # worksheet.write(expense_itog_row, 0, 'Итого расходы', frmt_head_expense)
    # worksheet.write(assets_start_row - 1, 0, 'АКТИВЫ', frmt_head_assets)
    # worksheet.write(assets_itog_row, 0, 'Итого АКТИВЫ', frmt_head_assets)
    # Ширина первой колонки
    worksheet.set_column(firstcol=0, lastcol=0, width=25)

    worksheet.set_column(firstcol=1, lastcol=col_count, cell_format=frmt_money, width=12)
    # Ширина за последней колонкой
    worksheet.set_column(firstcol=col_count + 1, lastcol=col_count + 1, width=3)
    # Ширина за последней последней колонкой
    worksheet.set_column(firstcol=col_count + 2, lastcol=col_count + 3, width=12)

    # Формат итогов

    # worksheet.conditional_format(first_row=income_itog_row, first_col=0,
    #                              last_row=income_itog_row, last_col=col_count,
    #                              options={'type': 'no_blanks', 'format': frmt_income})
    #
    # worksheet.conditional_format(first_row=expense_itog_row, first_col=0,
    #                              last_row=expense_itog_row, last_col=col_count,
    #                              options={'type': 'no_blanks', 'format': frmt_head_expense})
    #
    # worksheet.conditional_format(first_row=assets_itog_row, first_col=0,
    #                              last_row=assets_itog_row, last_col=col_count,
    #                              options={'type': 'no_blanks', 'format': frmt_head_assets})



    # worksheet.write_string(row=last_row, col=0, string='ПРИБЫЛЬ', cell_format=frmt_profit)
    # profit
    # for i in range(1, col_count + 1):
    #     sum1_cell = xl_rowcol_to_cell(income_row+len(df_income), i)
    #     sum2_cell = xl_rowcol_to_cell(expense_row + len(df_expense), i)
    #     formula = '={}-{}'.format(sum1_cell, sum2_cell)
    #     worksheet.write_formula(last_row, i, formula, frmt_profit)

    # Заголовок таблицы
    cols = df_income.columns.tolist()
    i = 1
    for col in cols:
        worksheet.write(0, i, col, frmt_date)
        i = i + 1
    worksheet.write(0, col_count + 2, 'Всего', frmt_bold)
    worksheet.write(0, col_count + 3, 'Среднее', frmt_bold)

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    writer.close()

# complex_test()
# exit()

filename = 'u:/tables/ex-test.xlsx'
template_file = 'u:/tables/template.xlsx'

df_income = pandas.read_pickle('U:/test_data/income.pkl')
df_expense = pandas.read_pickle('U:/test_data/expense.pkl')
df_assets = pandas.read_pickle('U:/test_data/assets.pkl')
df_loans = pandas.read_pickle('U:/test_data/loans.pkl')

# styles = exutils.MyNamedStyles(template_file)

xlsxreport = XlSXReport(filename=filename, template_file=template_file)

xlsxreport.add_dataframe(df_income, 'income_header', header=True)

xlsxreport.save()


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