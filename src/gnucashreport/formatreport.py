import xlsxwriter.workbook
import xlsxwriter.worksheet

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

        # Описание текущего формата
        self.format_name = self._format_bold_center
        self.format_header = self._format_bold_center
        self.format_index = self._format_bold_center
        self.format_itog = self._format_bold
        self.format_itog_col = self._format_bold
        self.format_float = None
        self.margins = Margins()
        self.show_header = True
        self.show_index = True
        self.report_name = None
        self.index_width = 25 # Ширина колонки
        self.column_width = 12
        self.total_width = 15
        self.empty_width = 1


class FormatBalance(FormatReport):

    def __init__(self, workbook: xlsxwriter.workbook, from_date, to_date, period):
        super(FormatBalance, self).__init__(workbook)
        self.period = period
        self.from_date = from_date
        self.to_date = to_date
        self._format_date = self._dateformat_from_period(period)
        # Заголовок - это дата с нужным форматом
        self.format_header = workbook.add_format({'bold': True, 'align': 'center', 'num_format': self._format_date})
        # Значения - это деньги
        self.format_float = self._format_currency
        # Итоговая строка - деньги, жирным
        self.format_itog = workbook.add_format({'bold': True, 'align': 'center', 'num_format': const.MONEY_FORMAT})
        # Итоговая колонка - деньги, жирным
        self.format_itog_col = workbook.add_format({'bold': True, 'align': 'center', 'num_format': const.MONEY_FORMAT})

    def _dateformat_from_period(self, period: str):
        """
        Get Excel date format from period letter (D, M, Y ...)
        :param period: May be date format, e.g. dd-mm-yyyy,
                        or may be period letter: D, M, Q, Y (day, month, quarter, year)
                        or may be None, then dd-mm-yyyy returns
        :return: datetime_format for excel
        """

        if period:
            dateformat = period
        else:
            dateformat = 'dd-mm-yyyy'

        if period:
            if period.upper() == 'D':
                dateformat = const.DAYDATE_FORMAT # 'dd-mm-yyyy'
            if period.upper() == 'M':
                dateformat = const.MONTHDATE_FORMAT # 'mmm yyyy'
            if period.upper() == 'A':
                dateformat = 'yyyy'
            if period.upper() == 'Q':
                dateformat = const.MONTHDATE_FORMAT # 'Q YY'  # ???
        return dateformat


class FormatIncome(FormatBalance):

    def __init__(self, workbook: xlsxwriter.workbook, from_date, to_date, period):
        super(FormatIncome, self).__init__(workbook, from_date, to_date, period)
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

class FormatAssets(FormatBalance):

    def __init__(self, workbook: xlsxwriter.workbook, from_date, to_date, period):
        super(FormatAssets, self).__init__(workbook, from_date, to_date, period)
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





