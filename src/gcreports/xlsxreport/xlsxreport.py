from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from gcreports.xlsxreport.mynamedstyles import MyNamedStyles
import clipboard as clp

class XlSXReport:

    def __init__(self, filename, sheet='Sheet1', template_file=None):
        self.styles = MyNamedStyles(template_file)
        self.filename = filename
        self.workbook = Workbook()
        self.worksheet = self.workbook.active
        self.worksheet.title = sheet

    def save(self):
        self.workbook.save(self.filename)

    def _rows_to_sheet(self, rows, name, start_row=2, start_col=1, header=False, index=True):
        head = True
        col_head = True
        frmt_header = self.styles.get_style(name)
        # Заголовок
        if frmt_header:
            ce = self.worksheet.cell(row=start_row-1, column=start_col, value=frmt_header.value)
            frmt_header.set_on_cell(ce)

        for r_idx, row in enumerate(rows, start_row):
            col_head = True
            for c_idx, value in enumerate(row, start_col):
                ce = self.worksheet.cell(row=r_idx, column=c_idx, value=value)
                if head and header:
                    self.styles.set_style(ce, name)
                col_head = False
            head = False


    def add_df_clipboard(self, df):
        # Copy dataframe to clipboard
        df.to_clipboard()
        # paste the clipboard to a valirable
        cells = clp.paste()
        # split text in varialble as rows and columns
        cells = [x.split() for x in cells.split('\n')]

        # Open the work book
        wb = openpyxl.load_workbook('H:/template.xlsx')
        # Get the Sheet
        sheet = wb.get_sheet_by_name('spam')
        sheet.title = 'df data'
        # Paste clipboard values to the sheet
        for i, r in zip(range(1, len(cells)), cells):
            for j, c in zip(range(1, len(r)), r):
                sheet.cell(row=i, column=j).value = c
        # Save the workbook
        wb.save('H:/df_out.xlsx')

    def add_df_test(self, datafarame):
        for r in dataframe_to_rows(datafarame, index=True, header=True):
            # if type(r) == tuple:
            #     r =
            self.worksheet.append(r)

    def add_dataframe(self, dataframe, name, start_row=2, start_col=1, header=False, index=True):

        rows = dataframe_to_rows(dataframe, index=index, header=header)
        head = True
        col_head = True
        frmt_header = self.styles.get_style(name)
        # Заголовок
        if frmt_header:
            ce = self.worksheet.cell(row=start_row - 1, column=start_col, value=frmt_header.value)
            frmt_header.set_on_cell(ce)

        for r_idx, row in enumerate(rows, start_row):
            col_head = True
            for c_idx, value in enumerate(row, start_col):
                if value:
                    ce = self.worksheet.cell(row=r_idx, column=c_idx, value=str(value))
                    ce = self.worksheet.cell(row=r_idx, column=c_idx, value=str(value))
                    if head and header:
                        self.styles.set_style(ce, name)
                col_head = False
            head = False