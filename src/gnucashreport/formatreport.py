import xlsxwriter.workbook
import xlsxwriter.worksheet
from gnucashreport.margins import Margins

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
        self.margins = None
        self.show_header = True
        self.show_index = True
        self.report_name = None
        self.index_width = 25 # Ширина колонки
        self.column_width = 12
        self.total_width = 15
        self.empty_width = 1


class FormatBalance(FormatReport):

    def __init__(self, workbook: xlsxwriter.workbook, format_date):
        super(FormatBalance, self).__init__(workbook)
        # Заголовок - это дата с нужным форматом
        self.format_header = workbook.add_format({'bold': True, 'align': 'center', 'num_format': format_date})
        # Значения - это деньги
        self.format_float = self._format_currency
        # Итоговая строка - деньги, жирным
        self.format_itog = workbook.add_format({'bold': True, 'align': 'center', 'num_format': const.MONEY_FORMAT})
        # Итоговая колонка - деньги, жирным
        self.format_itog_col = workbook.add_format({'bold': True, 'align': 'center', 'num_format': const.MONEY_FORMAT})

    # def set_cell_width(self, worksheet: xlsxwriter.worksheet, points:TablePoints):
    #     # Ширина первой колонки
    #     worksheet.set_column(firstcol=points.col_begin, lastcol=points.col_head_end, width=25)
    #     # Ширина колонок до итогов
    #     worksheet.set_column(firstcol=points.col_data_begin,
    #                                lastcol=points.col_data_end, width=12)


class FormatIncome(FormatBalance):

    def __init__(self, workbook: xlsxwriter.workbook, format_date):
        super(FormatIncome, self).__init__(workbook, format_date)
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
        self.margins = Margins(total_row=True, total_col=True, mean_col=True, empty_col=True)





