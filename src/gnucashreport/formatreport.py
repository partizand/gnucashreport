import xlsxwriter.workbook
import xlsxwriter.worksheet
from gnucashreport import utils

from gnucashreport.margins import Margins
from gnucashreport.gnucashdata import GNUCashData
import gnucashreport.const as const

# COLOR_GREEN = '#92D050'
# COLOR_GREEN_DARK = '#00B050'
# COLOR_BLUE = '#00B0F0'
# COLOR_YELLOW = '#FFFF00'
# COLOR_ORANGE_LIGHT = '#FDE9D9'
from gnucashreport.tablepoints import TablePoints


class FormatReport:

    # MONEY_FORMAT = 0x08
    # PERCENTAGE_FORMAT = 0x0a

    def __init__(self, workbook: xlsxwriter.workbook):
        self._workbook = workbook
        # Базовые форматы ячеек для всех наследуемых объектов
        self._format_bold = workbook.add_format({'bold': True})
        self._format_bold_center = workbook.add_format({'bold': True, 'align': 'center'})
        self._format_currency = workbook.add_format({'num_format': const.MONEY_FORMAT})
        self._format_percent = workbook.add_format({'num_format': const.PERCENTAGE_FORMAT})
        self._format_date = workbook.add_format({'num_format': const.DAYDATE_FORMAT})
        # Описание текущего формата
        self.format_name = self._format_bold_center
        self.format_header = self._format_bold_center
        self.format_index = self._format_bold_center
        self.format_itog = self._format_bold
        self.format_itog_col = self._format_bold
        self.format_float = None
        self.format_date = self._format_date
        self.margins = Margins()
        self.show_header = True
        self.show_index = True
        self.report_name = None
        self.index_width = 25 # Ширина колонки
        self.column_width = 12
        self.total_width = 15
        self.empty_width = 1


class FormatBalance(FormatReport):

    def __init__(self, workbook: xlsxwriter.workbook, period):
        super(FormatBalance, self).__init__(workbook)
        self.period = period
        # self.from_date = from_date
        # self.to_date = to_date
        self.format_date = utils.dateformat_from_period(period)
        # Заголовок - это дата с нужным форматом
        self.format_header = workbook.add_format({'bold': True, 'align': 'center', 'num_format': self.format_date})
        # Значения - это деньги
        self.format_float = self._format_currency
        # Итоговая строка - деньги, жирным
        self.format_itog = workbook.add_format({'bold': True, 'align': 'center', 'num_format': const.MONEY_FORMAT})
        # Итоговая колонка - деньги, жирным
        self.format_itog_col = workbook.add_format({'bold': True, 'align': 'center', 'num_format': const.MONEY_FORMAT})


class _FormatPercent(FormatReport):

    def __init__(self, workbook: xlsxwriter.workbook):
        super(_FormatPercent, self).__init__(workbook)
        self.format_float = self._format_percent

        self.format_name = workbook.add_format({'bold': True,
                                                'align': 'center',
                                                'bg_color': const.COLOR_YELLOW
                                                })


class FormatInflation(_FormatPercent):

    def __init__(self, workbook: xlsxwriter.workbook, cumulative=False):
        super(FormatInflation, self).__init__(workbook)
        # Заголовок - это дата с нужным форматом
        self.format_header = workbook.add_format({'bold': True, 'align': 'center', 'num_format': 'YYYY'})
        # Итоговая строка - Проценты, жирным
        self.format_itog = workbook.add_format({'bold': True, 'align': 'center', 'num_format': const.PERCENTAGE_FORMAT})
        # Итоговая колонка - Проценты, жирным
        self.format_itog_col = workbook.add_format({'bold': True, 'align': 'center', 'num_format': const.PERCENTAGE_FORMAT})
        # Даты - года
        self.format_date = 'YYYY'
        self.cumulative = cumulative
        if cumulative:
            self.report_name = _('Inflation cumulative')
        else:
            self.report_name = _('Inflation annual')
        # self.format_name = workbook.add_format({'bold': True,
        #                                         'align': 'center',
        #                                         'bg_color': const.COLOR_YELLOW
        #                                         })

        self.margins = Margins()
        self.margins.set_for_inflation(cumulative=cumulative)


class FormatReturns(_FormatPercent):

    def __init__(self, workbook: xlsxwriter.workbook, from_date, to_date):
        super(FormatReturns, self).__init__(workbook)
        self.format_index = self._format_bold
        if from_date and to_date:
            self.report_name = _('Return on assets (per annum) {from_date} - {to_date}').\
                format(from_date=from_date, to_date=to_date)
        else:
            self.report_name = _('Return on assets (per annum)')

        self.index_width = 50  # Ширина колонки





