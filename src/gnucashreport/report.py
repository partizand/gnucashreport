import pandas

import abc

from gnucashreport.gnucashbook import GNUCashBook
from gnucashreport.gnucashdata import GNUCashData
from gnucashreport.margins import Margins


class Report(abc.ABC):
    # report types
    INFLATION = 'inflation'
    RETURNS = 'returns'
    INCOME = 'income'
    EXPENSE = 'expense'
    PROFIT = 'profit'
    ASSETS = 'assets'
    LOANS = 'loans'
    EQUITY = 'equity'

    def __init__(self, from_date, to_date, period, glevel):
        # self.rep_type = rep_type
        self.df = None
        # # low level report info
        self.from_date = from_date
        self.to_date = to_date
        self.period = period
        self.account_types = None
        self.glevel = glevel
        # # format
        # self.report_name = rep_type
        # empty margins
        self.margins = Margins()
        # self._format()

    @abc.abstractmethod
    def receive_data(self, raw_report:GNUCashData):
        pass

    def _add_margins(self):
        """
        Add totals into DataFrame
        :param dataframe:
        :param margins:
        :return: DataFrame with totals
        """

        # df = dataframe.copy()
        if self.margins:
            if self.margins.total_row:
                self.df = self._add_row_total(self.df, self.margins)

            if self.margins.total_col or self.margins.mean_col:
                self.df = self._add_col_total(self.df, self.margins)
        # return df

    def _add_col_total(self, dataframe, margins):
        # Список полей для подсчета среднего
        columns = dataframe.columns.tolist()
        df_ret = dataframe.copy()
        # Добавление пустого столбца
        if margins.empty_col:
            df_ret[''] = ''
        if margins.total_col:
            df_ret[margins.total_name] = df_ret[columns].sum(axis=1)
        if margins.mean_col:
            df_ret[margins.mean_name] = df_ret[columns].mean(axis=1)

        return df_ret

    def _add_row_total(self, dataframe, margins=None):
        total_name = _('Total')
        if margins:
            total_name = margins.total_name
        if isinstance(dataframe.index, pandas.core.index.MultiIndex):

            df_ret = dataframe.copy()
            df_sum = pandas.DataFrame(data=dataframe.sum()).T
            # df_sum.reindex()
            # Строковые имена колонок индекса
            strinames = [str(name) for name in dataframe.index.names]

            first = True
            for i in strinames:
                if first:
                    df_sum[i] = total_name
                    first = False
                else:
                    df_sum[i] = ''
            df_sum.set_index(strinames, inplace=True)
            df_ret = df_ret.append(df_sum)
            return df_ret

        else:
            index = total_name
            df_ret = dataframe.copy()
            df_ret.loc[index] = dataframe.sum()
            return df_ret


class ReportInflation(Report):
    def __init__(self, from_date, to_date, period, cumulative, glevel):
        super(ReportInflation, self).__init__(from_date, to_date, period, glevel)
        # self.from_date = from_date
        # self.to_date = to_date
        # self.period = period
        # self.account_types = None
        self.cumulative = cumulative
        self.margins.set_for_inflation(cumulative)
        if cumulative:
            self.report_name = _('Inflation cumulative')
        else:
            self.report_name = _('Inflation annual')

    def receive_data(self, raw_report:GNUCashData):
        self.df = raw_report.inflation_by_period(from_date=self.from_date, to_date=self.to_date, period=self.period,
                                        cumulative=self.cumulative, glevel=self.glevel)
        self._add_margins()


class ReportAssets(Report):
    def __init__(self, from_date, to_date, period, cumulative, glevel):
        super(ReportAssets, self).__init__(from_date, to_date, period, glevel)
        # self.from_date = from_date
        # self.to_date = to_date
        # self.period = period
        # self.account_types = None
        self.report_name = _('Assets')
        self.margins.set_for_balances()
        self.account_types = GNUCashBook.ALL_ASSET_TYPES

    def receive_data(self, raw_report:GNUCashData):
        self.df = raw_report.balance_by_period(from_date=self.from_date,
                                             to_date=self.to_date,
                                             period=self.period,
                                             account_types=self.account_types,
                                             margins=self.margins,
                                             glevel=self.glevel)
        self._add_margins()


