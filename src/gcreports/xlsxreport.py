import os

import pandas


class XLSXReport:

    default_dir_reports = 'U:/tables'

    def __init__(self, filename, sheet='Sheet1', datetime_format=None, start_row=0):
        self.filename = filename
        self.sheet = sheet
        self.worksheet = None
        self.writer = pandas.ExcelWriter(filename, engine='xlsxwriter', datetime_format=datetime_format)
        self.workbook = self.writer.book
        self.cur_row = start_row
        if datetime_format:
            self.datetime_format = datetime_format
        else:
            self.datetime_format = 'dd-mm-yyyy'

    def save(self):
        self.writer.save()

    @classmethod
    def dataframe_to_excel(cls, dataframe, filename, sheet='Sheet1', datetime_format=None):
        """
        Записывает dataFrame в excel. Указывать только имя файла без расширения!
        :param dataframe:
        :param filename: Указывать только имя файла без расширения
        :return:
        """
        if not filename.endswith('.xlsx'):
            filename = os.path.join(cls.default_dir_reports, filename + ".xlsx")

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer = pandas.ExcelWriter(filename, engine='xlsxwriter', datetime_format=datetime_format)
        # writer = pandas.ExcelWriter(filename, engine='openpyxl')
        # writer = pandas.ExcelWriter(filename)
        # workbook = writer.book
        # worksheet_wr = workbook.add_worksheet(sheet)
        # worksheet = workbook.create_sheet(title=sheet, index=0)

        # Convert the dataframe to an XlsxWriter Excel object.
        # dataframe.to_excel(writer, sheet_name=sheet)
        dataframe.to_excel(writer, sheet_name=sheet)

        # Get the xlsxwriter objects from the dataframe writer object.

        # worksheet = writer.sheets[sheet] # Так работает
        # worksheet = workbook.active # Так тоже работает

        # worksheet['A1'] = 'A1'

        # Close the Pandas Excel writer and output the Excel file.
        writer.save()

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

    def add_header(self, dataframe, row=-1):
        # Заголовок таблицы
        if row <= -1:
            row=self.cur_row
        frmt_date = self.workbook.add_format()
        frmt_date.set_num_format('mmm yyyy')
        frmt_date.set_bold()
        frmt_date.set_align('center')
        cols = dataframe.columns.tolist()
        i = len(dataframe.index.names)

        for col_name in cols:
            # self.worksheet.write(0, i, col, frmt_date)
            self.worksheet.write(row, i, col_name, frmt_date)
            i = i + 1
        # self.worksheet.write(0, col_count + 2, 'Всего', frmt_bold)
        # self.worksheet.write(0, col_count + 3, 'Среднее', frmt_bold)
        self._update_cur_row(row + 1)
        # self.cur_row = row + 1

    def add_dataframe(self, dataframe, color=None, name=None, row=None, header=True, margins=None):
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


            if margins.total_row:
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


        # col_count = len(dataframe.columns)

        # total itog
        # for i in range(1, col_count+1):
        #     sum1_cell = xl_rowcol_to_cell(row, i)
        #     sum2_cell = xl_rowcol_to_cell(itog_row-1, i)
        #     formula = '=SUM({}:{})'.format(sum1_cell, sum2_cell)
        #     worksheet.write_formula(itog_row, i, formula, frmt_head)

        # right itog sum
        # if h_total:
        #     for i in range(row, itog_row+1):
        #         sum1_cell = xl_rowcol_to_cell(i, 1)
        #         sum2_cell = xl_rowcol_to_cell(i, col_count)
        #         formula = '=SUM({}:{})'.format(sum1_cell, sum2_cell)
        #         worksheet.write_formula(i, col_count + 2, formula, cell_format=frmt_money)

            # right itog average
            # for i in range(row, itog_row + 1):
            #     sum1_cell = xl_rowcol_to_cell(i, 1)
                # sum_cell = xl_rowcol_to_cell(i, col_count+2)
                # formula = '={}/{}'.format(sum_cell, col_count)
                # worksheet.write_formula(i, col_count + 3, formula, cell_format=frmt_money)

        # Format money
        # self.worksheet.set_column(firstcol=1, lastcol=col_count + 1, cell_format=frmt_money)

        # Ширина первой колонки
        index_len = len(dataframe.index.names)
        # print(index_len)
        self.worksheet.set_column(firstcol=0, lastcol=index_len-1, width=25)
        self.worksheet.set_column(firstcol=index_len, lastcol=col_count, cell_format=frmt_money, width=12)

        if margins:
            if margins.empty_col:
                empty_col = col_count-width_totals_col
                # print(empty_col)
                self.worksheet.set_column(firstcol=empty_col, lastcol=empty_col, width=1)
                # self.worksheet.set_column(14, 14, width=5)



        # Ширина за последней колонкой
        # self.worksheet.set_column(firstcol=col_count + 1, lastcol=col_count + 1, width=3)
        # Ширина за последней последней колонкой
        # self.worksheet.set_column(firstcol=col_count + 2, lastcol=col_count + 3, width=12)

        # Format itog line
        # worksheet.conditional_format(first_row=itog_row, first_col=0,
        #                              last_row=itog_row, last_col=col_count,
        #                              options={'type': 'no_blanks', 'format': frmt_head})

        # self.cur_row = itog_row + 1
        self._update_cur_row(itog_row + 1)
        # return itog_row + 1

