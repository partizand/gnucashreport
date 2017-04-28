from xlsxwriter.utility import xl_col_to_name

class TablePoints:
    def __init__(self, dataframe, header, margins, row):
        """
        Calculate positions for table in excel file
        All positions are 0-started

+--------------------------------------------------------------------------------------------------------------------+
| Account header                |  Data                                | totals                                      |
|--------------------------------------------------------------------------------------------------------------------+
| col_begin |   | col_head_end  | col_data_begin | | |  | col_data_end | col_empty | col_total_begin | col_total_end |
| row_begin |   |               |                | | |  |              |           |                 |               |
+-----------+---+---------------+----------------+-+-+--+--------------+-----------+-----------------+---------------+
|row_data_begin |               |                | | |  |              |           |                 |               |
+-----------+---+---------------+----------------+-+-+--+--------------+-----------+-----------------+---------------+
|           |   |               |                | | |  |              |           |                 |               |
+-----------+---+---------------+----------------+-+-+--+--------------+-----------+-----------------+---------------+
|           |   |               |                | | |  |              |           |                 |               |
+-----------+---+---------------+----------------+-+-+--+--------------+-----------+-----------------+---------------+
| row_itog  |   |               |                | | |  |              |           |                 | col_all_end   |
+-----------+---+---------------+----------------+-+-+--+--------------+-----------+-----------------+---------------+


        :param dataframe:
        :param header:
        :param margins:
        :param row:
        """

        # Кол-во колонок названий
        len_index = len(dataframe.index.names)
        # Высота данных без заголовка
        height = len(dataframe)
        # Кол-во колонок с данными (без колонок названий)
        col_count = len(dataframe.columns)

        self.col_empty = None
        self.col_totals_begin = None
        self.col_totals_end = None

        self.col_begin = 0
        self.row_begin = row
        self.row_data_begin = row
        if header:
            self.row_data_begin += 1

        # Номер колонки с окончанием заголовка для счетов
        self.col_head_end = self.col_begin + len_index - 1

        self.col_data_begin = self.col_head_end + 1
        self.col_data_end = self.col_data_begin + col_count - 1
        self.col_all_end = self.col_data_begin + col_count - 1

        # Строка с итоговыми значениями
        self.row_itog = self.row_data_begin + height - 1

        # self.count_vtotals = 0
        # self.count_vtotals_without_empty = 0
        if margins:
            count_vtotals = margins.get_counts_vtotals()
            if count_vtotals:
                self.col_data_end -= count_vtotals
                self.col_totals_begin = self.col_data_end + 1
                self.col_totals_end = self.col_data_end + count_vtotals
                if margins.empty_col:
                    self.col_empty = self.col_data_end + 1
                    self.col_totals_begin = self.col_data_end + 2
                    self.col_empty_l = xl_col_to_name(self.col_empty)
                self.col_totals_begin_l = xl_col_to_name(self.col_totals_begin)
                self.col_totals_end_l = xl_col_to_name(self.col_totals_end)

        # Буквы для колонок
        self.col_begin_l = xl_col_to_name(self.col_begin)
        self.col_data_begin_l = xl_col_to_name(self.col_data_begin)
        self.col_data_end_l = xl_col_to_name(self.col_data_end)
        self.col_head_end_l = xl_col_to_name(self.col_head_end)

