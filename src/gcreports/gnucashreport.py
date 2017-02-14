from gcreports.gnucashdata import GNUCashData
from gcreports.margins import Margins
from gcreports.xlsxreport import XLSXReport


class GNUCashReport(GNUCashData):

    def complex_report_excel(self, filename, from_date, to_date, period='M', glevel=1):

        margins = Margins()
        margins.set_for_turnover()
        margins.empty_col = True
        # filename = 'v:/tables/ex-test.xlsx'
        # glevel = 1
        dateformat = self._dateformat_from_period(period)
        xlsxreport = XLSXReport(filename=filename, datetime_format=dateformat)

        # Income
        df_income = self.turnover_by_period(from_date=from_date, to_date=to_date, period=period, account_type=GNUCashData.INCOME,
                                                glevel=glevel, margins=margins)
        xlsxreport.add_dataframe(df_income, name='Доходы', color='green', header=False, margins=margins, row=1)
        xlsxreport.add_empty_row()

        # expense
        df_expense = self.turnover_by_period(from_date=from_date, to_date=to_date, period=period, account_type=GNUCashData.EXPENSE,
                                                 glevel=glevel, margins=margins)
        xlsxreport.add_dataframe(df_expense, name='Расходы', color='yellow', header=False, margins=margins)
        xlsxreport.add_empty_row()

        # profit
        margins.set_for_profit()
        df_profit = self.profit_by_period(from_date=from_date, to_date=to_date, period=period, glevel=glevel, margins=margins)
        xlsxreport.add_dataframe(df_profit, color='red', header=False, margins=margins)
        xlsxreport.add_empty_row()

        # assets
        margins.set_for_balances()
        df_assets = self.balance_by_period(from_date=from_date, to_date=to_date, period=period, glevel=glevel, margins=margins)
        xlsxreport.add_dataframe(df_assets, color='green', name='Активы', header=False, margins=margins)
        xlsxreport.add_empty_row()

        # loans
        margins.total_row = False
        df_loans = self.balance_by_period(from_date=from_date, to_date=to_date, period=period, glevel=0,
                                              account_types=GNUCashData.LIABILITY,
                                              margins=margins)
        xlsxreport.add_dataframe(df_loans, color='yellow', header=False, margins=margins)
        xlsxreport.add_empty_row()

        # equity
        # margins.set_for_profit()
        df_profit = self.equity_by_period(from_date=from_date, to_date=to_date, period=period, glevel=glevel, margins=margins)
        xlsxreport.add_dataframe(df_profit, color='green', header=False, margins=margins, addchart=True)
        xlsxreport.add_empty_row()

        # xlsxreport.add_chart()

        margins.set_for_turnover()
        xlsxreport.add_header(df_income, row=0, margins=margins)
        # xlsxreport.add_empty_row()
        # xlsxreport.add_dataframe(df)
        # xlsxreport.set_cell_format()
        # xlsxreport.add_df_test(df)

        xlsxreport.save()

