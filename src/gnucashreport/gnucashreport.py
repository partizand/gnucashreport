import calendar
from datetime import date, datetime, timedelta

from gnucashreport.gnucashdata import GNUCashData
from gnucashreport.margins import Margins
from gnucashreport.xlsxreport import XLSXReport

from gnucashreport.utils import dataframe_to_excel, dataframe_to_html, dateformat_from_period

# ASSETS_NAME = 'Assets'

# EXPENSE_NAME = 'Expense'

# INCOME_NAME = 'Income'

COLOR_GREEN = '#92D050'
COLOR_GREEN_DARK = '#00B050'
COLOR_BLUE = '#00B0F0'
COLOR_YELLOW = '#FFFF00'
COLOR_ORANGE_LIGHT = '#FDE9D9'


class GNUCashReport(GNUCashData):
    """
    High level reports from GnuCash to Excel

    Example

    >>> import gnucashreport
    >>> gcrep = GNUCashReport()

    open sql book
    >>> gcrep.open_book_sql('v:/gnucash-base/sqlite/GnuCash-base.gnucash', open_if_lock=True)

    save reports by years in xlsx file
    >>> gcrep.all_reports_excel('v:/tables/ex-test.xlsx', glevel=1)

    """

    def __init__(self):
        super(GNUCashReport, self).__init__()
        # self.dataframe_to_excel = XLSXReport.dataframe_to_excel

    def cashflow_report_html(self, from_date, to_date, period='M', glevel=[0, 1]):
        """
        Test only
        :param from_date:
        :param to_date:
        :param period:
        :param glevel:
        :return:
        """
        margins = Margins()
        margins.set_for_turnover()
        margins.empty_col = True
        # dateformat = self._dateformat_from_period(period)

        # Income
        df_income = self.turnover_by_period(from_date=from_date, to_date=to_date, period=period,
                                            account_type=GNUCashData.INCOME,
                                            glevel=glevel, margins=margins)


        # expense
        df_expense = self.turnover_by_period(from_date=from_date, to_date=to_date, period=period,
                                             account_type=GNUCashData.EXPENSE,
                                             glevel=glevel, margins=margins)


        # profit
        margins.set_for_profit()
        df_profit = self.profit_by_period(from_date=from_date, to_date=to_date, period=period, glevel=glevel,
                                          margins=margins)

        df_itog = df_income.append(df_expense)
        df_itog = df_itog.append(df_profit)
        # self.dataframe_to_excel(df_itog, 'itog')
        dataframe_to_html(df_itog, 'itog')

        # print(df_itog)

    def all_reports_excel(self, filename, glevel=1):
        min_date = self.df_splits['post_date'].min()
        max_date = self.df_splits['post_date'].max()

        from_date, to_date = self._complete_month(min_date, max_date)

        years = self._split_by_years(from_date, to_date)

        xlsxreport = XLSXReport(filename=filename, datetime_format='M')
        # sheet on each year
        for start_date, end_date in years:
            xlsxreport.next_sheet(sheet=str(start_date.year))
            self._complex_report_writer(xlsxreport, start_date, end_date, period='M', glevel=glevel)

        # sheet by years
        full_years = self._complete_years(from_date, to_date)
        if full_years:
            start_year, end_year = full_years
            y_start_date = date(start_year, 1, 1)
            y_end_date = date(end_year, 12, 31)
            xlsxreport.next_sheet(sheet=_('All'), datetime_format='A')
            self._complex_report_writer(xlsxreport, from_date=y_start_date, to_date=y_end_date, period='A', glevel=glevel)
            # inflation
            xlsxreport.next_sheet(sheet=_('Inflation'), datetime_format='A')
            self._inflation_writer(xlsxreport, from_date=y_start_date, to_date=y_end_date, period='A', glevel=glevel)
        xlsxreport.save()
        return



    @staticmethod
    def _split_by_years(from_date: date, to_date: date):
        """
        Splits two dates interval on array of intervals by years

        >>> GNUCashReport._split_by_years(date(2014,1,2), date(2017, 1, 20))
        [[datetime.date(2014, 2, 1), datetime.date(2014, 12, 31)],\
 [datetime.date(2015, 1, 1), datetime.date(2015, 12, 31)],\
 [datetime.date(2016, 1, 1), datetime.date(2016, 12, 31)]]

        :param from_date:
        :param to_date:
        :return: Array of tuples date
        """
        dates = []
        from_date, to_date = GNUCashReport._complete_month(from_date, to_date)
        cur_year = from_date.year
        not_end_cycle = True
        while not_end_cycle:
            first_date = date(cur_year, 1, 1)
            end_date = date(cur_year, 12, 31)
            if first_date < from_date:
                first_date = from_date
            if end_date > to_date:
                end_date = to_date
                # end cycle
                not_end_cycle = False
            if first_date >= end_date:
                break
            dates.append([first_date, end_date])
            cur_year += 1

        return dates

    @staticmethod
    def _complete_years(from_date: date, to_date: date):
        """
        Возвращает начальный и конечный полные года интервала
        >>> GNUCashReport._complete_years(date(2016,1,2), date(2016,12,30))

        >>> GNUCashReport._complete_years(date(2008,12,31), date(2017, 2, 15))
        (2009, 2016)

        :param from_date:
        :param to_date:
        :return:
        """
        # Первая дата, выравниваем год
        from_year = from_date.year
        if not (from_date.month == 1 and from_date.day == 1):
            from_year += 1
            if from_year > date.today().year:
                return None

        to_year = to_date.year
        if not(to_date.month == 12 and to_date.day == 31):
            to_year -= 1

        if from_year > to_year:
            return None

        if from_year == to_year:
            return None

        return from_year, to_year

    @staticmethod
    def _complete_month(from_date: date, to_date: date):
        """
        Возвращает интервал дат выровненный по месяцам

        >>> GNUCashReport._complete_month(date(2016,1,2), date(2016,12,30))
        (datetime.date(2016, 2, 1), datetime.date(2016, 11, 30))
        >>> GNUCashReport._complete_month(date(2008,12,31), date(2017, 2, 15))
        (datetime.date(2009, 1, 1), datetime.date(2017, 1, 31))
        >>> GNUCashReport._complete_month(date(2008,12,31), date(2017, 1, 15))
        (datetime.date(2009, 1, 1), datetime.date(2016, 12, 31))

        :param from_date:
        :param to_date:
        :return:
        """
        # Первая дата, выравниваем на месяц
        new_from_date = from_date
        first_day = from_date.day
        if first_day != 1:
            new_from_date = GNUCashReport._add_months(from_date, 1)
            new_from_date = new_from_date.replace(day=1)

        # Вторая дата выравниваем на месяц
        new_to_date = to_date
        _, days_in_month = calendar.monthrange(to_date.year, to_date.month)
        if to_date.day != days_in_month:
            new_to_date = GNUCashReport._add_months(to_date, -1)
            _, new_days_in_month = calendar.monthrange(new_to_date.year, new_to_date.month)
            new_to_date = new_to_date.replace(day=new_days_in_month)

        return new_from_date,  new_to_date

    @staticmethod
    def _add_months(sourcedate: date, months):
        """
        Add month to date
        From
        http://stackoverflow.com/questions/4130922/how-to-increment-datetime-by-custom-months-in-python-without-using-library
        >>> GNUCashReport._add_months(date(2016,1,2), 1)
        datetime.date(2016, 2, 2)
        >>> GNUCashReport._add_months(date(2016,12,31), 1)
        datetime.date(2017, 1, 31)
        >>> GNUCashReport._add_months(date(2017,2,28), 1)
        datetime.date(2017, 3, 28)
        >>> GNUCashReport._add_months(date(2017,2,28), -1)
        datetime.date(2017, 1, 28)
        >>> GNUCashReport._add_months(date(2017,1,1), -1)
        datetime.date(2016, 12, 1)

        :param months:
        :return: datetime.date = sourcedate + months
        """

        month = sourcedate.month - 1 + months


        year = int(sourcedate.year + month / 12)

        month = month % 12 + 1

        day = min(sourcedate.day, calendar.monthrange(year, month)[1])

        return date(year, month, day)

    def inflation_excel(self, filename, from_date, to_date, period, glevel=1):


        xlsxreport = XLSXReport(filename=filename, datetime_format=period)

        self._inflation_writer(xlsxreport, from_date=from_date, to_date=to_date, period=period, glevel=glevel)

        xlsxreport.save()

    def complex_report_excel(self, filename, from_date, to_date, period, glevel=1):
        """
        Saves complex report by period to excel file
        Contains: income, expense, profit, assets, loans, equity and chart equity
        :param filename: Excel file name
        :param from_date:
        :param to_date:
        :param period:
        :param glevel:
        :return:
        """

        xlsxreport = XLSXReport(filename=filename, datetime_format=period)

        self._complex_report_writer(xlsxreport, from_date=from_date, to_date=to_date, period=period, glevel=glevel)

        xlsxreport.save()

    def _inflation_writer(self, xlsxreport:XLSXReport, from_date, to_date, period, glevel):
        margins = Margins()
        margins.set_for_inflation(cumulative=False)
        df_inf = self.inflation_by_period(from_date=from_date, to_date=to_date, period=period,
                                          glevel=glevel, cumulative=False)
        xlsxreport.add_dataframe(df_inf, name=_('Inflation annual'), margins=margins, color=COLOR_YELLOW,
                                 num_format=XLSXReport.PERCENTAGE_FORMAT, addchart='line')
        xlsxreport.add_empty_row()

        margins.set_for_inflation(cumulative=True)
        df_inf = self.inflation_by_period(from_date=from_date, to_date=to_date, period=period,
                                          glevel=glevel, cumulative=True)
        xlsxreport.add_dataframe(df_inf, name=_('Inflation cumulative'), margins=margins, color=COLOR_YELLOW,
                                 num_format=XLSXReport.PERCENTAGE_FORMAT, addchart='line')


    def _complex_report_writer(self, xlsxreport:XLSXReport, from_date, to_date, period, glevel):
        """
        Saves complex report by period to excel file
        Contains: income, expense, profit, assets, loans, equity and chart equity
        :param filename: Excel file name
        :param from_date:
        :param to_date:
        :param period:
        :param glevel:
        :return:
        """

        margins = Margins()
        margins.set_for_turnover()
        margins.empty_col = True
        # filename = 'v:/tables/ex-test.xlsx'
        # glevel = 1
        # dateformat = self._dateformat_from_period(period)
        # xlsxreport = XLSXReport(filename=filename, datetime_format=period)

        # Income
        df_income = self.turnover_by_period(from_date=from_date, to_date=to_date, period=period, account_type=GNUCashData.INCOME,
                                                glevel=glevel, margins=margins)
        xlsxreport.add_dataframe(df_income, name=_('Income'), color=COLOR_GREEN, header=True, margins=margins)
        xlsxreport.add_empty_row()

        # expense
        df_expense = self.turnover_by_period(from_date=from_date, to_date=to_date, period=period, account_type=GNUCashData.EXPENSE,
                                                 glevel=glevel, margins=margins)
        xlsxreport.add_dataframe(df_expense, name=_('Expense'), color=COLOR_YELLOW, header=True, margins=margins)
        xlsxreport.add_empty_row()

        # profit
        margins.set_for_profit()
        df_profit = self.profit_by_period(from_date=from_date, to_date=to_date, period=period, glevel=glevel, margins=margins)
        xlsxreport.add_dataframe(df_profit, color=COLOR_GREEN_DARK, header=False, margins=margins)
        xlsxreport.add_empty_row()

        # assets
        margins.set_for_balances()
        df_assets = self.balance_by_period(from_date=from_date, to_date=to_date, period=period, glevel=glevel, margins=margins)
        xlsxreport.add_dataframe(df_assets, color=COLOR_BLUE, name=_('Assets'), header=True, margins=margins)
        xlsxreport.add_empty_row()

        # loans
        margins.total_row = False
        df_loans = self.balance_by_period(from_date=from_date, to_date=to_date, period=period, glevel=0,
                                              account_types=[GNUCashData.LIABILITY],
                                              margins=margins)
        has_loans = not (df_loans.isnull().values.all())
        if has_loans:
            xlsxreport.add_dataframe(df_loans, color=COLOR_ORANGE_LIGHT, header=False, margins=margins)
            xlsxreport.add_empty_row()

        # equity
        df_profit = self.equity_by_period(from_date=from_date, to_date=to_date, period=period, glevel=glevel, margins=margins)
        xlsxreport.add_dataframe(df_profit, color=COLOR_BLUE, header=False, margins=margins, addchart='column')
        xlsxreport.add_empty_row()

        # margins.set_for_turnover()
        # xlsxreport.add_header(df_income, row=0, margins=margins)

        # xlsxreport.save()
