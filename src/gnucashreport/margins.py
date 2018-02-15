
# TOTAL_NAME = 'Total'
# MEAN_NAME = 'Average'
# PROFIT_NAME = 'Profit'
# EQUITY_NAME = 'Equity'

class Margins:

    def __init__(self, total_row=False, total_col=False, mean_col=False,

                 empty_col=False):
        # self.total_name = total_name
        self.total_name = _('Total')
        # if total_name:
        #     self.total_name = total_name
        self.mean_name = _('Average')
        # if mean_name:
        # self.mean_name = _(mean_name)
        self.profit_name = _('Profit')
        self.equity_name = _('Equity')
        self.total_row = total_row
        self.total_col = total_col
        self.mean_col = mean_col
        self.empty_col = empty_col

    def set_for_turnover(self):
        self.total_row = True
        self.total_col = True
        self.mean_col = True
        self.empty_col = True

    def set_for_profit(self):
        self.total_row = False
        self.total_col = True
        self.mean_col = True
        self.empty_col = True

    def set_for_balances(self):
        self.total_row = True
        self.total_col = False
        self.mean_col = False

    def set_for_equity(self):
        self.total_row = False
        self.total_col = False
        self.mean_col = False

    def set_for_inflation(self, cumulative=False):
        self.total_row = True
        self.total_col = not cumulative

    def get_counts_vtotals(self):
        """
        Возвращает количество итоговых колонок вместе с пустой колонкой
        :return:
        """
        width = 0
        if self.total_col:
            width += 1
        if self.mean_col:
            width += 1
        if (self.total_col or self.mean_col) and self.empty_col:
            width += 1
        return width






