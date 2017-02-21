import pandas
from xlsxwriter.utility import xl_col_to_name

from gnucashreport.utils import dateformat_from_period


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
    PERCENTAGE_FORMAT = 0x0a

    def __init__(self, filename, sheet='Sheet1', datetime_format=None, start_row=0):
        # self.filename = filename
        # self._sheet = sheet
        # self._worksheet = None
        self._datetime_format = dateformat_from_period(datetime_format)
        self._writer = pandas.ExcelWriter(filename, engine='xlsxwriter', datetime_format=datetime_format)
        self._workbook = self._writer.book
        # self._cur_row = start_row
        # self._charts = []
        # self._headers = []
        # self.common_categories = None
        self._some_init(sheet=sheet, start_row=start_row, datetime_format=datetime_format)

    def save(self):
        """
        Add charts of current sheet and save file
        :return:
        """
        self._add_headers()
        self._add_charts()
        self._writer.save()

    def next_sheet(self, sheet, start_row=0, datetime_format=None):
        """
        Next data will be on this new sheet
        :param sheet:
        :param start_row:
        :return:
        """
        self._add_headers()
        self._add_charts()
        # self._sheet = sheet
        # self._cur_row = start_row
        # self._worksheet = None
        # self.common_categories = None
        # if datetime_format:
        #     self._datetime_format = dateformat_from_period(datetime_format)
        self._some_init(sheet=sheet, start_row=start_row, datetime_format=datetime_format)

    def _some_init(self, sheet, start_row, datetime_format):
        self._sheet = sheet
        self._worksheet = None
        if datetime_format:
            self._datetime_format = dateformat_from_period(datetime_format)
        self._cur_row = start_row
        self._charts = []
        self._headers = []
        self.common_categories = None

    def add_dataframe(self, dataframe, color=None, name=None, row=None, header=True, margins=None, addchart=None,
                      num_format=MONEY_FORMAT):
        """
        Add DataFrame on current sheet, update next position to down
        :param dataframe:
        :param color:
        :param name:
        :param row:
        :param header: Show DataFrame header
        :param margins:
        :param addchart: must be type of chart: 'column', 'line'. See xlsxwriter help
        :param num_format: cell format number for data
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
        frmt_money = self._workbook.add_format()
        frmt_money.set_num_format(num_format)
        frmt_head = self._workbook.add_format({'bold': True})
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
                                                   options={'type': 'no_blanks',
                                                            'format': frmt_head})
                self._worksheet.conditional_format(first_row=points.row_itog,
                                                   last_row=points.row_itog,
                                                   first_col=points.col_begin,
                                                   last_col=points.col_all_end,
                                                   options={'type': 'blanks',
                                                            'format': frmt_head})
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
                                                   options={'type': 'no_blanks',
                                                            'format': frmt_bold})
                # Ширина колонк с итогами
                if points.col_totals_begin and points.col_totals_end:
                    self._worksheet.set_column(firstcol=points.col_totals_begin, lastcol=points.col_totals_end,
                                               cell_format=frmt_money,
                                               width=15)

        # index_len = len(dataframe.index.names)
        # Ширина первой колонки
        self._worksheet.set_column(firstcol=points.col_begin, lastcol=points.col_head_end, width=25)
        # Ширина колонок до итогов
        self._worksheet.set_column(firstcol=points.col_data_begin,
                                   lastcol=points.col_data_end,
                                   cell_format=frmt_money, width=12)

        self._update_cur_row(points.row_itog + 1)

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
