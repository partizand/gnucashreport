from gnucashreport.gnucashbook import GNUCashBook
from gnucashreport.rawdata import RawData
from gnucashreport.margins import Margins
from gnucashreport.report import Report
from gnucashreport import utils
from gnucashreport.reportset import ReportSet


class BuildReport:
    """Build high level reports"""
    def __init__(self, raw_data: RawData):
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
            report_type = Report.Type.INFLATION_CUM
        else:
            report_name = _('Inflation annual')
            report_type = Report.Type.INFLATION_ANNUAL

        margins = Margins()
        margins.set_for_inflation(cumulative)

        report = Report(report_name=report_name, report_type=report_type, df_data=df_data, period=period, margins=margins)
        return report

    def get_reportset_inflation(self, sheet_name, glevel):
        reportset = ReportSet()
        reportset.add_sheet(sheet_name=sheet_name)
        report = self.get_report_inflation(glevel=glevel, cumulative=False)
        report.add_chart(Report.ChartType.Line)
        reportset.add_report(report)
        report = self.get_report_inflation(glevel=glevel, cumulative=True)
        report.add_chart(Report.ChartType.Line)
        reportset.add_report(report)
        return reportset

    def get_report_return(self, from_date=None, to_date=None):
        df_data = self._raw_data.yield_calc(from_date=from_date, to_date=to_date)
        report_name = _('Return on assets (per annum)')
        report = Report(report_name=report_name, report_type=Report.Type.RETURNS, df_data=df_data, period='', margins=None)
        return report

    def get_report_income(self, from_date, to_date, period, glevel):

        margins = Margins()
        margins.set_for_turnover()

        report_name = _('Income')

        df_data = self._raw_data.turnover_by_period(from_date=from_date, to_date=to_date, period=period,
                                                    account_type=GNUCashBook.INCOME, margins=margins, glevel=glevel)

        report = Report(report_name=report_name, report_type=Report.Type.INCOME, df_data=df_data, period=period, margins=margins)

        return report

    def get_report_expense(self, from_date, to_date, period, glevel):

        margins = Margins()
        margins.set_for_turnover()
        report_name = _('Expense')
        account_type = GNUCashBook.EXPENSE

        df_data = self._raw_data.turnover_by_period(from_date=from_date,
                                             to_date=to_date,
                                             period=period,
                                             account_type=account_type,
                                             margins=margins,
                                             glevel=glevel)

        report = Report(report_name=report_name, report_type=Report.Type.EXPENSE, df_data=df_data, period=period,
                        margins=margins)

        return report

    def get_report_profit(self, from_date, to_date, period, glevel):

        margins = Margins()
        margins.set_for_profit()
        report_name = _('Profit')

        df_data = self._raw_data.profit_by_period(from_date=from_date,
                                             to_date=to_date,
                                             period=period,
                                             margins=margins,
                                           glevel=glevel)

        report = Report(report_name=report_name, report_type=Report.Type.PROFIT, df_data=df_data, period=period,
                        margins=margins)

        return report

    def get_report_assets(self, from_date, to_date, period, glevel):
        margins = Margins()
        margins.set_for_balances()
        report_name = _('Assets')
        account_type = GNUCashBook.ALL_ASSET_TYPES

        df_data = self._raw_data.balance_by_period(from_date=from_date,
                                             to_date=to_date,
                                             period=period,
                                             account_types=account_type,
                                             margins=margins,
                                             glevel=glevel)

        report = Report(report_name=report_name, report_type=Report.Type.ASSETS, df_data=df_data, period=period,
                        margins=margins)

        return report

    def get_report_loans(self, from_date, to_date, period, glevel=1):
        margins = Margins()
        margins.set_for_balances()
        report_name = _('Loans')
        account_type = [GNUCashBook.LIABILITY]

        df_data = self._raw_data.balance_by_period(from_date=from_date,
                                             to_date=to_date,
                                             period=period,
                                             account_types=account_type,
                                             margins=margins,
                                            glevel=glevel)

        report = Report(report_name=report_name, report_type=Report.Type.LOANS, df_data=df_data, period=period,
                        margins=margins)

        return report

    def get_report_equity(self, from_date, to_date, period):
        margins = Margins()
        margins.set_for_equity()
        report_name = _('Equity')

        df_data = self._raw_data.equity_by_period(from_date=from_date,
                                             to_date=to_date,
                                             period=period,
                                             margins=margins)

        report = Report(report_name=report_name, report_type=Report.Type.EQUITY, df_data=df_data, period=period,
                        margins=margins)

        return report

    def get_reportset_complex(self, sheet_name, from_date, to_date, period, glevel):
        reportset = ReportSet()

        reportset.add_sheet(sheet_name=sheet_name)
        # Income
        report = self.get_report_income(from_date=from_date, to_date=to_date, period=period, glevel=glevel)
        reportset.add_report(report)
        # Expense
        report = self.get_report_expense(from_date=from_date, to_date=to_date, period=period, glevel=glevel)
        reportset.add_report(report)
        # Profit
        report = self.get_report_profit(from_date=from_date, to_date=to_date, period=period, glevel=glevel)
        reportset.add_report(report)
        # Assets
        report = self.get_report_assets(from_date=from_date, to_date=to_date, period=period, glevel=glevel)
        reportset.add_report(report)
        # Loans
        report = self.get_report_assets(from_date=from_date, to_date=to_date, period=period, glevel=0)
        if not report.is_data_empty(): # May be add this rule to add_report function of reportset?
            reportset.add_report(report)
        # equity
        report = self.get_report_equity(from_date=from_date, to_date=to_date, period=period)
        report.add_chart(Report.ChartType.Column)
        reportset.add_report(report)
        # Returns
        report = self.get_report_return(from_date=from_date, to_date=to_date)
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
        sheet_name = _('Returns')
        report = self.get_report_return()
        reportset.add_sheet(sheet_name=sheet_name)
        reportset.add_report(report)

        return reportset

