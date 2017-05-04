from datetime import date, datetime, timedelta

from gnucashreport import formatreport, utils
from gnucashreport.gnucashdata import GNUCashData
from gnucashreport.xlsxreport import XLSXReport


# from gnucashreport.utils import dataframe_to_excel, dataframe_to_html, dateformat_from_period

# COLOR_GREEN = '#92D050'
# COLOR_GREEN_DARK = '#00B050'
# COLOR_BLUE = '#00B0F0'
# COLOR_YELLOW = '#FFFF00'
# COLOR_ORANGE_LIGHT = '#FDE9D9'


class GCReport(GNUCashData):
    """
    High level reports from GnuCash to Excel

    Example

    # >>> import gnucashreport
    >>> gcrep = GCReport()

    open sql or xml book
    >>> gcrep.open_book_file('v:/gnucash-base/sqlite/GnuCash-base.gnucash', open_if_lock=True)

    save reports by years in xlsx file
    >>> gcrep.all_reports_excel('v:/tables/ex-test.xlsx', glevel=1)

    """

    def __init__(self):
        super(GCReport, self).__init__()

    # def cashflow_report_html(self, from_date, to_date, period='M', glevel=[0, 1]):
    #     """
    #     Test only
    #     :param from_date:
    #     :param to_date:
    #     :param period:
    #     :param glevel:
    #     :return:
    #     """
    #     margins = Margins()
    #     margins.set_for_turnover()
    #     margins.empty_col = True
    #     # dateformat = self._dateformat_from_period(period)
    #
    #     # Income
    #     df_income = self.turnover_by_period(from_date=from_date, to_date=to_date, period=period,
    #                                         account_type=GNUCashData.INCOME,
    #                                         glevel=glevel, margins=margins)
    #
    #     # expense
    #     df_expense = self.turnover_by_period(from_date=from_date, to_date=to_date, period=period,
    #                                          account_type=GNUCashData.EXPENSE,
    #                                          glevel=glevel, margins=margins)
    #
    #     # profit
    #     margins.set_for_profit()
    #     df_profit = self.profit_by_period(from_date=from_date, to_date=to_date, period=period, glevel=glevel,
    #                                       margins=margins)
    #
    #     df_itog = df_income.append(df_expense)
    #     df_itog = df_itog.append(df_profit)
    #     # self.dataframe_to_excel(df_itog, 'itog')
    #     dataframe_to_html(df_itog, 'itog')

        # print(df_itog)

    def all_reports_excel(self, filename, glevel=1):
        """
        Save all reports into xlsx file
        This report contain:

        - Income, expense, profit, assets, loans, equity by months each year (sheet on each year)
        - Income, expense, profit, assets, loans, equity by years on each full year
        - Inflation (annual expenditure growth)
        - Some charts

        :param filename: path to xlsx file
        :param glevel: Level account number or list for grouping. See glevel explain in readme.rst
        :return:
        """

        # min_date, max_date = self._get_daterange()

        # min_date = self.df_splits['post_date'].min()
        # max_date = self.df_splits['post_date'].max()

        from_date, to_date = utils.complete_month(self.min_date, self.max_date)

        years = utils.split_by_years(from_date, to_date)

        xlsxreport = XLSXReport(filename=filename)
        # sheet on each year
        for start_date, end_date in years:
            xlsxreport.add_sheet(sheet_name="{year}".format(year=str(start_date.year)))
            self._complex_report_writer(xlsxreport, start_date, end_date, period='M', glevel=glevel)

        # sheet by years
        full_years = utils.complete_years(from_date, to_date)
        if full_years:
            start_year, end_year = full_years
            y_start_date = date(start_year, 1, 1)
            y_end_date = date(end_year, 12, 31)
            xlsxreport.add_sheet(sheet_name=_('All'))
            self._complex_report_writer(xlsxreport, from_date=y_start_date, to_date=y_end_date, period='A',
                                        glevel=glevel)
            # inflation
            xlsxreport.add_sheet(sheet_name=_('Inflation'))
            self._inflation_writer(xlsxreport, glevel=glevel)

        # ROE
        xlsxreport.add_sheet(sheet_name=_('Returns'))
        self._returns_writer(xlsxreport)

        xlsxreport.close()
        return





    def inflation_excel(self, filename, from_year=None, to_year=None, glevel=1):
        """
        Saves inflation report by period to excel file
        :param filename:
        :param from_date:
        :param to_date:
        :param period:
        :param glevel:
        :return:
        """

        xlsxreport = XLSXReport(filename=filename, sheet_name=_('Inflation'))

        self._inflation_writer(xlsxreport, from_year=from_year, to_year=to_year, glevel=glevel)

        xlsxreport.close()

    def complex_report_excel(self, filename, from_date, to_date, period, glevel=1):
        """
        Saves complex report by period to excel file
        Contains: income, expense, profit, assets, loans, equity and chart equity
        :param filename: Excel file name
        :param from_date:
        :param to_date:
        :param period: Split into 'M' - months, 'A' - years, 'W' - weeks. See pandas freq
        :param glevel:
        :return:
        """

        xlsxreport = XLSXReport(filename=filename)

        self._complex_report_writer(xlsxreport, from_date=from_date, to_date=to_date, period=period, glevel=glevel)

        xlsxreport.close()

    def returns_report_excel(self, filename, from_date=None, to_date=None):
        """
        Saves returns report to excel file
        :param filename: Excel file name
        :param from_date:
        :param to_date:
        :return:
        """

        xlsxreport = XLSXReport(filename=filename, sheet_name='_Returns')

        self._returns_writer(xlsxreport, from_date=from_date, to_date=to_date)

        xlsxreport.close()

    def _returns_writer(self, xlsxreport: XLSXReport, from_date=None, to_date=None):
        df_xirr = self.yield_calc(from_date=from_date, to_date=to_date)
        rep_format = formatreport.FormatReturns(xlsxreport.workbook, from_date=from_date, to_date=to_date)
        # if from_date and to_date:
        #     header = _('Return on assets (per annum) {from_date} - {to_date}').\
        #         format(from_date=from_date, to_date=to_date)
        # else:
        #     header = _('Return on assets (per annum)')
        xlsxreport.add_report(df_xirr,rep_format)
        # xlsxreport.add_dataframe(df_xirr, name=header, cell_format=XLSXReport.PERCENTAGE_FORMAT, color=COLOR_YELLOW)
        # xlsxreport.format_for_returns()

    def _inflation_writer(self, xlsxreport: XLSXReport, from_year=None, to_year=None, glevel=1):
        """
        Save inflation report to excel writer
        :param xlsxreport:
        :param from_date:
        :param to_date:
        :param period:
        :param glevel:
        :return:
        """

        # if not from_date:
        #     from_date = self.min_date
        # if not to_date:
        #     to_date = self.max_date
        # full_years = utils.complete_years(from_date, to_date)
        # if full_years:
        #     start_year, end_year = full_years
        #     y_start_date = date(start_year, 1, 1)
        #     y_end_date = date(end_year, 12, 31)
        # else:
        #     return
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

    def _complex_report_writer(self, xlsxreport: XLSXReport, from_date, to_date, period, glevel):

        # Income
        format_rep = formatreport.FormatIncome(xlsxreport.workbook, period=period)
        df_balance = self.turnover_by_period(from_date=from_date,
                                              to_date=to_date,
                                              period=format_rep.period,
                                              account_type=format_rep.account_types,
                                              margins=format_rep.margins,
                                             glevel=glevel)
        xlsxreport.add_report(df_balance, format_rep)
        xlsxreport.add_empty_row()

        # expense
        format_rep = formatreport.FormatExpense(xlsxreport.workbook, period=period)
        df_balance = self.turnover_by_period(from_date=from_date,
                                             to_date=to_date,
                                             period=format_rep.period,
                                             account_type=format_rep.account_types,
                                             margins=format_rep.margins,
                                             glevel=glevel)
        xlsxreport.add_report(df_balance, format_rep)
        xlsxreport.add_empty_row()

        # profit
        format_rep = formatreport.FormatProfit(xlsxreport.workbook, period=period)
        df_balance = self.profit_by_period(from_date=from_date,
                                             to_date=to_date,
                                             period=format_rep.period,
                                             margins=format_rep.margins,
                                           glevel=glevel)
        xlsxreport.add_report(df_balance, format_rep)
        xlsxreport.add_empty_row()

        # assets
        format_rep = formatreport.FormatAssets(xlsxreport.workbook, period=period)
        df_balance = self.balance_by_period(from_date=from_date,
                                             to_date=to_date,
                                             period=format_rep.period,
                                             account_types=format_rep.account_types,
                                             margins=format_rep.margins,
                                             glevel=glevel)
        xlsxreport.add_report(df_balance, format_rep)
        xlsxreport.add_empty_row()

        # loans
        format_rep = formatreport.FormatLoans(xlsxreport.workbook, period=period)
        df_balance = self.balance_by_period(from_date=from_date,
                                             to_date=to_date,
                                             period=format_rep.period,
                                             account_types=format_rep.account_types,
                                             margins=format_rep.margins,
                                            glevel=0)
        # has_loans = not (df_balance.isnull().values.all())
        has_loans = not all((df_balance == 0).all())
        if has_loans:
            xlsxreport.add_report(df_balance, format_rep)
            xlsxreport.add_empty_row()

        # equity
        format_rep = formatreport.FormatEquity(xlsxreport.workbook, period=period)
        df_balance = self.equity_by_period(from_date=from_date,
                                             to_date=to_date,
                                             period=format_rep.period,
                                             margins=format_rep.margins)
        xlsxreport.add_report(df_balance, format_rep, addchart=xlsxreport.CHART_COLUMN)
        xlsxreport.add_empty_row()

        # Returns
        self._returns_writer(xlsxreport, from_date=from_date, to_date=to_date)


    # def _complex_report_writer_old(self, xlsxreport: XLSXReport, from_date, to_date, period, glevel):
    #     """
    #     Saves complex report by period to excel file
    #     Contains: income, expense, profit, assets, loans, equity and chart equity
    #     :param filename: Excel file name
    #     :param from_date:
    #     :param to_date:
    #     :param period:
    #     :param glevel:
    #     :return:
    #     """
    #
    #     margins = Margins()
    #     margins.set_for_turnover()
    #     margins.empty_col = True
    #     # filename = 'v:/tables/ex-test.xlsx'
    #     # glevel = 1
    #     # dateformat = self._dateformat_from_period(period)
    #     # xlsxreport = XLSXReport(filename=filename, datetime_format=period)
    #
    #     # Income
    #     df_income = self.turnover_by_period(from_date=from_date, to_date=to_date, period=period,
    #                                         account_type=GNUCashData.INCOME,
    #                                         glevel=glevel, margins=margins)
    #     xlsxreport.add_dataframe(df_income, color=COLOR_GREEN, name=_('Income'), header=True, margins=margins,
    #                              cell_format=XLSXReport.MONEY_FORMAT)
    #     xlsxreport.add_empty_row()
    #
    #     # expense
    #     df_expense = self.turnover_by_period(from_date=from_date, to_date=to_date, period=period,
    #                                          account_type=GNUCashData.EXPENSE,
    #                                          glevel=glevel, margins=margins)
    #     xlsxreport.add_dataframe(df_expense, color=COLOR_YELLOW, name=_('Expense'), header=True, margins=margins,
    #                              cell_format=XLSXReport.MONEY_FORMAT)
    #     xlsxreport.add_empty_row()
    #
    #     # profit
    #     margins.set_for_profit()
    #     df_profit = self.profit_by_period(from_date=from_date, to_date=to_date, period=period, glevel=glevel,
    #                                       margins=margins)
    #     xlsxreport.add_dataframe(df_profit, color=COLOR_GREEN_DARK, header=False, margins=margins,
    #                              cell_format=XLSXReport.MONEY_FORMAT)
    #     xlsxreport.add_empty_row()
    #
    #     # assets
    #     margins.set_for_balances()
    #     df_assets = self.balance_by_period(from_date=from_date, to_date=to_date, period=period, glevel=glevel,
    #                                        margins=margins)
    #     xlsxreport.add_dataframe(df_assets, color=COLOR_BLUE, name=_('Assets'), header=True, margins=margins,
    #                              cell_format=XLSXReport.MONEY_FORMAT)
    #     xlsxreport.add_empty_row()
    #
    #     # loans
    #     margins.total_row = False
    #     df_loans = self.balance_by_period(from_date=from_date, to_date=to_date, period=period, glevel=0,
    #                                       account_types=[GNUCashData.LIABILITY],
    #                                       margins=margins)
    #     has_loans = not (df_loans.isnull().values.all())
    #     if has_loans:
    #         xlsxreport.add_dataframe(df_loans, color=COLOR_ORANGE_LIGHT, header=False, margins=margins,
    #                                  cell_format=XLSXReport.MONEY_FORMAT)
    #         xlsxreport.add_empty_row()
    #
    #     # equity
    #     df_profit = self.equity_by_period(from_date=from_date, to_date=to_date, period=period, glevel=glevel,
    #                                       margins=margins)
    #     xlsxreport.add_dataframe(df_profit, color=COLOR_BLUE, header=False, margins=margins,
    #                              cell_format=XLSXReport.MONEY_FORMAT, addchart='column')
    #     xlsxreport.add_empty_row()
    #
    #
