import os

import pandas

from xlsxwriter.utility import xl_col_to_name

from gcreports.gnucashdata import GNUCashData
from gcreports.margins import Margins

class XLSXReport:

    default_dir_reports = 'V:/tables'

    def __init__(self, filename, sheet='Sheet1', datetime_format=None, start_row=0):
        self.filename = filename
        self.sheet = sheet
        self.worksheet = None
        self.writer = pandas.ExcelWriter(filename, engine='xlsxwriter', datetime_format=datetime_format)
        self.workbook = self.writer.book
        self.cur_row = start_row
        self.charts = []
        # self.datetime_format = XLSXReport.dateformat_from_period(period=datetime_format)
        self.datetime_format = datetime_format
        # if datetime_format:
        #     self.datetime_format = datetime_format
        # else:
        #     self.datetime_format = 'dd-mm-yyyy'

    def save(self):
        self._add_charts()
        self.writer.save()




    # def complex_report(self, gcreport, from_date, to_date, period='M', glevel=1):
    #     # margins.set_for_profit()
    #     # df = rep.equity_by_period(from_date=from_date, to_date=to_date, glevel=[0, 1], margins=margins)
    #     # XLSXReport.dataframe_to_excel(df, 'equity')
    #     # exit()
    #     margins = Margins()
    #     margins.set_for_turnover()
    #     margins.empty_col = True
    #     # filename = 'v:/tables/ex-test.xlsx'
    #     # glevel = 1
    #     # xlsxreport = XLSXReport(filename=self.filename, datetime_format='mmm yyyy')
    #
    #     # Income
    #     df_income = gcreport.turnover_by_period(from_date=from_date, to_date=to_date, period=period, account_type=GNUCashData.INCOME,
    #                                             glevel=glevel, margins=margins)
    #     self.add_dataframe(df_income, name='Доходы', color='green', header=False, margins=margins, row=1)
    #     self.add_empty_row()
    #
    #     # expense
    #     df_expense = gcreport.turnover_by_period(from_date=from_date, to_date=to_date, period=period, account_type=GNUCashData.EXPENSE,
    #                                              glevel=glevel, margins=margins)
    #     self.add_dataframe(df_expense, name='Расходы', color='yellow', header=False, margins=margins)
    #     self.add_empty_row()
    #
    #     # profit
    #     margins.set_for_profit()
    #     df_profit = gcreport.profit_by_period(from_date=from_date, to_date=to_date, period=period, glevel=glevel, margins=margins)
    #     self.add_dataframe(df_profit, color='red', header=False, margins=margins)
    #     self.add_empty_row()
    #
    #     # assets
    #     margins.set_for_balances()
    #     df_assets = gcreport.balance_by_period(from_date=from_date, to_date=to_date, period=period, glevel=glevel, margins=margins)
    #     self.add_dataframe(df_assets, color='green', name='Активы', header=False, margins=margins)
    #     self.add_empty_row()
    #
    #     # loans
    #     margins.total_row = False
    #     df_loans = gcreport.balance_by_period(from_date=from_date, to_date=to_date, period=period, glevel=0,
    #                                           account_types=GNUCashData.LIABILITY,
    #                                           margins=margins)
    #     self.add_dataframe(df_loans, color='yellow', header=False, margins=margins)
    #     self.add_empty_row()
    #
    #     # equity
    #     # margins.set_for_profit()
    #     df_profit = gcreport.equity_by_period(from_date=from_date, to_date=to_date, period=period, glevel=glevel, margins=margins)
    #     self.add_dataframe(df_profit, color='green', header=False, margins=margins, addchart=True)
    #     self.add_empty_row()
    #
    #     # xlsxreport.add_chart()
    #
    #     margins.set_for_turnover()
    #     self.add_header(df_income, row=0, margins=margins)
    #     # xlsxreport.add_empty_row()
    #     # xlsxreport.add_dataframe(df)
    #     # xlsxreport.set_cell_format()
    #     # xlsxreport.add_df_test(df)
    #
    #     # xlsxreport.save()

    def add_empty_row(self):
        """
        Добавляет пустую строку
        :return:
        """
        self.cur_row += 1

    def _update_cur_row(self, next_row):
        """
        Update current row
        :param next_row: end of added lines
        :return:
        """
        if self.cur_row < next_row:
            self.cur_row = next_row

    def _add_charts(self):
        for chart in self.charts:
            name = chart['name']
            values = chart['values']
            if (not 'categories' in chart) and self.common_categories:
                chart['categories'] = self.common_categories

            ex_chart = self.workbook.add_chart({'type': 'column'})
            ex_chart.add_series(chart)
            ex_chart.set_size({'x_scale': 2, 'y_scale': 2})
            self.worksheet.insert_chart(row=self.cur_row, col=1, chart=ex_chart)
            self._update_cur_row(self.cur_row + 10)

    def add_header(self, dataframe, row=-1, margins=None):
        # Заголовок таблицы
        if row <= -1:
            row=self.cur_row
        frmt_date = self.workbook.add_format()
        frmt_date.set_num_format('mmm yyyy')
        frmt_date.set_bold()
        frmt_date.set_align('center')
        cols = dataframe.columns.tolist()

        i = len(dataframe.index.names)
        start_col = xl_col_to_name(i)

        for col_name in cols:
            # self.worksheet.write(0, i, col, frmt_date)
            self.worksheet.write(row, i, col_name, frmt_date)
            i = i + 1

        count_vtotals = 0
        if margins:
            count_vtotals = margins.get_counts_vtotals()

        end_col = xl_col_to_name(i-1-count_vtotals)
        self.common_categories = '={0}!${1}${3}:${2}${3}'.format(self.sheet, start_col, end_col, row+1)
        # self.worksheet.write(0, col_count + 2, 'Всего', frmt_bold)
        # self.worksheet.write(0, col_count + 3, 'Среднее', frmt_bold)
        self._update_cur_row(row + 1)
        # self.cur_row = row + 1

    def add_dataframe(self, dataframe, color=None, name=None, row=None, header=True, margins=None, addchart=None):
        # income_start_row = 2
        # income_height = len(dataframe)
        if not row:
            row = self.cur_row

        df_start_row = row
        if name:
            df_start_row = row + 1

        height = len(dataframe)
        if header:
            height += 1

        itog_row = df_start_row + height - 1
        col_count = len(dataframe.columns)

        dataframe.to_excel(self.writer, sheet_name=self.sheet, startrow=df_start_row, header=header)
        # Get the xlsxwriter objects from the dataframe writer object.
        if not self.worksheet:
            self.worksheet = self.writer.sheets[self.sheet]

        frmt_bold = self.workbook.add_format({'bold': True})
        frmt_money = self.workbook.add_format()
        frmt_money.set_num_format(0x08)
        frmt_head = self.workbook.add_format({'bold': True})
        frmt_head.set_align('center')
        if color:
            frmt_head.set_bg_color(color)

        if name:
            self.worksheet.write(row, 0, name, frmt_head)

        # Выделение итогов
        width_totals_col = 0

        if margins:


            if (margins.total_row) or (len(dataframe) == 1 and color):
                self.worksheet.conditional_format(first_row=itog_row, last_row=itog_row, first_col=0, last_col=col_count,
                                                  options={'type': 'no_blanks',
                                                  'format': frmt_head})
                self.worksheet.conditional_format(first_row=itog_row, last_row=itog_row, first_col=0,
                                                  last_col=col_count,
                                                  options={'type': 'blanks',
                                                           'format': frmt_head})
            if margins.total_col or margins.mean_col:
                if margins.total_col:
                    width_totals_col += 1
                if margins.mean_col:
                    width_totals_col += 1
                start_col = col_count
                self.worksheet.conditional_format(first_row=df_start_row, last_row=itog_row, first_col=col_count-width_totals_col+1,
                                                  last_col=col_count,
                                                  options={'type': 'no_blanks',
                                                           'format': frmt_bold})

        # Ширина первой колонки
        index_len = len(dataframe.index.names)
        self.worksheet.set_column(firstcol=0, lastcol=index_len-1, width=25)
        self.worksheet.set_column(firstcol=index_len, lastcol=col_count, cell_format=frmt_money, width=12)

        if margins:
            if margins.empty_col:
                empty_col = col_count-width_totals_col
                self.worksheet.set_column(firstcol=empty_col, lastcol=empty_col, width=1)

        if addchart:
            chart_prop = self._get_chart_prop(dataframe, name=name, header=header, margins=margins, row=row)
            self.charts.append(chart_prop)

        self._update_cur_row(itog_row + 1)

    def _get_chart_prop(self, dataframe, name, header, margins, row):
        """
        Возвращает текст-ссылку на categories для chart
        :param dataframe:
        :param margins:
        :param row:
        :return:
        """
        chart_prop = {}

        # if row == -1:
        #     row = self.cur_row

        df_start_row = row
        if name:
            df_start_row = row + 1

        height = len(dataframe)
        if header:
            height += 1

        itog_row = df_start_row + height - 1
        col_count = len(dataframe.columns)

        len_index = len(dataframe.index.names)
        str_start_col = xl_col_to_name(len_index)

        count_vtotals = 0
        if margins:
            count_vtotals = margins.get_counts_vtotals()
        str_end_col = xl_col_to_name(col_count - count_vtotals)
        if header:
            categories = '={0}!${1}${3}:${2}${3}'.format(self.sheet, str_start_col, str_end_col, row + 1)
            chart_prop.categories = categories
        # values Последняя строка dataframe
        # 'values': '=Sheet1!$B$37:$M$37'
        values = '={0}!${1}${3}:${2}${3}'.format(self.sheet, str_start_col, str_end_col, itog_row + 1)
        chart_prop['values'] = values

        chart_name = ''
        if name:
            chart_name = name
        else:
            # Ссылка на начало последней строчки
            chart_name = '={}!$A${}'.format(self.sheet, itog_row + 1)

        chart_prop['name'] = chart_name





        return chart_prop


