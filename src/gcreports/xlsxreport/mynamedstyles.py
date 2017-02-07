from gcreports.xlsxreport.cellstyle import CellStyle
from openpyxl import load_workbook


class MyNamedStyles:

    def __init__(self, template_file=None):
        self.template_filename = template_file
        self.styles = {}
        if template_file:
            self._read_styles()

    def _read_styles(self):
        template_wb = load_workbook(self.template_filename)
        sheet_styles = template_wb['styles']
        self.styles = {}
        for row in sheet_styles.rows:
            for cell in row:
                comment = cell.comment
                if comment:
                    self.styles[comment.text] = CellStyle(cell)

    def set_style(self, cell, style_name):
        style = self.get_style(style_name)
        if style:
            style.set_on_cell(cell)

    def get_style(self, style_name):
        if style_name in self.styles:
            return(self.styles[style_name])
        else:
            return None
