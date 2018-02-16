# import pandas

# from gnucashreport.report import Report, ReportInflation, ReportReturns

from gnucashreport import utils


# book = book(filename)
# reports = ReportSet()
# reports.fill_all(book.start, book.end) # reports.fill_complex(start,end,period='auto')
#
# out_report= OutputReportXLSX(book)
# out_report.fill(reports)
#
# out_report.write(outfile)
from gnucashreport.utils import complete_month


class ReportSet:
    """
    Set of reports objects by sheets

    >>> reports = ReportSet()
    >>> reports.add_sheet('Sheet1')
    >>> reports.add_report('report1')
    >>> reports.add_report('report2')
    >>> reports.add_sheet('sheet2')
    >>> reports.add_report('report1')
    >>> reports.add_report('report2')
    >>> reports.add_report('report3', sheet_name='Sheet1')
    >>> reports.get_sheet_names()
    ['Sheet1', 'sheet2']
    >>> reports.get_reports('Sheet1')
    ['report1', 'report2', 'report3']
    >>> reports.get_reports('sheet2')
    ['report1', 'report2']

    """

    def __init__(self):
        self._sheets = {}
        # self.reports = {}
        # self.last_report = None
        self._last_sheet_name = None

        # reports = [{'name': 'report1', 'df': ['df1','df2','df3']}]
        r = {'sheet1': ['report1', 'report2'], 'sheet2': ['report1', 'report2']}

    # def add_inflation(self, min_date, max_date, glevel):
    #     self.add_sheet(_('Inflation'))
    #     from_date, to_date = utils.complete_years_dates(min_date, max_date)
    #     cumulative = False
    #     report = ReportInflation(from_date=from_date, to_date=to_date, period='A', glevel=glevel, cumulative=cumulative)
    #     # report.add_chart()
    #     self.add_report(report)
    #
    #     cumulative = True
    #     report = ReportInflation(from_date=from_date, to_date=to_date, period='A', glevel=glevel, cumulative=cumulative)
    #     self.add_report(report)
    #
    #
    #
    # def add_complex(self, year=None):
    #     pass
    #
    # def add_returns(self, from_date, to_date):
    #     self.add_sheet(_('Returns'))
    #     report = ReportReturns(from_date=from_date, to_date=to_date)
    #     self.add_report(report)
    #     pass
    #
    # def add_all(self, min_date, max_date, glevel=1):
    #     pass
    #
    # def receive_data(self, raw_report):
    #     pass
    #



    def get_sheet_names(self):
        return list(self._sheets)

    def get_reports(self, sheet_name):
        return self._sheets[sheet_name]

    def add_sheet(self, sheet_name):
        if sheet_name not in self._sheets:
            self._sheets[sheet_name] = []
        self._last_sheet_name = sheet_name

    def add_reportset(self, reportset):

        # Add all sheets of reportset to me

        sheet_names = reportset.get_sheet_names()

        for sheet_name in sheet_names:
            reports = reportset.get_reports(sheet_name=sheet_name)
            for report in reports:
                self.add_report(report=report, sheet_name=sheet_name)

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





