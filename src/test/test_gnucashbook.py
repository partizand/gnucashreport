import unittest

from gnucashreport.gnucashbook import GNUCashBook
import gnucashreport.cols as cols

import decimal

import piecash

from pandas.api.types import is_datetime64_any_dtype

# @unittest.skip('Skip open test')
from test.testinfo import TestInfo

MARKER_XIRR_TRUE = '%xirr_true%'
MARKER_XIRR_FALSE = '%xirr_false%'

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
        pie_sql = piecash.open_book(TestInfo.GNUCASH_TESTBASE_SQL, open_if_lock=True)
        pie_xml = piecash.open_book(TestInfo.GNUCASH_TESTBASE_SQL, open_if_lock=True)
        book_sql = GNUCashBook(TestInfo.GNUCASH_TESTBASE_SQL)
        book_xml = GNUCashBook(TestInfo.GNUCASH_TESTBASE_XML)


        cls.test_array = [[book_xml, pie_xml], [book_sql, pie_sql]]

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
        for book, piebook in self.test_array:
            with self.subTest(book):
                self.dataframe_fields_control(book.df_accounts, self.account_fields, 'df_account sql ')
                self.dataframe_fields_control(book.df_commodities, self.comm_fields, 'df_commodities sql ')
                self.dataframe_fields_control(book.df_transactions, self.tr_fields, 'df_transactions sql ')
                self.dataframe_fields_control(book.df_prices, self.price_fields, 'df_prices sql ')
                self.dataframe_fields_control(book.df_splits, self.split_fields, 'df_splits sql ')

    def test_splits_value_decimal(self):
        for book, piebook in self.test_array:
            with self.subTest(book):
                value = book.df_splits[cols.VALUE][0]
                self.assertIsInstance(value, decimal.Decimal, 'Splits value is decimal type')

    def test_splits_quantity_decimal(self):
        for book, piebook in self.test_array:
            with self.subTest(book):
                value = book.df_splits[cols.QUANTITY][0]
                self.assertIsInstance(value, decimal.Decimal, 'Splits quantity is decimal type')

    def test_prices_value_decimal(self):
        for book, piebook in self.test_array:
            with self.subTest(book):
                value = book.df_prices[cols.VALUE][0]
                self.assertIsInstance(value, decimal.Decimal, 'Prices value is decimal type')

    def test_accounts_notempty(self):
        for book, piebook in self.test_array:
            with self.subTest(book):
                self.df_notempty(book.df_accounts, 'df_accounts')

    def test_splits_notempty(self):
        for book, piebook in self.test_array:
            with self.subTest(book):
                self.df_notempty(book.df_splits, 'df_splits')

    def test_accounts_index(self):
        for book, piebook in self.test_array:
            with self.subTest(book):
                self.assertEqual(book.df_accounts.index.name, cols.GUID,'df_accounts index is not GUID')

    def test_splits_index(self):
        for book, piebook in self.test_array:
            with self.subTest(book):
                self.assertEqual(book.df_splits.index.name, cols.GUID,'df_splits index is not GUID')

    def test_transactions_index(self):
        for book, piebook in self.test_array:
            with self.subTest(book):
                self.assertEqual(book.df_transactions.index.name, cols.GUID,'df_transactions index is not GUID')

    # def test_prices_index(self):
    #     for book, piebook in self.test_array:
    #         with self.subTest(book):
    #             self.assertEqual(book.df_prices.index.name, cols.GUID, 'df_prices index is not GUID')

    def test_commodities_index(self):
        for book, piebook in self.test_array:
            with self.subTest(book):
                self.assertEqual(book.df_commodities.index.name, cols.GUID, 'df_commodities index is not GUID')

    def df_notempty(self, df, name_df):
        for book, piebook in self.test_array:
            with self.subTest(book):
                self.assertIsNotNone(df, '{} is not none'.format(name_df))
                l = len(df)
                self.assertGreater(l, 0, '{} contain lines'.format(name_df))

    def test_rootaccount(self):
        for book, piebook in self.test_array:
            with self.subTest(book):
                self.assertIsNotNone(book.root_account_guid, 'root_account_guid is not none')
                self.assertNotEqual(book.root_account_guid, '', 'root_account_guid is not empty')
                self.assertEqual(book.root_account_guid, piebook.root_account.guid, 'Pie compare root account')

    def test_account_fullname(self):
        for book, piebook in self.test_array:
            with self.subTest(book):
                df_error = book.df_accounts[book.df_accounts[cols.FULLNAME].str.contains("error")]
                self.assertEqual(len(df_error), 0, 'Fullnames of account contains error string')

    def test_splits_count(self):
        for book, piebook in self.test_array:
            with self.subTest(book):
                pie_splits = piebook.splits
                self.assertEqual(len(book.df_splits), len(pie_splits), 'Number splits compare with piecash')

    def test_transactions_count(self):
        for book, piebook in self.test_array:
            with self.subTest(book):
                pie_transactions = piebook.transactions
                self.assertEqual(len(book.df_transactions), len(pie_transactions), 'Number transactions compare with piecash')

    def test_accounts_count(self):
        for book, piebook in self.test_array:
            with self.subTest(book):
                pie_accounts = piebook.accounts
                self.assertGreaterEqual(len(book.df_accounts), len(pie_accounts), 'Number accounts compare with piecash')

    def test_transaction_dates(self):
        for book, piebook in self.test_array:
            with self.subTest(book):
                self.assertTrue(is_datetime64_any_dtype(book.df_transactions[cols.POST_DATE].dtype), 'Post_date in transaction is date type')


    def test_account_values(self):
        for book, piebook in self.test_array:
            # iterate all accounts
            for index, account in book.df_accounts.iterrows():
                with self.subTest('{}-{}'.format(book, account[cols.FULLNAME])):

                    if account[cols.ACCOUNT_TYPE] != book.ROOT:
                        # check fullname
                        pie_account = piebook.accounts(fullname=account[cols.FULLNAME])
                        self.assertNotEqual(pie_account, None, 'fullname compare with piecash')
                        # check xirr enable value
                        notes = account[cols.NOTES]
                        if notes:
                            if MARKER_XIRR_FALSE in notes:
                                self.assertEqual(account[cols.XIRR_ENABLE], False, 'xirr enable wrong value')
                            if MARKER_XIRR_TRUE in notes:
                                self.assertEqual(account[cols.XIRR_ENABLE], True, 'xirr enable wrong value')

    #----------------------------------------------------------------------------------------------------
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


