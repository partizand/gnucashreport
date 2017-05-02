import collections
import pandas
from decimal import Decimal

import xlsxwriter
from xlsxwriter.utility import xl_col_to_name

from gnucashreport.margins import Margins
# from gnucashreport.formatreport import FormatReport, FormatBalance, FormatIncome
from gnucashreport.tablepoints import TablePoints

# from gnucashreport.utils import dateformat_from_period

COLOR_GREEN = '#92D050'
COLOR_GREEN_DARK = '#00B050'
COLOR_BLUE = '#00B0F0'
COLOR_YELLOW = '#FFFF00'
COLOR_ORANGE_LIGHT = '#FDE9D9'


class XLSXReport:
    default_dir_reports = 'V:/tables'

    CHART_COLUMN = 'column'
    CHART_LINE = 'line'


    MONEY_FORMAT = 0x08
    # MONEY_FORMAT = 0x08
    # MONEY_FORMAT = '# ##0,00'
    # MONEY_FORMAT = '# ##,##'
    PERCENTAGE_FORMAT = 0x0a




    def __init__(self, filename, sheet_name=None, start_row=0):
        # self.filename = filename
        # self._sheet = sheet
        # self._worksheet = None
        # self._datetime_format = dateformat_from_period(datetime_format)
        # self._writer = pandas.ExcelWriter(filename, engine='xlsxwriter', datetime_format=self._datetime_format)
        self.workbook = xlsxwriter.Workbook(filename)
        self._common_categories = None
        self._worksheet = None
        # self._sheet_name = sheet_name
        self._charts = []
        if sheet_name:
            self.add_sheet(sheet_name=sheet_name, start_row=start_row)
        # self._worksheet = self._workbook.add_worksheet(sheet)

        # Test


        # self._some_init(sheet=sheet, start_row=start_row, datetime_format=datetime_format)
        # self._set_formats()

    def close(self):
        """
        Add charts of current sheet and save file
        :return:
        """
        # self._add_headers()
        self._add_charts()
        self.workbook.close()
        # _writer.save()

    def add_sheet(self, sheet_name=None, start_row=0):
        """
        Next data will be on this new sheet
        :param sheet_name:
        :param start_row:
        :return:
        """
        # self._add_headers()
        self._add_charts()
        self._worksheet = self.workbook.add_worksheet(sheet_name)
        self._sheet_name = self._worksheet.get_name()
        self._common_categories = None
        self._cur_row = start_row
        self._charts = []
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

    # def _set_formats(self):
    #     # Заголовки таблиц
    #     self._format_header = self._workbook.add_format({'bold': True})
    #     self._format_header.set_align('center')
    #     self._format_index_left = self._workbook.add_format({'bold': True})
    #     self._format_index_center = self._workbook.add_format({'bold': True})
    #     self._format_index_center.set_align('center')
    #     self._format_itog = self._workbook.add_format({'bold': True})
    #     self._format_itog.set_align('center')
    #     # Значение в валюте
    #     self._format_value_currency = self._workbook.add_format()
    #     self._format_value_currency.set_num_format(self.MONEY_FORMAT)
    #     # Значение в процентах
    #     self._format_value_perc = self._workbook.add_format()
    #     self._format_value_perc.set_num_format(self.PERCENTAGE_FORMAT)
    #     # Формат доходов
    #     self._format_income = self._workbook.add_format({'bold': True})
    #     self._format_income.set_bg_color(COLOR_GREEN)

    def add_report(self, report: pandas.DataFrame, format_report, start_row=None, addchart=None):


        # if start_row:
        #     row = start_row
        # else:
        #     row = self._cur_row

        # points = TablePoints(dataframe=report, header=header, margins=margins, row=row)

        # format_report = cls_format(self.workbook, format_date)
        chart_prop = self.add_dataframe(report, format_report, startrow=start_row, startcol=0)
        # chart_prop = self._get_chart_prop(points=points, name=name, header=header, addchart=addchart)

        if addchart:
            chart_prop['type'] = addchart
            self._charts.append(chart_prop)





        # self._update_cur_row(points.row_itog + 1)

    def add_dataframe(self, df: pandas.DataFrame, format_report, startcol=None, startrow=None):
        """
        Adds dataframe on current sheet
        :param df: 
        :param format_report: 
        :param startcol: 
        :param startrow: 
        :return: 
        """

        if not startrow:
            startrow = self._cur_row
        if not startcol:
            startcol = 0
        row = startrow
        vtotals = format_report.margins.get_counts_vtotals()

        chart_prop = {}

        if format_report.show_header:
            col = startcol
            if format_report.show_index:
                # Имена индексов
                index_names = df.index.names
                # Установка ширины колонок индексов
                self._worksheet.set_column(firstcol=col, lastcol=col + len(index_names) - 1,
                                           width=format_report.index_width)
                # Добавление названий индексов на лист
                self._append_line(index_names, row=row, col=col, cell_format=format_report.format_header)
                col += len(index_names)

            # Названия полей
            columns = df.columns.tolist()
            # Установка ширины колонок полей
            self._worksheet.set_column(firstcol=col, lastcol=col + len(columns) - 1,
                                       width=format_report.column_width)

            # Ширина итоговых колонок
            if format_report.margins.empty_col:
                self._worksheet.set_column(firstcol=col + len(columns) - vtotals, lastcol=col + len(columns) - vtotals,
                                           width=format_report.empty_width)
                self._worksheet.set_column(firstcol=col + len(columns) - vtotals+1, lastcol=col + len(columns),
                                           width=format_report.total_width)
            elif vtotals > 0:
                self._worksheet.set_column(firstcol=col + len(columns) - vtotals, lastcol=col + len(columns),
                                           width=format_report.total_width)
            # Добавление категорий в свойства графика
            categories = "='{sheet}'!${start_col}${start_row}:${end_col}${end_row}". \
                format(sheet=self._sheet_name,
                       start_col=xl_col_to_name(col),
                       end_col=xl_col_to_name(col + len(columns)-1 - vtotals),
                       start_row=row+1,
                       end_row=row+1)
            chart_prop['categories'] = categories
            if not self._common_categories:
                self._common_categories = categories

            # Добавление названий полей на лист
            self._append_line(columns, row=row, col=col, cell_format=format_report.format_header)
            row += 1



        last_row = row + len(df) - 1

        for idx, df_row in df.iterrows():
            col = startcol
            # Если последняя строка, меняем формат
            if row == last_row and (format_report.margins.total_row):
                float_format = format_report.format_itog
                format_index = format_report.format_itog
                cell_format = format_report.format_itog
            else:
                float_format = format_report.format_float
                format_index = format_report.format_index
                cell_format = None
            # Отображение индекса
            if format_report.show_index:
                if isinstance(idx, tuple):
                    self._append_line(idx, row, col, cell_format=format_index)
                    col += len(idx)
                else:
                    self._worksheet.write(row, col, idx, format_index)
                    col += 1

            # Если последняя строка, запоминаем ее данные для графика
            if row == last_row:
                values = "='{sheet}'!${start_col}${start_row}:${end_col}${end_row}". \
                    format(sheet=self._sheet_name,
                           start_col=xl_col_to_name(col),
                           end_col=xl_col_to_name(col + len(df_row)-1-format_report.margins.get_counts_vtotals()),
                           start_row=row+1,
                           end_row=row+1)
                chart_prop['values'] = values

            # Отображение данных
            self._append_line(df_row, row, col, float_format=float_format, cell_format=cell_format, vtotal_format=format_report.format_itog_col)

            row += 1

        # Отбражение имени отчета
        if format_report.report_name:
            self._worksheet.write(startrow, startcol, format_report.report_name, format_report.format_name)
            # Добавление имени в график
            chart_name = "='{sheet}'!${col}${row}".format(sheet=self._sheet_name,
                                                          col=xl_col_to_name(startcol),
                                                          row=startrow+1)
            chart_prop['name'] = chart_name

        self._update_cur_row(row)
        return chart_prop

    # def _get_chart_prop(self, points: TablePoints, name, header, addchart):
    #     """
    #     Get chart series properties.
    #     :param points:
    #     :param name:
    #     :param header:
    #     :param addchart:
    #     :return: chart series properties
    #     """
    #     chart_prop = {}
    #
    #     if header:
    #         categories = "='{sheet}'!${start_col}${start_row}:${end_col}${end_row}". \
    #             format(sheet=self._sheet,
    #                    start_col=points.col_data_begin_l,
    #                    end_col=points.col_data_end_l,
    #                    start_row=points.row_begin + 1,
    #                    end_row=points.row_begin + 1)
    #         chart_prop['categories'] = categories
    #         if not self.common_categories:
    #             self.common_categories = categories
    #
    #     values = "='{sheet}'!${start_col}${start_row}:${end_col}${end_row}". \
    #         format(sheet=self._sheet,
    #                start_col=points.col_data_begin_l,
    #                end_col=points.col_data_end_l,
    #                start_row=points.row_itog + 1,
    #                end_row=points.row_itog + 1)
    #     chart_prop['values'] = values
    #     chart_name = "='{sheet}'!${col}${row}".format(sheet=self._sheet, col=points.col_begin_l,
    #                                                   row=points.row_itog + 1)
    #     if name:
    #         chart_name = name
    #     chart_prop['name'] = chart_name
    #     chart_prop['type'] = addchart
    #
    #     return chart_prop

    # def add_dataframe_old(self, dataframe, color=None, name=None, row=None, header=True, margins=None, addchart=None,
    #                   cell_format=None):
    #     """
    #     Add DataFrame on current sheet, update next position to down
    #     :param dataframe:
    #     :param color:
    #     :param name:
    #     :param row:
    #     :param header: Show DataFrame header
    #     :param margins:
    #     :param addchart: must be type of chart: 'column', 'line'. See xlsxwriter help
    #     :param cell_format: cell format number for data
    #     :return:
    #     """
    #
    #     if not row:
    #         row = self._cur_row
    #
    #     points = TablePoints(dataframe=dataframe, header=header, margins=margins, row=row)
    #
    #     chart_prop = self._get_chart_prop(points=points, name=name, header=header, addchart=addchart)
    #
    #     if header:
    #         self._header_to_list(dataframe, row, margins)
    #         if not self.common_categories:
    #             self.common_categories = chart_prop['categories']
    #
    #     if addchart:
    #         self._charts.append(chart_prop)
    #
    #     dataframe.to_excel(self._writer, sheet_name=self._sheet, startrow=points.row_data_begin, header=False)
    #     # Get the xlsxwriter objects from the dataframe writer object.
    #     if not self._worksheet:
    #         self._worksheet = self._writer.sheets[self._sheet]
    #
    #     frmt_bold = self._workbook.add_format({'bold': True})
    #     frmt_cell = self._workbook.add_format()
    #     if cell_format:
    #         frmt_cell.set_num_format(cell_format)
    #     frmt_cell_bold = self._workbook.add_format({'bold': True})
    #     if cell_format:
    #         frmt_cell_bold.set_num_format(cell_format)
    #     frmt_head = self._workbook.add_format({'bold': True})
    #     if cell_format:
    #         frmt_head.set_num_format(cell_format)
    #     frmt_head.set_align('center')
    #     if color:
    #         frmt_head.set_bg_color(color)
    #
    #     if name:
    #         # self._worksheet.write(df_start_row - 1, 0, name, frmt_head)
    #         self._worksheet.write(row, 0, name, frmt_head)
    #
    #     # Выделение итогов
    #     # width_totals_col = 0
    #
    #     if margins:
    #         # Выделение строки с итогами
    #         if (margins.total_row) or (len(dataframe) == 1 and color):
    #             self._worksheet.conditional_format(first_row=points.row_itog,
    #                                                last_row=points.row_itog,
    #                                                first_col=points.col_begin,
    #                                                last_col=points.col_all_end,
    #                                                options={'type': 'no_errors',
    #                                                         'format': frmt_head})
    #             # self._worksheet.conditional_format(first_row=points.row_itog,
    #             #                                    last_row=points.row_itog,
    #             #                                    first_col=points.col_begin,
    #             #                                    last_col=points.col_all_end,
    #             #                                    options={'type': 'blanks',
    #             #                                             'format': frmt_head})
    #         if margins.total_col or margins.mean_col:
    #             # Ширина пустой колонки
    #             if margins.empty_col:
    #                 # empty_col = self.col_count-width_totals_col
    #                 self._worksheet.set_column(firstcol=points.col_empty, lastcol=points.col_empty, width=1)
    #             # Итоговые колонки жирным
    #             self._worksheet.conditional_format(first_row=points.row_data_begin,
    #                                                last_row=points.row_itog,
    #                                                first_col=points.col_totals_begin,
    #                                                # col_count - width_totals_col + 1,
    #                                                last_col=points.col_totals_end,
    #                                                options={'type': 'no_errors',
    #                                                         'format': frmt_cell_bold})
    #             # Ширина колонк с итогами
    #             if points.col_totals_begin and points.col_totals_end:
    #                 self._worksheet.set_column(firstcol=points.col_totals_begin, lastcol=points.col_totals_end,
    #                                            cell_format=frmt_cell,
    #                                            width=15)
    #
    #
    #
    #     # index_len = len(dataframe.index.names)
    #     # Ширина первой колонки
    #     self._worksheet.set_column(firstcol=points.col_begin, lastcol=points.col_head_end, width=25)
    #     # Ширина колонок до итогов
    #     self._worksheet.set_column(firstcol=points.col_data_begin,
    #                                lastcol=points.col_data_end, width=12, #)
    #                                cell_format=frmt_cell)
    #
    #     # Формат ячеек с данными
    #     # self._worksheet.conditional_format(first_row=points.row_data_begin,
    #     #                                    last_row=points.row_itog,
    #     #                                    first_col=points.col_data_begin,
    #     #                                    last_col=points.col_data_end,
    #     #                                    options={'type': 'no_errors',
    #     #                                             'format': frmt_cell})
    #
    #     self._update_cur_row(points.row_itog + 1)

    # def format_for_returns(self):
    #     """
    #     Костыль, правящий форматы для отчета по доходам
    #     :return:
    #     """
    #     # Чутка правим форматы
    #     # frmt_cell1 = self._workbook.add_format({'bold': True})
    #     # frmt_cell1.set_align('right')
    #     self._worksheet.set_column(firstcol=0,
    #                                      lastcol=0, width=40)
    #     frmt_cell = self._workbook.add_format()
    #     frmt_cell.set_num_format(0x0e)
    #     self._worksheet.set_column(firstcol=5,
    #                                      lastcol=6, cell_format=frmt_cell)
    #     frmt_cell2 = self._workbook.add_format()
    #     frmt_cell2.set_num_format(0x00)
    #     self._worksheet.set_column(firstcol=7,
    #                                      lastcol=7, cell_format=frmt_cell2)



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
        if self._charts:
            for chart in self._charts:
                self.add_empty_row()
                if ('categories' not in chart) and self._common_categories:
                    chart['categories'] = self._common_categories

                ex_chart = self.workbook.add_chart({'type': chart['type']})
                # ex_chart = self._workbook.add_chart({'type': 'column'})
                ex_chart.add_series(chart)
                ex_chart.set_size({'x_scale': 2, 'y_scale': 1.5})
                self._worksheet.insert_chart(row=self._cur_row, col=1, chart=ex_chart)
                self._update_cur_row(self._cur_row + 23)

            self._charts = None

    # def _header_to_list(self, dataframe, row=-1, margins=None):
    #     """
    #     Add header of DataFrame to list
    #     :param dataframe:
    #     :param row:
    #     :param margins:
    #     :return:
    #     """
    #     if row <= -1:
    #         row = self._cur_row
    #     frmt_date = self._workbook.add_format()
    #     frmt_date.set_num_format(self._datetime_format)
    #     frmt_date.set_bold()
    #     frmt_date.set_align('center')
    #     columns = dataframe.columns.tolist()
    #
    #     idx_len = len(dataframe.index.names)
    #
    #     header = {'row': row, 'col': idx_len, 'columns': columns}
    #
    #     self._headers.append(header)
    #
    # def _add_headers(self):
    #     """
    #     Put all headers on current sheet
    #     :return:
    #     """
    #     if self._headers:
    #         for header in self._headers:
    #             self._add_header(header)
    #         self._headers = []
    #
    # def _add_header(self, header):
    #     """
    #     Put header to current sheet
    #     :param header: Dict with 'row', 'col', 'values'
    #     :return:
    #     """
    #
    #     frmt_date = self._workbook.add_format()
    #     frmt_date.set_num_format(self._datetime_format)
    #     frmt_date.set_bold()
    #     frmt_date.set_align('center')
    #
    #     cols = header['columns']
    #
    #     col = header['col']
    #     row = header['row']
    #
    #     for col_name in cols:
    #         self._worksheet.write(row, col, col_name, frmt_date)
    #         col += 1
    #


    def _append_line(self, line, row, col, cell_format=None, float_format=None, vtotals=None, vtotal_format=None):
        # if isinstance(line, collections.Iterable):
        if vtotals:
            col_totals_start = col + len(line) - vtotals
        for value in line:

            if float_format and (isinstance(value, float) or isinstance(value, Decimal)):
                cur_format = float_format
            else:
                cur_format=cell_format

            if vtotals and col_totals_start < col:
                cur_format = vtotal_format
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

    # gcrep = GCReport()
    # _ = lambda x: x
    df = pandas.DataFrame(line1)
    # df.set_index('date', append=True, inplace=True)
    xls = XLSXReport('v:/tables/test.xlsx')
    # format_report = FormatReport()
    xls.add_report(df, FormatIncome, 'dd-mm-yyyy')
    xls.close()