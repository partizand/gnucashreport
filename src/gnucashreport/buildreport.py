from gnucashreport.gnucashbook import GNUCashBook
from gnucashreport.gnucashdata import GNUCashData
from gnucashreport.margins import Margins
from gnucashreport.report import Report
from gnucashreport import utils
from gnucashreport.reportset import ReportSet


class BuildReport:

    def __init__(self, raw_data: GNUCashData):
        self._raw_data = raw_data

    def get_report_inflation(self, from_date=None, to_date=None, period='A', glevel=1, cumulative=False):

        if from_date and to_date:
            start_date = from_date
            end_date = to_date
            # local_period = 'A'
        else:
            start_date, end_date = utils.complete_years_dates(self._raw_data.min_date, self._raw_data.max_date)
            # local_period = 'A'

        df_data = self._raw_data.inflation_by_period(from_date=start_date, to_date=end_date, period=period,
                                        cumulative=cumulative, glevel=glevel)

        if cumulative:
            report_name = _('Inflation cumulative')
        else:
            report_name = _('Inflation annual')

        margins = Margins()
        margins.set_for_inflation(cumulative)


        report = Report(report_name=report_name, df_data=df_data, period=period, margins=margins)

        return report

    def get_reportset_inflation(self, sheet_name, glevel):
        reportset = ReportSet()
        reportset.add_sheet(sheet_name=sheet_name)
        report = self.get_report_inflation(glevel=glevel, cumulative=False)
        reportset.add_report(report)
        report = self.get_report_inflation(glevel=glevel, cumulative=True)
        reportset.add_report(report)
        return reportset

    def get_report_return(self, from_date=None, to_date=None):
        df_data = self._raw_data.yield_calc(from_date=from_date, to_date=to_date)
        report_name = _('Return on assets (per annum)')
        report = Report(report_name=report_name, df_data=df_data, period='', margins=None)
        return report

    def get_report_income(self, from_date, to_date, period, glevel=1):

        margins = Margins()
        margins.set_for_turnover()

        report_name = _('Income')

        df_data = self._raw_data.turnover_by_period(from_date=from_date, to_date=to_date, period=period,
                                                    account_type=GNUCashBook.INCOME, glevel=glevel)

        report = Report(report_name=report_name, df_data=df_data, period=period, margins=margins)

        return report

    def get_reportset_complex(self, sheet_name, from_date, to_date, period, glevel):
        reportset = ReportSet()

        reportset.add_sheet(sheet_name=sheet_name)

        report = self.get_report_income(from_date=from_date, to_date=to_date, period=period, glevel=glevel)
        reportset.add_report(report)

        return reportset

    def get_reportset_all(self, glevel=1):

        reportset = ReportSet()

        from_date, to_date = utils.complete_month(self._raw_data.min_date, self._raw_data.max_date)

        years = utils.split_by_years(from_date, to_date)

        # sheet on each year
        for start_date, end_date in years:
            sheet_name = "{year}".format(year=str(start_date.year))
            reportset_sheet = self.get_reportset_complex(sheet_name=sheet_name, from_date=start_date, to_date=end_date,
                                                         period='M', glevel=glevel)
            reportset.add_reportset(reportset_sheet)



        # sheet by years
        # full_years = utils.complete_years(from_date, to_date)
        years_border_dates = utils.complete_years_dates(from_date, to_date)

        if years_border_dates:
            # start_year, end_year = full_years
            # y_start_date = date(start_year, 1, 1)
            # y_end_date = date(end_year, 12, 31)

            y_start_date, y_end_date = years_border_dates

            sheet_name = _('All')

            reportset_sheet = self.get_reportset_complex(sheet_name=sheet_name, from_date=y_start_date,
                                                         to_date=y_end_date,
                                                         period='A', glevel=glevel)
            reportset.add_reportset(reportset_sheet)


            # inflation
            sheet_name=_('Inflation')
            reportset_sheet = self.get_reportset_inflation(sheet_name=sheet_name, glevel=glevel)
            reportset.add_reportset(reportset_sheet)

        # ROE
        report = self.get_report_return()
        reportset.add_sheet(sheet_name=_('Returns'))
        reportset.add_report(report)

        return reportset

