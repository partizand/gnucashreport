from gcreports.xlsxreport.excelreport import ExcelReport


class XLSXWReport(ExcelReport):
    """
    Reports from dataframe to Excel based on xlsxwriter
    """

    def __init__(self, filename, sheet='Sheet1', template_file=None):
        super(XLSXWReport, self).__init__(filename=filename, sheet=sheet, engine='openpyxl')
