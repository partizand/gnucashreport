import collections
import pandas
from decimal import Decimal

import xlsxwriter
from gnucashreport.margins import Margins
from xlsxwriter.utility import xl_col_to_name

from gnucashreport.utils import dateformat_from_period

COLOR_GREEN = '#92D050'
COLOR_GREEN_DARK = '#00B050'
COLOR_BLUE = '#00B0F0'
COLOR_YELLOW = '#FFFF00'
COLOR_ORANGE_LIGHT = '#FDE9D9'

class TablePoints:
    def __init__(self, dataframe, header, margins, row):
        """
        Calculate positions for table in excel file
        All positions are 0-started

+--------------------------------------------------------------------------------------------------------------------+
| Account header                |  Data                                | totals                                      |
|--------------------------------------------------------------------------------------------------------------------+
| col_begin |   | col_head_end  | col_data_begin | | |  | col_data_end | col_empty | col_total_begin | col_total_end |
| row_begin |   |               |                | | |  |              |           |                 |               |
+-----------+---+---------------+----------------+-+-+--+--------------+-----------+-----------------+---------------+
|row_data_begin |               |                | | |  |              |           |                 |               |
+-----------+---+---------------+----------------+-+-+--+--------------+-----------+-----------------+---------------+
|           |   |               |                | | |  |              |           |                 |               |
+-----------+---+---------------+----------------+-+-+--+--------------+-----------+-----------------+---------------+
|           |   |               |                | | |  |              |           |                 |               |
+-----------+---+---------------+----------------+-+-+--+--------------+-----------+-----------------+---------------+
| row_itog  |   |               |                | | |  |              |           |                 | col_all_end   |
+-----------+---+---------------+----------------+-+-+--+--------------+-----------+-----------------+---------------+


        :param dataframe:
        :param header:
        :param margins:
        :param row:
        """

        # Кол-во колонок названий
        len_index = len(dataframe.index.names)
        # Высота данных без заголовка
        height = len(dataframe)
        # Кол-во колонок с данными (без колонок названий)
        col_count = len(dataframe.columns)

        self.col_empty = None
        self.col_totals_begin = None
        self.col_totals_end = None

        self.col_begin = 0
        self.row_begin = row
        self.row_data_begin = row
        if header:
            self.row_data_begin += 1

        # Номер колонки с окончанием заголовка для счетов
        self.col_head_end = self.col_begin + len_index - 1

        self.col_data_begin = self.col_head_end + 1
        self.col_data_end = self.col_data_begin + col_count - 1
        self.col_all_end = self.col_data_begin + col_count - 1

        # Строка с итоговыми значениями
        self.row_itog = self.row_data_begin + height - 1

        # self.count_vtotals = 0
        # self.count_vtotals_without_empty = 0
        if margins:
            count_vtotals = margins.get_counts_vtotals()
            if count_vtotals:
                self.col_data_end -= count_vtotals
                self.col_totals_begin = self.col_data_end + 1
                self.col_totals_end = self.col_data_end + count_vtotals
                if margins.empty_col:
                    self.col_empty = self.col_data_end + 1
                    self.col_totals_begin = self.col_data_end + 2
                    self.col_empty_l = xl_col_to_name(self.col_empty)
                self.col_totals_begin_l = xl_col_to_name(self.col_totals_begin)
                self.col_totals_end_l = xl_col_to_name(self.col_totals_end)

        # Буквы для колонок
        self.col_begin_l = xl_col_to_name(self.col_begin)
        self.col_data_begin_l = xl_col_to_name(self.col_data_begin)
        self.col_data_end_l = xl_col_to_name(self.col_data_end)
        self.col_head_end_l = xl_col_to_name(self.col_head_end)


