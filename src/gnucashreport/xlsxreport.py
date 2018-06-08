import collections

import datetime
import pandas
from decimal import Decimal

import xlsxwriter
from xlsxwriter.utility import xl_col_to_name

from gnucashreport.formatreport import get_format_xlsx
from gnucashreport.margins import Margins
from gnucashreport.report import Report
from gnucashreport.reportset import ReportSet


class XLSXReport:
    """
    Output Report, ReportSet and DataFrame to formatted Excel file

    >>> from gnucashreport.buildreport import BuildReport
    >>> from gnucashreport.rawdata import RawData
    >>> bookfile_sql = 'v:/gnucash-base/sqlite/GnuCash-base.gnucash'
    >>> raw_data = RawData(bookfile_sql)
    >>> builder = BuildReport(raw_data)
    >>> reportset = builder.get_reportset_all(glevel=1)
    >>> out_filename = 'v:/tables/ex-test.xlsx'
    >>> outputer_excel = XLSXReport(out_filename)
    >>> outputer_excel.add_reportset(reportset)
    >>> outputer_excel.close()

    """


    default_dir_reports = 'V:/tables'

    CHART_COLUMN = 'column'
    CHART_LINE = 'line'

    MONEY_FORMAT = 0x08
    # MONEY_FORMAT = 0x08
    # MONEY_FORMAT = '# ##0,00'
    # MONEY_FORMAT = '# ##,##'
    PERCENTAGE_FORMAT = 0x0a

    def __init__(self, filename, sheet_name=None, start_row=0):

        self.workbook = xlsxwriter.Workbook(filename, {'nan_inf_to_errors': True})
        self._common_categories = None
        self._worksheet = None
        # self._sheet_name = sheet_name
        self._charts = []
        if sheet_name:
            self._add_sheet(sheet_name=sheet_name, start_row=start_row)

    def add_reportset(self, reportset:ReportSet):
        # Перебрать reportset и вывести отчеты
        sheet_names = reportset.get_sheet_names()
        for sheet_name in sheet_names:
            reports = reportset.get_reports(sheet_name)
            self._add_sheet(sheet_name)
            for report in reports:
                format_xlsx = get_format_xlsx(report, self.workbook)
                self._add_report(report.df_data, format_xlsx, addchart=report.chart_type)
                self._add_empty_row()

    def add_dataframe(self, dataframe, sheet_name='Sheet1'):

        report = Report(report_name='', report_type='', df_data=dataframe, period='D', margins=Margins())

        reportset = ReportSet()
        reportset.add_report(report, sheet_name=sheet_name)
        self.add_reportset(reportset)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """
        Add charts of current sheet and save file
        :return:
        """
        self._add_charts()
        self.workbook.close()

    def _add_sheet(self, sheet_name=None, start_row=0):
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

    def _add_report(self, report: pandas.DataFrame, format_report, start_row=None, addchart=None):

        chart_prop = self._add_dataframe(report, format_report, startrow=start_row, startcol=0)

        if addchart:
            chart_prop['type'] = addchart
            self._charts.append(chart_prop)

    def _add_dataframe(self, df: pandas.DataFrame, format_report, startcol=None, startrow=None):
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
                self._worksheet.set_column(first_col=col, last_col=col + len(index_names) - 1,
                                           width=format_report.index_width)
                # Добавление названий индексов на лист
                self._append_line(index_names, row=row, col=col, cell_format=format_report.format_header)
                col += len(index_names)

            # Названия полей
            columns = df.columns.tolist()
            # Установка ширины колонок полей
            self._worksheet.set_column(first_col=col, last_col=col + len(columns) - 1,
                                       width=format_report.column_width)

            # Ширина итоговых колонок
            if format_report.margins.empty_col:
                self._worksheet.set_column(first_col=col + len(columns) - vtotals, last_col=col + len(columns) - vtotals,
                                           width=format_report.empty_width)
                self._worksheet.set_column(first_col=col + len(columns) - vtotals+1, last_col=col + len(columns),
                                           width=format_report.total_width)
            elif vtotals > 0:
                self._worksheet.set_column(first_col=col + len(columns) - vtotals, last_col=col + len(columns),
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
                vtotal_format = format_report.format_itog
            else:
                float_format = format_report.format_float
                format_index = format_report.format_index
                cell_format = None
                vtotal_format = format_report.format_itog_col
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

            self._append_line(df_row, row, col,
                              float_format=float_format,
                              date_format=format_report.format_date,
                              cell_format=cell_format,
                              vtotals=vtotals,
                              vtotal_format=vtotal_format)

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

    def _add_empty_row(self):
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
                self._add_empty_row()
                if ('categories' not in chart) and self._common_categories:
                    chart['categories'] = self._common_categories

                ex_chart = self.workbook.add_chart({'type': chart['type']})
                ex_chart.add_series(chart)
                ex_chart.set_size({'x_scale': 2, 'y_scale': 1.5})
                self._worksheet.insert_chart(row=self._cur_row, col=1, chart=ex_chart)
                self._update_cur_row(self._cur_row + 23)

            self._charts = None

    def _append_line(self, line, row, col,
                     cell_format=None,
                     float_format=None,
                     date_format=None,
                     vtotals=None, vtotal_format=None):
        if vtotals:
            col_totals_start = col + len(line) - vtotals - 1
        for value in line:

            if float_format and (isinstance(value, float) or isinstance(value, Decimal)):
                cur_format = float_format
            elif date_format and isinstance(value, datetime.date):
                cur_format = date_format
            else:
                cur_format=cell_format

            if vtotals and col > col_totals_start:
                cur_format = vtotal_format

            self._worksheet.write(row, col, value, cur_format)
            col += 1


