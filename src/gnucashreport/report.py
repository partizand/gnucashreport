from gnucashreport.gnucashbook import GNUCashBook
from gnucashreport.gnucashdata import GNUCashData
from gnucashreport.margins import Margins


class Report:
    # report types
    INFLATION = 'inflation'
    RETURNS = 'returns'
    INCOME = 'income'
    EXPENSE = 'expense'
    PROFIT = 'profit'
    ASSETS = 'assets'
    LOANS = 'loans'
    EQUITY = 'equity'

    def __init__(self, rep_type, from_date, to_date, period, glevel):
        self.rep_type = rep_type
        self.df = None
        # low level report info
        self.from_date = from_date
        self.to_date = to_date
        self.period = period
        self.account_types = None
        self.glevel = glevel
        # format
        self.report_name = rep_type
        # empty margins
        self.margins = Margins()
        self._format()

    def _format(self):
        if self.rep_type == self.ASSETS:
            self.report_name = _('Assets')
            self.account_types = GNUCashBook.ALL_ASSET_TYPES
            # self.total_row = True
            # self.total_col = False
            # self.mean_col = False
            self.margins.set_for_balances()

        elif self.rep_type == self.INCOME:
            self.report_name = _('Income')
            self.margins.set_for_turnover()
            self.account_types = GNUCashBook.INCOME

    def build(self, gcreport:GNUCashData):
        if self.rep_type == self.ASSETS:
            self.df = gcreport.balance_by_period(from_date=self.from_date,
                                                to_date=self.to_date,
                                                period=self.period,
                                                account_types=self.account_types,
                                                margins=self.margins,
                                                glevel=self.glevel)
        elif self.rep_type == self.INCOME:
            self.df = gcreport.turnover_by_period(from_date=self.from_date,
                                                 to_date=self.to_date,
                                                 period=self.period,
                                                 account_type=self.account_types,
                                                 margins=self.margins,
                                                 glevel=self.glevel)




