import unittest

import pandas
import numpy

from gnucashreport.xlsxreport import TablePoints
from gnucashreport.margins import Margins
import gnucashreport


class TablePointsTest(unittest.TestCase):
    """
    Тестирование расчета точек excel таблицы
    """

    def test_header_nomargins(self):
        # create simple dataframe 8 rows , 4 cols
        df = pandas.DataFrame(numpy.random.randn(4, 6), index=[0, 1, 2, 3])
        # print(df)
        points = TablePoints(dataframe=df, header=True, margins=None, row=0)
        self.assertEqual(points.row_data_begin, 1)
        self.assertEqual(points.col_head_end, 0)
        self.assertEqual(points.col_data_begin, 1)
        self.assertEqual(points.col_data_end, 6)
        self.assertEqual(points.row_itog, 4)

    def test_noheader_nomargins(self):
        # create simple dataframe 8 rows , 4 cols
        df = pandas.DataFrame(numpy.random.randn(4, 4), index=[0, 1, 2, 3])
        # print(df)
        points = TablePoints(dataframe=df, header=False, margins=None, row=0)
        self.assertEqual(points.row_data_begin, 0)
        self.assertEqual(points.col_head_end, 0)
        self.assertEqual(points.col_data_begin, 1)
        self.assertEqual(points.col_data_end, 4)
        self.assertEqual(points.row_itog, 3)

    def test_header_allmargins(self):
        # create simple dataframe 8 rows , 4 cols
        df = pandas.DataFrame(numpy.random.randn(4, 7), index=[0, 1, 2, 3])
        gnucashreport.GNUCashReport.set_locale()
        margins = Margins()
        margins.empty_col = True
        margins.total_col = True
        margins.mean_col = True
        margins.total_row = True
        points = TablePoints(dataframe=df, header=True, margins=margins, row=0)
        self.assertEqual(points.col_head_end, 0)
        self.assertEqual(points.col_data_begin, 1)
        self.assertEqual(points.col_data_end, 4)
        self.assertEqual(points.row_itog, 4)

        self.assertEqual(points.col_empty, 5)
        self.assertEqual(points.col_totals_begin, 6)
        self.assertEqual(points.col_totals_end, 7)

    def test_header_somemargins(self):
        # create simple dataframe 8 rows , 4 cols
        df = pandas.DataFrame(numpy.random.randn(4, 6), index=[0, 1, 2, 3])
        gnucashreport.GNUCashReport.set_locale()
        margins = Margins()
        # margins.empty_col = True
        margins.total_col = True
        margins.mean_col = True
        margins.total_row = True
        points = TablePoints(dataframe=df, header=True, margins=margins, row=0)
        self.assertEqual(points.col_head_end, 0)
        self.assertEqual(points.col_data_begin, 1)
        self.assertEqual(points.col_data_end, 4)
        self.assertEqual(points.row_itog, 4)

        # self.assertEqual(points.col_empty, 5)
        self.assertEqual(points.col_totals_begin, 5)
        self.assertEqual(points.col_totals_end, 6)