class XLSXReport:
    default_dir_reports = 'V:/tables'



    MONEY_FORMAT = 0x08
    # MONEY_FORMAT = 0x08
    # MONEY_FORMAT = '# ##0,00'
    # MONEY_FORMAT = '# ##,##'
    PERCENTAGE_FORMAT = 0x0a

    T_BALANCE = 'balance'
    T_INFLATION = 'inflation'
    T_RETURN = 'return'


    def __init__(self, filename, sheet='Sheet1', datetime_format=None, start_row=0):
        # self.filename = filename
        # self._sheet = sheet
        # self._worksheet = None
        self._datetime_format = dateformat_from_period(datetime_format)
        # self._writer = pandas.ExcelWriter(filename, engine='xlsxwriter', datetime_format=self._datetime_format)
        self._workbook = xlsxwriter.Workbook(filename)
        self.next_sheet(sheet=sheet)
        # self._worksheet = self._workbook.add_worksheet(sheet)

        # Test


        # self._some_init(sheet=sheet, start_row=start_row, datetime_format=datetime_format)
        self._set_formats()

    def save(self):
        """
        Add charts of current sheet and save file
        :return:
        """
        # self._add_headers()
        self._add_charts()
        self._workbook.close()
        # _writer.save()

    def next_sheet(self, sheet, start_row=0, datetime_format=None):
        """
        Next data will be on this new sheet
        :param sheet:
        :param start_row:
        :return:
        """
        # self._add_headers()
        self._add_charts()
        self._worksheet = self._workbook.add_worksheet(sheet)
        # self._sheet = sheet
        # self._cur_row = start_row
        # self._worksheet = None
        # self.common_categories = None
        # if datetime_format:
        #     self._datetime_format = dateformat_from_period(datetime_format)
        # self._some_init(sheet=sheet, start_row=start_row, datetime_format=datetime_format)

    # def _some_init(self, sheet, start_row, datetime_format):
    #     # self._sheet = sheet
    #     # self._worksheet = None
    #     # if datetime_format:
    #         self._datetime_format = dateformat_from_period(datetime_format)
    #     self._cur_row = start_row
    #     self._charts = []
    #     self._headers = []
    #     self.common_categories = None

    def _set_formats(self):
        # Заголовки таблиц
        self._format_header = self._workbook.add_format({'bold': True})
        self._format_header.set_align('center')
        self._format_index_left = self._workbook.add_format({'bold': True})
        self._format_index_center = self._workbook.add_format({'bold': True})
        self._format_index_center.set_align('center')
        self._format_itog = self._workbook.add_format({'bold': True})
        self._format_itog.set_align('center')
        # Значение в валюте
        self._format_value_currency = self._workbook.add_format()
        self._format_value_currency.set_num_format(self.MONEY_FORMAT)
        # Значение в процентах
        self._format_value_perc = self._workbook.add_format()
        self._format_value_perc.set_num_format(self.PERCENTAGE_FORMAT)
        # Формат доходов
        self._format_income = self._workbook.add_format({'bold': True})
        self._format_income.set_bg_color(COLOR_GREEN)

    def add_report(self, report: pandas.DataFrame, margins:Margins=None, start_row=None,
                   name=None, color=None, rep_type=None, addchart=None):
        header = True

        if start_row:
            row = start_row
        else:
            row = self._cur_row

        points = TablePoints(dataframe=report, header=header, margins=margins, row=row)

        chart_prop = self._get_chart_prop(points=points, name=name, header=header, addchart=addchart)

        if header:
            self._header_to_list(report, row, margins)
            if not self.common_categories:
                self.common_categories = chart_prop['categories']

        if addchart:
            self._charts.append(chart_prop)

        self.add_dataframe_test(report,  )
        dataframe.to_excel(self._writer, sheet_name=self._sheet, startrow=points.row_data_begin, header=False)
        # Get the xlsxwriter objects from the dataframe writer object.
        if not self._worksheet:
            self._worksheet = self._writer.sheets[self._sheet]

        frmt_bold = self._workbook.add_format({'bold': True})
        frmt_cell = self._workbook.add_format()
        if cell_format:
            frmt_cell.set_num_format(cell_format)
        frmt_cell_bold = self._workbook.add_format({'bold': True})
        if cell_format:
            frmt_cell_bold.set_num_format(cell_format)
        frmt_head = self._workbook.add_format({'bold': True})
        if cell_format:
            frmt_head.set_num_format(cell_format)
        frmt_head.set_align('center')
        if color:
            frmt_head.set_bg_color(color)

        if name:
            # self._worksheet.write(df_start_row - 1, 0, name, frmt_head)
            self._worksheet.write(row, 0, name, frmt_head)

        # Выделение итогов
        # width_totals_col = 0

        if margins:
            # Выделение строки с итогами
            if (margins.total_row) or (len(report) == 1 and color):
                self._worksheet.conditional_format(first_row=points.row_itog,
                                                   last_row=points.row_itog,
                                                   first_col=points.col_begin,
                                                   last_col=points.col_all_end,
                                                   options={'type': 'no_errors',
                                                            'format': frmt_head})
                # self._worksheet.conditional_format(first_row=points.row_itog,
                #                                    last_row=points.row_itog,
                #                                    first_col=points.col_begin,
                #                                    last_col=points.col_all_end,
                #                                    options={'type': 'blanks',
                #                                             'format': frmt_head})
            if margins.total_col or margins.mean_col:
                # Ширина пустой колонки
                if margins.empty_col:
                    # empty_col = self.col_count-width_totals_col
                    self._worksheet.set_column(firstcol=points.col_empty, lastcol=points.col_empty, width=1)
                # Итоговые колонки жирным
                self._worksheet.conditional_format(first_row=points.row_data_begin,
                                                   last_row=points.row_itog,
                                                   first_col=points.col_totals_begin,
                                                   # col_count - width_totals_col + 1,
                                                   last_col=points.col_totals_end,
                                                   options={'type': 'no_errors',
                                                            'format': frmt_cell_bold})
                # Ширина колонк с итогами
                if points.col_totals_begin and points.col_totals_end:
                    self._worksheet.set_column(firstcol=points.col_totals_begin, lastcol=points.col_totals_end,
                                               cell_format=frmt_cell,
                                               width=15)



        # index_len = len(dataframe.index.names)
        # Ширина первой колонки
        self._worksheet.set_column(firstcol=points.col_begin, lastcol=points.col_head_end, width=25)
        # Ширина колонок до итогов
        self._worksheet.set_column(firstcol=points.col_data_begin,
                                   lastcol=points.col_data_end, width=12, #)
                                   cell_format=frmt_cell)

        # Формат ячеек с данными
        # self._worksheet.conditional_format(first_row=points.row_data_begin,
        #                                    last_row=points.row_itog,
        #                                    first_col=points.col_data_begin,
        #                                    last_col=points.col_data_end,
        #                                    options={'type': 'no_errors',
        #                                             'format': frmt_cell})

        self._update_cur_row(points.row_itog + 1)


    def add_dataframe(self, dataframe, color=None, name=None, row=None, header=True, margins=None, addchart=None,
                      cell_format=None):
        """
        Add DataFrame on current sheet, update next position to down
        :param dataframe:
        :param color:
        :param name:
        :param row:
        :param header: Show DataFrame header
        :param margins:
        :param addchart: must be type of chart: 'column', 'line'. See xlsxwriter help
        :param cell_format: cell format number for data
        :return:
        """

        if not row:
            row = self._cur_row

        points = TablePoints(dataframe=dataframe, header=header, margins=margins, row=row)

        chart_prop = self._get_chart_prop(points=points, name=name, header=header, addchart=addchart)

        if header:
            self._header_to_list(dataframe, row, margins)
            if not self.common_categories:
                self.common_categories = chart_prop['categories']

        if addchart:
            self._charts.append(chart_prop)

        dataframe.to_excel(self._writer, sheet_name=self._sheet, startrow=points.row_data_begin, header=False)
        # Get the xlsxwriter objects from the dataframe writer object.
        if not self._worksheet:
            self._worksheet = self._writer.sheets[self._sheet]

        frmt_bold = self._workbook.add_format({'bold': True})
        frmt_cell = self._workbook.add_format()
        if cell_format:
            frmt_cell.set_num_format(cell_format)
        frmt_cell_bold = self._workbook.add_format({'bold': True})
        if cell_format:
            frmt_cell_bold.set_num_format(cell_format)
        frmt_head = self._workbook.add_format({'bold': True})
        if cell_format:
            frmt_head.set_num_format(cell_format)
        frmt_head.set_align('center')
        if color:
            frmt_head.set_bg_color(color)

        if name:
            # self._worksheet.write(df_start_row - 1, 0, name, frmt_head)
            self._worksheet.write(row, 0, name, frmt_head)

        # Выделение итогов
        # width_totals_col = 0

        if margins:
            # Выделение строки с итогами
            if (margins.total_row) or (len(dataframe) == 1 and color):
                self._worksheet.conditional_format(first_row=points.row_itog,
                                                   last_row=points.row_itog,
                                                   first_col=points.col_begin,
                                                   last_col=points.col_all_end,
                                                   options={'type': 'no_errors',
                                                            'format': frmt_head})
                # self._worksheet.conditional_format(first_row=points.row_itog,
                #                                    last_row=points.row_itog,
                #                                    first_col=points.col_begin,
                #                                    last_col=points.col_all_end,
                #                                    options={'type': 'blanks',
                #                                             'format': frmt_head})
            if margins.total_col or margins.mean_col:
                # Ширина пустой колонки
                if margins.empty_col:
                    # empty_col = self.col_count-width_totals_col
                    self._worksheet.set_column(firstcol=points.col_empty, lastcol=points.col_empty, width=1)
                # Итоговые колонки жирным
                self._worksheet.conditional_format(first_row=points.row_data_begin,
                                                   last_row=points.row_itog,
                                                   first_col=points.col_totals_begin,
                                                   # col_count - width_totals_col + 1,
                                                   last_col=points.col_totals_end,
                                                   options={'type': 'no_errors',
                                                            'format': frmt_cell_bold})
                # Ширина колонк с итогами
                if points.col_totals_begin and points.col_totals_end:
                    self._worksheet.set_column(firstcol=points.col_totals_begin, lastcol=points.col_totals_end,
                                               cell_format=frmt_cell,
                                               width=15)



        # index_len = len(dataframe.index.names)
        # Ширина первой колонки
        self._worksheet.set_column(firstcol=points.col_begin, lastcol=points.col_head_end, width=25)
        # Ширина колонок до итогов
        self._worksheet.set_column(firstcol=points.col_data_begin,
                                   lastcol=points.col_data_end, width=12, #)
                                   cell_format=frmt_cell)

        # Формат ячеек с данными
        # self._worksheet.conditional_format(first_row=points.row_data_begin,
        #                                    last_row=points.row_itog,
        #                                    first_col=points.col_data_begin,
        #                                    last_col=points.col_data_end,
        #                                    options={'type': 'no_errors',
        #                                             'format': frmt_cell})

        self._update_cur_row(points.row_itog + 1)

    def format_for_returns(self):
        """
        Костыль, правящий форматы для отчета по доходам
        :return: 
        """
        # Чутка правим форматы
        # frmt_cell1 = self._workbook.add_format({'bold': True})
        # frmt_cell1.set_align('right')
        self._worksheet.set_column(firstcol=0,
                                         lastcol=0, width=40)
        frmt_cell = self._workbook.add_format()
        frmt_cell.set_num_format(0x0e)
        self._worksheet.set_column(firstcol=5,
                                         lastcol=6, cell_format=frmt_cell)
        frmt_cell2 = self._workbook.add_format()
        frmt_cell2.set_num_format(0x00)
        self._worksheet.set_column(firstcol=7,
                                         lastcol=7, cell_format=frmt_cell2)

    def _get_chart_prop(self, points: TablePoints, name, header, addchart):
        """
        Get chart series properties.
        :param points:
        :param name:
        :param header:
        :param addchart:
        :return: chart series properties
        """
        chart_prop = {}

        if header:
            categories = "='{sheet}'!${start_col}${start_row}:${end_col}${end_row}". \
                format(sheet=self._sheet,
                       start_col=points.col_data_begin_l,
                       end_col=points.col_data_end_l,
                       start_row=points.row_begin + 1,
                       end_row=points.row_begin + 1)
            chart_prop['categories'] = categories
            if not self.common_categories:
                self.common_categories = categories

        values = "='{sheet}'!${start_col}${start_row}:${end_col}${end_row}". \
            format(sheet=self._sheet,
                   start_col=points.col_data_begin_l,
                   end_col=points.col_data_end_l,
                   start_row=points.row_itog + 1,
                   end_row=points.row_itog + 1)
        chart_prop['values'] = values
        chart_name = "='{sheet}'!${col}${row}".format(sheet=self._sheet, col=points.col_begin_l,
                                                      row=points.row_itog + 1)
        if name:
            chart_name = name
        chart_prop['name'] = chart_name
        chart_prop['type'] = addchart

        return chart_prop

    def add_empty_row(self):
        """
        Add empty row to current sheet
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
        """
        Add all charts on current sheet from self._charts
        :return:
        """
        for chart in self._charts:
            if ('categories' not in chart) and self.common_categories:
                chart['categories'] = self.common_categories

            ex_chart = self._workbook.add_chart({'type': chart['type']})
            # ex_chart = self._workbook.add_chart({'type': 'column'})
            ex_chart.add_series(chart)
            ex_chart.set_size({'x_scale': 2, 'y_scale': 1.5})
            self._worksheet.insert_chart(row=self._cur_row, col=1, chart=ex_chart)
            self._update_cur_row(self._cur_row + 23)

        self._charts = []

    def _header_to_list(self, dataframe, row=-1, margins=None):
        """
        Add header of DataFrame to list
        :param dataframe:
        :param row:
        :param margins:
        :return:
        """
        if row <= -1:
            row = self._cur_row
        frmt_date = self._workbook.add_format()
        frmt_date.set_num_format(self._datetime_format)
        frmt_date.set_bold()
        frmt_date.set_align('center')
        columns = dataframe.columns.tolist()

        idx_len = len(dataframe.index.names)

        header = {'row': row, 'col': idx_len, 'columns': columns}

        self._headers.append(header)

    def _add_headers(self):
        """
        Put all headers on current sheet
        :return:
        """
        if self._headers:
            for header in self._headers:
                self._add_header(header)
            self._headers = []

    def _add_header(self, header):
        """
        Put header to current sheet
        :param header: Dict with 'row', 'col', 'values'
        :return:
        """

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

    def add_dataframe_test(self, df:pandas.DataFrame, startcol=None, startrow=None, header=True, index=True,
                           header_format=None, index_format=None, float_format=None):
        if not self._worksheet:
            self._worksheet = self._workbook.add_worksheet()

        if not startrow:
            startrow = 0
        if not startcol:
            startcol = 0
        row = startrow
        # col = startcol


        # col = start_col
        if header:
            col = startcol
            if index:
                index_names = df.index.names
                self._append_line(index_names, row=row, col=col, cell_format=header_format)
                col += len(index_names)

            columns = df.columns.tolist()
            self._append_line(columns, row=row, col=col, cell_format=header_format)
            row += 1

        for idx, df_row in df.iterrows():
            col = startcol
            if index:
                if isinstance(idx, tuple):
                    self._append_line(idx, row, col, cell_format=index_format)
                    col += len(idx)
                else:
                    self._worksheet.write(row, col, idx, index_format)
                    col += 1

            # self._append_line(df_row, row, col, cell_format=self._format_value_currency)
            self._append_line(df_row, row, col, float_format=float_format)
            row += 1

    def _append_line(self, line, row, col, cell_format=None, float_format=None):
        # if isinstance(line, collections.Iterable):
        for value in line:
            if float_format and (isinstance(value, float) or isinstance(value, Decimal.decimal)):
                cur_format = float_format
            else:
                cur_format=cell_format
            # if isinstance(value, float):
            #     cur_format = self._format_value_d
            # print(type(value))
            self._worksheet.write(row, col, value, cur_format)
            col += 1
        # else:
        #     self._worksheet.write(row, col, line)


if __name__ == "__main__":
    line1 = [{'date': '01.01.2016', 'value': 10, 'account': 'Активы:Текущие:Карта', 'guid': '10', 'perc': 0.1},
             {'date': '02.01.2016', 'value': 50, 'account': 'Активы:Текущие:Карта', 'guid': '10', 'perc': 0.2},
             {'date': '01.02.2016', 'value': 100, 'account': 'Активы:Текущие:Карта', 'guid': '10', 'perc': 0.3},
             {'date': '05.02.2016', 'value': 100, 'account': 'Активы:Текущие:Карта', 'guid': '10', 'perc': 0.4},

             ]

    df = pandas.DataFrame(line1)
    df.set_index('date', append=True, inplace=True)
    xls = XLSXReport('v:/tables/test.xlsx')
    xls.add_dataframe_test(df)
    xls.save()