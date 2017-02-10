import os

import pandas


class ExcelReport:
    """
    Reports from dataframe to Excel Abstract class
    """

    default_dir_reports = 'U:/tables'

    def __init__(self, filename, sheet='Sheet1', engine=None):
        self.filename = filename
        self.sheet = sheet
        # self.workbook = None
        self.worksheet = None
        # self.writer = None
        self.writer = pandas.ExcelWriter(filename, engine=engine)
        self.workbook = self.writer.book
        self.engine = engine

    def save(self):
        self.writer.save()

    @staticmethod
    def dataframe_to_writer(dataframe, writer, sheet='Sheet1'):

        dataframe.to_excel(writer, sheet_name=sheet)

    @classmethod
    def dataframe_to_excel(cls, dataframe, filename, sheet='Sheet1'):
        """
        Записывает dataFrame в excel. Указывать только имя файла без расширения!
        :param dataframe:
        :param filename: Указывать только имя файла без расширения
        :return:
        """
        if not filename.endswith('.xlsx'):
            filename = os.path.join(cls.default_dir_reports, filename + ".xlsx")

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        # writer = pandas.ExcelWriter(filename, engine='xlsxwriter', datetime_format="mmm yyyy")
        # writer = pandas.ExcelWriter(filename, engine='openpyxl')
        writer = pandas.ExcelWriter(filename)
        workbook = writer.book
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
