import unittest

import os

from gnucashreport.gnucashbook import GNUCashBook
from gnucashreport.rawdata import RawData
import gnucashreport.cols as cols
from test.basetest import BaseTest

import decimal


# @unittest.skip('Skip open test')
from test.testinfo import TestInfo


class GnuCashBook_Test(unittest.TestCase):
    """
    Шаблон для тестирования чтения данных из базы
    """

    # Список полей загруженных dataframe для проверки
    account_fields = [cols.SHORTNAME, cols.FULLNAME, cols.ACCOUNT_TYPE,
                      cols.COMMODITY_GUID, "commodity_scu",
                      "parent_guid", "description", "hidden", cols.NOTES]
    comm_fields = ["namespace", "mnemonic"]
    tr_fields = [cols.CURRENCY_GUID, cols.POST_DATE, cols.DESCRIPTION]
    split_fields = ["transaction_guid", "account_guid",
                    "memo", "reconcile_state", "value", "quantity"]
    price_fields = ["currency_guid", "source", "type", "value"]

    # test_name = 'abstract_open_test'

    # book = GNUCashBook()

    @classmethod
    def setUpClass(cls):
        # gcrep_xml = GNUCashBook()
        # gcrep_sql = GNUCashBook()
        # base_path = os.path.dirname(os.path.realpath(__file__))
        # xml_book = os.path.join(base_path, TestInfo.GNUCASH_TESTBASE_XML)
        # sql_book = os.path.join(base_path, TestInfo.GNUCASH_TESTBASE_SQL)
        # gcrep_xml.open_file(xml_book)
        # gcrep_sql.open_file(sql_book)

        # cls.test_array = [('xml', gcrep_xml), ('sql', gcrep_sql)]
        cls.test_array = [GNUCashBook(TestInfo.GNUCASH_TESTBASE_XML), GNUCashBook(TestInfo.GNUCASH_TESTBASE_SQL)]

    # @classmethod
    # def open_book(cls, filename):
    #     base_path = os.path.dirname(os.path.realpath(__file__))
    #     base_path = os.path.join(base_path, filename)
    #     cls.book.open_file(base_path)

    def test_fields(self):
        """
        Проверка имен столбцов прочитанных данных
        :return:
        """
        for book in self.test_array:
            with self.subTest(book):
                self.dataframe_fields_control(book.df_accounts, self.account_fields, 'df_account sql ')
                self.dataframe_fields_control(book.df_commodities, self.comm_fields, 'df_commodities sql ')
                self.dataframe_fields_control(book.df_transactions, self.tr_fields, 'df_transactions sql ')
                self.dataframe_fields_control(book.df_prices, self.price_fields, 'df_prices sql ')
                self.dataframe_fields_control(book.df_splits, self.split_fields, 'df_splits sql ')

    def test_splits_value_decimal(self):
        for book in self.test_array:
            with self.subTest(book):
                value = book.df_splits[cols.VALUE][0]
                self.assertIsInstance(value, decimal.Decimal, 'Splits value is decimal type')

    def test_splits_quantity_decimal(self):
        for book in self.test_array:
            with self.subTest(book):
                value = book.df_splits[cols.QUANTITY][0]
                self.assertIsInstance(value, decimal.Decimal, 'Splits quantity is decimal type')

    def test_prices_value_decimal(self):
        for book in self.test_array:
            with self.subTest(book):
                value = book.df_prices[cols.VALUE][0]
                self.assertIsInstance(value, decimal.Decimal, 'Prices value is decimal type')

    def test_accounts_notempty(self):
        for book in self.test_array:
            with self.subTest(book):
                self.df_notempty(book.df_accounts, 'df_accounts')

    def test_splits_notempty(self):
        for book in self.test_array:
            with self.subTest(book):
                self.df_notempty(book.df_splits, 'df_splits')

    def test_accounts_index(self):
        for book in self.test_array:
            with self.subTest(book):
                self.assertEqual(book.df_accounts.index.name, cols.GUID,'df_accounts index is not GUID')

    def test_splits_index(self):
        for book in self.test_array:
            with self.subTest(book):
                self.assertEqual(book.df_splits.index.name, cols.GUID,'df_splits index is not GUID')

    def test_transactions_index(self):
        for book in self.test_array:
            with self.subTest(book):
                self.assertEqual(book.df_transactions.index.name, cols.GUID,'df_transactions index is not GUID')

    def test_prices_index(self):
        for book in self.test_array:
            with self.subTest(book):
                self.assertEqual(book.df_prices.index.name, cols.GUID, 'df_prices index is not GUID')

    def test_commodities_index(self):
        for book in self.test_array:
            with self.subTest(book):
                self.assertEqual(book.df_commodities.index.name, cols.GUID, 'df_commodities index is not GUID')

    def df_notempty(self, df, name_df):
        for book in self.test_array:
            with self.subTest(book):
                self.assertIsNotNone(df, '{} is not none'.format(name_df))
                l = len(df)
                self.assertGreater(l, 0, '{} contain lines'.format(name_df))

    def test_rootaccount_filled(self):
        for book in self.test_array:
            with self.subTest(book):
                self.assertIsNotNone(book.root_account_guid, 'root_account_guid is not none')
                self.assertNotEqual(book.root_account_guid, '', 'root_account_guid is not empty')

    def test_account_fullname(self):
        for book in self.test_array:
            with self.subTest(book):
                df_error = book.df_accounts[book.df_accounts[cols.FULLNAME].str.contains("error")]
                self.assertEqual(len(df_error), 0, 'Fullnames of account contains error string')

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
            self.assertIn(field, cols, 'DataFrame {} contain field {}.'.format(df_name, field))


