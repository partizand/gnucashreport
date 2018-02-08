import unittest
import os
from datetime import date

import pandas
from pandas.util.testing import assert_frame_equal

from gnucashreport.gnucashdata import GNUCashData
from gnucashreport.gnucashbook import GNUCashBook


class BaseTest(object):
    """
    Базовый шаблон для тестирования
    """
    # Данные для генерации тестовых данных и тестирования
    # Test info, change before generate test data!
    bookfile_sql = 'v:/gnucash-base/sqlite/GnuCash-base.gnucash'
    bookfile_xml = 'v:/gnucash-base/xml/GnuCash-base.gnucash'
    dir_testdata = 'v:/test_data'
    GNUCASH_TESTBASE_XML = 'data/xirr-test.gnucash'
    GNUCASH_TESTBASE_SQL = 'data/xirr-test-sql.gnucash'
    # end folder options---------------------------------------
    test_from_date = date(2016, 1, 1)
    test_to_date = date(2016, 12, 31)
    test_from_date_y = date(2009, 1, 1)
    test_to_date_y = date(2016, 12, 31)
    test_period = 'M'
    test_glevel = 1
    test_glevel2 = [0, 1]
    test_level2_suffix = '-2'
    # end test info--------------------------------------------

    # rep = GNUCashData()

    test_name = 'abstract_test'

    # dir_testdata = GNUCashData.dir_testdata

    # pickle_prices = 'prices.pkl'
    # pickle_splits = 'splits.pkl'
    # pickle_accounts = 'accounts.pkl'
    # pickle_tr = 'transactions.pkl'
    # pickle_commodities = 'commodities.pkl'

    pickle_prices = GNUCashData.pickle_prices  # 'prices.pkl'
    pickle_splits = GNUCashData.pickle_splits  # 'splits.pkl'
    pickle_accounts = GNUCashData.pickle_accounts  # 'accounts.pkl'
    pickle_tr = GNUCashData.pickle_tr  # 'transactions.pkl'
    pickle_commodities = GNUCashData.pickle_commodities  # 'commodities.pkl'

    pickle_assets = 'assets.pkl'
    pickle_loans = 'loans.pkl'
    pickle_expense = 'expense.pkl'
    pickle_income = 'income.pkl'
    pickle_profit = 'profit.pkl'
    pickle_equity = 'equity.pkl'
    pickle_inflation = 'inflation.pkl'

    # Конец тестовых данных

    @classmethod
    def set_locale(cls):
        GNUCashData.set_locale()


    # @classmethod
    # def open_sql(cls):
    #     cls.rep.open_book_file(BaseTest.bookfile_sql)

    # @classmethod
    # def open_xml(cls):
    #     cls.rep.open_book_file(BaseTest.bookfile_xml)

    @classmethod
    def open_pickle(cls):
        cls.rep._open_book_pickle(folder=BaseTest.dir_testdata)

    @classmethod
    def _save_db_to_pickle(cls, folder, suffix=None):
        """
        For test purpose
        Save book to pickle files
        Запись данных базы в pickle файлы каталога.
        :param folder: Каталог с файлами базы
        :return:
        """
        cls._dataframe_to_pickle(cls.rep.df_accounts, cls._add_suffix(cls.pickle_accounts, suffix), folder=folder)
        cls._dataframe_to_pickle(cls.rep.df_commodities, cls._add_suffix(cls.pickle_commodities, suffix), folder=folder)
        cls._dataframe_to_pickle(cls.rep.df_prices, cls._add_suffix(cls.pickle_prices, suffix), folder=folder)
        cls._dataframe_to_pickle(cls.rep.df_transactions, cls._add_suffix(cls.pickle_tr, suffix), folder=folder)
        cls._dataframe_to_pickle(cls.rep.df_splits, cls._add_suffix(cls.pickle_splits, suffix), folder=folder)

    @classmethod
    def _dataframe_to_pickle(cls, dataframe, filename, folder):
        """
        Записаывает DataFrame в pickle файл
        :param dataframe:
        :param filename:
        :return:
        """
        fullfilename = os.path.join(folder, filename)
        dataframe.to_pickle(fullfilename)


    @staticmethod
    def _add_suffix(filename, suffix):
        """
        Adds suffix to filename
        :param filename:
        :param suffix:
        :return:
        """
        if not suffix:
            return filename
        return "{0}{2}.{1}".format(*filename.rsplit('.', 1) + [suffix])


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


