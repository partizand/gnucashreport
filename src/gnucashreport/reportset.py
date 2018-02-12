# import pandas

from gnucashreport.report import Report





# book = book(filename)
# reports = ReportSet()
# reports.fill_all(book.start, book.end) # reports.fill_complex(start,end,period='auto')
#
# out_report= OutputReportXLSX(book)
# out_report.fill(reports)
#
# out_report.write(outfile)

class ReportSet:
    """
    Set of reports objects by sheets

    >>> reports = ReportSet()
    >>> reports.add_sheet('Sheet1')
    >>> reports._sheets
    {'Sheet1': []}
    >>> reports.add_report('report1')
    >>> reports.sheets
    {'Sheet1': ['report1']}
    >>> reports.add_report('report2')
    >>> reports.add_sheet('sheet2')
    >>> reports.add_report('report1')
    >>> reports.add_report('report2')
    >>> reports.sheets
    {'Sheet1': ['report1', 'report2'], 'sheet2': ['report1', 'report2']}
    >>> reports.add_report('report3', sheet_name='Sheet1')
    >>> reports.sheets
    {'Sheet1': ['report1', 'report2', 'report3'], 'sheet2': ['report1', 'report2']}
    """

    def __init__(self):
        self._sheets = {}
        # self.reports = {}
        # self.last_report = None
        self._last_sheet_name = None

        # reports = [{'name': 'report1', 'df': ['df1','df2','df3']}]
        r = {'sheet1': ['report1', 'report2'], 'sheet2': ['report1', 'report2']}

    def get_sheet_names(self):
        return list(self._sheets)

    def get_reports(self, sheet_name):
        return self._sheets[sheet_name]

    def add_sheet(self, sheet_name):
        if sheet_name not in self._sheets:
            self._sheets[sheet_name] = []
        self._last_sheet_name = sheet_name

    def add_report(self, report, sheet_name=None):

        if sheet_name:
            sheet_to_add = sheet_name
            if sheet_name not in self._sheets:
                self.add_sheet(sheet_name)
        else:
            sheet_to_add = self._last_sheet_name
            if not self._last_sheet_name:
                sheet_to_add = 'Sheet1'
                self.add_sheet(sheet_to_add)

        (self._sheets[sheet_to_add]).append(report)





