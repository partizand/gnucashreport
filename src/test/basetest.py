import unittest
import os

import pandas
from pandas.util.testing import assert_frame_equal

from gcreports.gnucashdata import GNUCashData


class BaseTest(object):
    """
    Базовый шаблон для тестирования
    """
    rep = GNUCashData()

    # bookfile_sql = "u:/sqllite_book/real-2017-01-26.gnucash"
    # bookfile_xml = 'U:/xml_book/GnuCash-base.gnucash'

    test_name = 'abstract_test'

    dir_testdata = GNUCashData.dir_testdata

    @classmethod
    def open_sql(cls):
        cls.rep.open_book_sql(GNUCashData.bookfile_sql, open_if_lock=True)

    @classmethod
    def open_xml(cls):
        cls.rep.open_book_xml(GNUCashData.bookfile_xml)

    @classmethod
    def open_pickle(cls):
        cls.rep.open_pickle()

    def pickle_control(self, pickle_file, df_to_test, test_name=None):
        """
        Сверка dataframe c эталонным Pickle файлом
        :param pickle_file:
        :param df_to_test:
        :param test_name:
        :return:
        """
        filename = os.path.join(self.dir_testdata, pickle_file)
        df_etalon = pandas.read_pickle(filename)
        assert_frame_equal(df_to_test, df_etalon, check_like=True, obj=test_name)
        self.assertEqual(len(df_to_test), len(df_etalon), 'length of dataframe')

    def dataframe_fields_control(self, df, etalon_fields, df_name):
        """
        Проверка что dataframe содержит колонки с заданными именами
        :param df:
        :param etalon_fields:
        :param df_name:
        :return:
        """
        cols = df.columns.values.tolist()
        for field in etalon_fields:
            self.assertIn(field, cols, 'DataFrame {} contain field {}. {}'.format(df_name, field, self.test_name))
