import unittest

from test.baseopentest import BaseOpenTest


# @unittest.skip('Skip open xml test')
from test.testinfo import TestInfo


class SQLOpenTest(unittest.TestCase, BaseOpenTest):
    """
    Тестирование чтения данных из xml
    """

    # pickle_prices = 'prices-xml.pkl'
    # pickle_splits = 'splits-xml.pkl'
    # pickle_accounts = 'accounts-xml.pkl'
    # pickle_tr = 'transactions-xml.pkl'
    # pickle_commodities = 'commodities-xml.pkl'

    test_name = 'open_xml_test'

    @classmethod
    def setUpClass(cls):
        cls.set_locale()
        cls.open_book(TestInfo.GNUCASH_TESTBASE_XML)

if __name__ == '__main__':
    unittest.main()