class FormatIncome(FormatBalance):

    def __init__(self, workbook: xlsxwriter.workbook, period):
        super(FormatIncome, self).__init__(workbook, period)
        # Название отчета
        self.report_name = _('Income')
        self.format_name = workbook.add_format({'bold': True,
                                                'align': 'center',
                                                'bg_color': const.COLOR_GREEN
                                                })
        # Итоговая строка - деньги, жирным, зеленым
        self.format_itog = workbook.add_format({'bold': True,
                                                'align': 'center',
                                                'bg_color': const.COLOR_GREEN,
                                                'num_format': const.MONEY_FORMAT})
        self.margins = Margins()
        self.margins.set_for_turnover()
        self.account_types = GNUCashData.INCOME

class FormatExpense(FormatBalance):

    def __init__(self, workbook: xlsxwriter.workbook, period):
        super(FormatExpense, self).__init__(workbook, period)
        # Название отчета
        self.report_name = _('Expense')
        self.format_name = workbook.add_format({'bold': True,
                                                'align': 'center',
                                                'bg_color': const.COLOR_YELLOW
                                                })
        # Итоговая строка - деньги, жирным, зеленым
        self.format_itog = workbook.add_format({'bold': True,
                                                'align': 'center',
                                                'bg_color': const.COLOR_YELLOW,
                                                'num_format': const.MONEY_FORMAT})
        self.margins = Margins()
        self.margins.set_for_turnover()
        self.account_types = GNUCashData.EXPENSE

class FormatProfit(FormatBalance):

    def __init__(self, workbook: xlsxwriter.workbook, period):
        super(FormatProfit, self).__init__(workbook, period)
        # Название отчета
        self.report_name = _('Profit')
        self.show_header = False
        self.format_name = workbook.add_format({'bold': True,
                                                'align': 'center',
                                                'bg_color': const.COLOR_GREEN_DARK
                                                })
        # Итоговая строка - деньги, жирным, зеленым
        self.format_itog = workbook.add_format({'bold': True,
                                                'align': 'center',
                                                'bg_color': const.COLOR_GREEN_DARK,
                                                'num_format': const.MONEY_FORMAT})
        self.margins = Margins()
        self.margins.set_for_profit()
        # self.account_types = GNUCashData.EXPENSE


class FormatAssets(FormatBalance):

    def __init__(self, workbook: xlsxwriter.workbook, period):
        super(FormatAssets, self).__init__(workbook, period)
        # Название отчета
        self.report_name = _('Assets')
        self.format_name = workbook.add_format({'bold': True,
                                                'align': 'center',
                                                'bg_color': const.COLOR_BLUE
                                                })
        # Итоговая строка - деньги, жирным, зеленым
        self.format_itog = workbook.add_format({'bold': True,
                                                'align': 'center',
                                                'bg_color': const.COLOR_BLUE,
                                                'num_format': const.MONEY_FORMAT})
        self.margins = Margins()
        self.margins.set_for_balances()
        self.account_types = GNUCashData.ALL_ASSET_TYPES

class FormatLoans(FormatBalance):

    def __init__(self, workbook: xlsxwriter.workbook, period):
        super(FormatLoans, self).__init__(workbook, period)
        # Название отчета
        self.report_name = _('Loans')
        self.show_header = False
        self.format_name = workbook.add_format({'bold': True,
                                                'align': 'center',
                                                'bg_color': const.COLOR_ORANGE_LIGHT
                                                })
        # Итоговая строка - деньги, жирным, зеленым
        self.format_itog = workbook.add_format({'bold': True,
                                                'align': 'center',
                                                'bg_color': const.COLOR_ORANGE_LIGHT,
                                                'num_format': const.MONEY_FORMAT})
        self.margins = Margins()
        self.margins.set_for_balances()
        self.margins.total_row = False
        self.account_types = [GNUCashData.LIABILITY]


class FormatEquity(FormatBalance):

    def __init__(self, workbook: xlsxwriter.workbook, period):
        super(FormatEquity, self).__init__(workbook, period)
        # Название отчета
        self.report_name = _('Equity')
        self.show_header = False
        self.format_name = workbook.add_format({'bold': True,
                                                'align': 'center',
                                                'bg_color': const.COLOR_BLUE
                                                })
        # Итоговая строка - деньги, жирным, зеленым
        self.format_itog = workbook.add_format({'bold': True,
                                                'align': 'center',
                                                'bg_color': const.COLOR_BLUE,
                                                'num_format': const.MONEY_FORMAT})
        self.margins = Margins()
        self.margins.set_for_balances()
        self.margins.total_row = False
        # self.account_types = [GNUCashData.LIABILITY]


