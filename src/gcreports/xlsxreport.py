import os

import pandas

from xlsxwriter.utility import xl_col_to_name

from gcreports.gnucashdata import GNUCashData
from gcreports.margins import Margins
from gcreports.utils import dateformat_from_period


class XLSXReport:

    default_dir_reports = 'V:/tables'

    def __init__(self, filename, sheet='Sheet1', datetime_format=None, start_row=0):
        # self.filename = filename
        self._sheet = sheet
        self._worksheet = None
        self._datetime_format = dateformat_from_period(datetime_format)
        self._writer = pandas.ExcelWriter(filename, engine='xlsxwriter', datetime_format=datetime_format)
        self._workbook = self._writer.book
        self._cur_row = start_row
        self._charts = []
        self._headers = []

    def save(self):
        """
        Add charts of current sheet and save file
        :return:
        """
        self._add_headers()
        self._add_charts()
        self._writer.save()

    def next_sheet(self, sheet_name, start_row=0, datetime_format=None):
        """
        Next data will be on this new sheet
        :param sheet_name:
        :param start_row:
        :return:
        """
        self._add_headers()
        self._add_charts()
        self._sheet = sheet_name
        self._cur_row = start_row
        self._worksheet = None
        if datetime_format:
            self._datetime_format = dateformat_from_period(datetime_format)

    def add_empty_row(self):
        """
        Добавляет пустую строку
        :return:
        """
        self._cur_row += 1

    def _update_cur_row(self, next_row):
        """
        Update current row
        :param next_row: end of added lines
        :return:
        """
        if self._cur_row < next_row:
            self._cur_row = next_row

    def _add_charts(self):
        for chart in self._charts:
            name = chart['name']
            values = chart['values']
            if (not 'categories' in chart) and self.common_categories:
                chart['categories'] = self.common_categories

            ex_chart = self._workbook.add_chart({'type': 'column'})
            ex_chart.add_series(chart)
            ex_chart.set_size({'x_scale': 2, 'y_scale': 2})
            self._worksheet.insert_chart(row=self._cur_row, col=1, chart=ex_chart)
            self._update_cur_row(self._cur_row + 10)

        self._charts = []

    def _header_to_list(self, dataframe, row=-1, margins=None):
        if row <= -1:
            row = self._cur_row
        frmt_date = self._workbook.add_format()
        frmt_date.set_num_format(self._datetime_format)
        frmt_date.set_bold()
        frmt_date.set_align('center')
        columns = dataframe.columns.tolist()

        idx_len = len(dataframe.index.names)


        header ={'row': row, 'col': idx_len, 'columns': columns}

        self._headers.append(header)


        if not self.common_categories:
            start_col_letter = xl_col_to_name(idx_len)
            count_vtotals = 0
            if margins:
                count_vtotals = margins.get_counts_vtotals()

            end_col = xl_col_to_name(idx_len + len(columns) - 1 - count_vtotals)
            self.common_categories = '={0}!${1}${3}:${2}${3}'.format(self._sheet, start_col_letter, end_col, row + 1)

    def _add_headers(self):

        if self._headers:
            for header in self._headers:
                self._add_header()
            self._headers = []

    def _add_header(self, header):

        frmt_date = self._workbook.add_format()
        frmt_date.set_num_format(self._datetime_format)
        frmt_date.set_bold()
        frmt_date.set_align('center')

        cols = header['columns']

        col = header['col']
        row = header['row']

        for col_name in cols:
            self._worksheet.write(row, col, col_name, frmt_date)
            col += 1



    def add_header(self, dataframe, row=-1, margins=None):
        # Заголовок таблицы
        if row <= -1:
            row = self._cur_row
        frmt_date = self._workbook.add_format()
        frmt_date.set_num_format(self._datetime_format)
        frmt_date.set_bold()
        frmt_date.set_align('center')
        cols = dataframe.columns.tolist()

        i = len(dataframe.index.names)
        start_col = xl_col_to_name(i)

        for col_name in cols:
            self._worksheet.write(row, i, col_name, frmt_date)
            i += 1

        count_vtotals = 0
        if margins:
            count_vtotals = margins.get_counts_vtotals()

        end_col = xl_col_to_name(i-1-count_vtotals)
        self.common_categories = '={0}!${1}${3}:${2}${3}'.format(self._sheet, start_col, end_col, row + 1)
        self._update_cur_row(row + 1)

    def add_dataframe(self, dataframe, color=None, name=None, row=None, header=True, margins=None, addchart=None):
        # income_start_row = 2
        # income_height = len(dataframe)
        if not row:
            row = self._cur_row

        df_start_row = row
        if name:
            df_start_row = row + 1

        height = len(dataframe)
        if header:
            height += 1
            self._header_to_list(dataframe, row, margins)
            header = False

        itog_row = df_start_row + height - 1
        col_count = len(dataframe.columns)

        dataframe.to_excel(self._writer, sheet_name=self._sheet, startrow=df_start_row, header=header)
        # Get the xlsxwriter objects from the dataframe writer object.
        if not self._worksheet:
            self._worksheet = self._writer.sheets[self._sheet]

        frmt_bold = self._workbook.add_format({'bold': True})
        frmt_money = self._workbook.add_format()
        frmt_money.set_num_format(0x08)
        frmt_head = self._workbook.add_format({'bold': True})
        frmt_head.set_align('center')
        if color:
            frmt_head.set_bg_color(color)

        if name:
            self._worksheet.write(row, 0, name, frmt_head)

        # Выделение итогов
        width_totals_col = 0

        if margins:


            if (margins.total_row) or (len(dataframe) == 1 and color):
                self._worksheet.conditional_format(first_row=itog_row, last_row=itog_row, first_col=0, last_col=col_count,
                                                   options={'type': 'no_blanks',
                                                  'format': frmt_head})
                self._worksheet.conditional_format(first_row=itog_row, last_row=itog_row, first_col=0,
                                                   last_col=col_count,
                                                   options={'type': 'blanks',
                                                           'format': frmt_head})
            if margins.total_col or margins.mean_col:
                if margins.total_col:
                    width_totals_col += 1
                if margins.mean_col:
                    width_totals_col += 1
                start_col = col_count
                self._worksheet.conditional_format(first_row=df_start_row, last_row=itog_row, first_col=col_count - width_totals_col + 1,
                                                   last_col=col_count,
                                                   options={'type': 'no_blanks',
                                                           'format': frmt_bold})

        # Ширина первой колонки
        index_len = len(dataframe.index.names)
        self._worksheet.set_column(firstcol=0, lastcol=index_len - 1, width=25)
        self._worksheet.set_column(firstcol=index_len, lastcol=col_count, cell_format=frmt_money, width=12)

        if margins:
            if margins.empty_col:
                empty_col = col_count-width_totals_col
                self._worksheet.set_column(firstcol=empty_col, lastcol=empty_col, width=1)

        if addchart:
            chart_prop = self._get_chart_prop(dataframe, name=name, header=header, margins=margins, row=row)
            self._charts.append(chart_prop)

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
            categories = '={0}!${1}${3}:${2}${3}'.format(self._sheet, str_start_col, str_end_col, row + 1)
            chart_prop.categories = categories
        # values Последняя строка dataframe
        # 'values': '=Sheet1!$B$37:$M$37'
        values = '={0}!${1}${3}:${2}${3}'.format(self._sheet, str_start_col, str_end_col, itog_row + 1)
        chart_prop['values'] = values

        chart_name = ''
        if name:
            chart_name = name
        else:
            # Ссылка на начало последней строчки
            chart_name = '={}!$A${}'.format(self._sheet, itog_row + 1)

        chart_prop['name'] = chart_name





        return chart_prop


