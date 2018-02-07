import pandas

class ReportSet:
    """
    Set of reports for formating in xlsx, html, etc

    >>> reports = ReportSet()
    >>> reports.add_report('report_name')
    >>> df = pandas.DataFrame()
    >>> reports.last_report.add_df(df)
    >>> len(reports.get_report('report_name').dfs)
    1
    """

    def __init__(self):
        self.reports = {}
        self.last_report = None

        reports = [{'name': 'report1', 'df': ['df1','df2','df3']}]

    def add_report(self, name):
        self.last_report = Report(name)
        self.reports[name] = self.last_report

    def get_report(self, name=None):
        """

        :param name:
        :return:Report: Report object
        """
        if name is None:
            return self.last_report
        else:
            return self.reports[name]


class Report:
    def __init__(self, name):
        self.name = name
        self.dfs = []

    def add_df(self, df):
        self.dfs.append(df)
