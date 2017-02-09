import unittest
import os

import pandas
from pandas.util.testing import assert_frame_equal

from gcreports.gcreport import GCReport


class BaseTest(object):
    """
    Шаблон для тестирования чтения данных из базы
    """
    rep = GCReport()

    bookfile_sql = "u:/sqllite_book/real-2017-01-26.gnucash"
    bookfile_xml = 'U:/xml_book/GnuCash-base.gnucash'

    test_name = 'abstract_test'

    dir_pickle = 'U:/test_data'


    def open_sql(self):
        self.rep.open_book_sql(self.bookfile_sql, open_if_lock=True)

    def open_xml(self):
        self.rep.open_book_xml(self.bookfile_xml)

    def open_pickle(self):
        self.rep.open_pickle()

    def pickle_control(self, pickle_file, df_to_test, test_name=None):
        """
        Сверка dataframe c эталонным Pickle файлом
        :param pickle_file:
        :param df_to_test:
        :param test_name:
        :return:
        """
        filename = os.path.join(self.dir_pickle, pickle_file)
        df_etalon = pandas.read_pickle(filename)
        assert_frame_equal(df_to_test, df_etalon, check_like=True, obj=test_name)

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



