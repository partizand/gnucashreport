

from gnucashreport.report import Report


class OutputReport():

    def __init__(self, gcreport, reportset=None):
        self._gcreport = gcreport
        self._reportset = reportset

    def fill_reportset(self, reportset):
        self._reportset = reportset

    def fill_reportset_all(self):
        pass

    def fill_reportset_complex(self, start_date, end_date):
        pass

    def fill_reportset_inflation(self, start_date, end_date, cumulative=False):
        report = Report(Report.INFLATION)
        rep_format = formatreport.FormatInflation(xlsxreport.workbook, cumulative=False)

        # margins = Margins()
        # margins.set_for_inflation(cumulative=False)
        df_inf = self.inflation(from_year=from_year, to_year=to_year, glevel=glevel, cumulative=rep_format.cumulative)

        xlsxreport.add_report(df_inf, rep_format, addchart=xlsxreport.CHART_LINE)

        # xlsxreport.add_dataframe(df_inf, color=COLOR_YELLOW, name=_('Inflation annual'), margins=margins,
        #                          addchart='line', cell_format=XLSXReport.PERCENTAGE_FORMAT)
        xlsxreport.add_empty_row()

        rep_format = formatreport.FormatInflation(xlsxreport.workbook, cumulative=True)
        # margins.set_for_inflation(cumulative=True)
        df_inf = self.inflation(from_year=from_year, to_year=to_year, glevel=glevel, cumulative=rep_format.cumulative)
        # xlsxreport.add_dataframe(df_inf, color=COLOR_YELLOW, name=_('Inflation cumulative'), margins=margins,
        #                          addchart='line', cell_format=XLSXReport.PERCENTAGE_FORMAT)

        xlsxreport.add_report(df_inf, rep_format, addchart=xlsxreport.CHART_LINE)

    def write(self, filename):
        pass