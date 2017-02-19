
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

    def set_for_profit(self):
        self.total_row = False
        self.total_col = True
        self.mean_col = True

    def set_for_balances(self):
        self.total_row = True
        self.total_col = False
        self.mean_col = False

    def get_counts_vtotals(self):
        """
        Возвращает количество итоговых колонок
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




            # def add_margins(self, dataframe):
    #     """
    #     Добавляет итоги в DataFrame
    #     :param dataframe:
    #     :param total_row: Добавить строку итогов
    #     :param total_col: Добавить колонку итогов
    #     :param mean_col: Добавить колонку среднее
    #     :param total_name: Имя итогов
    #     :param mean_name: Имя среднего
    #     :param empty_col: Добавить пустую колонку перед итогами
    #     :return: DataFrame с итогами
    #     """
    #     df = dataframe.copy()
    #     if self.total_row:
    #         df = self._add_row_total(df)
    #
    #     if self.total_col or self.mean_col:
    #         df = self._add_col_total(df)
    #     return df
    #
    # def _add_row_total(self, dataframe):
    #
    #     if isinstance(dataframe.index, pandas.core.index.MultiIndex):
    #
    #         df_ret = dataframe.copy()
    #         df_sum = pandas.DataFrame(data=dataframe.sum()).T
    #         # Строковые имена колонок индекса
    #         strinames = [str(name) for name in dataframe.index.names]
    #
    #         first = True
    #         for i in strinames:
    #             if first:
    #                 df_sum[i] = self.total_name
    #                 first = False
    #             else:
    #                 df_sum[i] = ''
    #         df_sum.set_index(strinames, inplace=True)
    #         df_ret = df_ret.append(df_sum)
    #         return df_ret
    #
    #     else:
    #         index = self.total_name
    #         df_ret = dataframe.copy()
    #         df_ret.loc[index] = dataframe.sum()
    #         return df_ret
    #
    # def _add_col_total(self, dataframe):
    #     # Список полей для подсчета среднего
    #     cols = dataframe.columns.tolist()
    #     df_ret = dataframe.copy()
    #     # Добавление пустого столбца
    #     if self.empty_col:
    #         df_ret[''] = ''
    #     if self.total_col:
    #         df_ret[self.total_name] = df_ret[cols].sum(axis=1)
    #     if self.mean_col:
    #         df_ret[self.mean_name] = df_ret[cols].mean(axis=1)
    #
    #     return df_ret

