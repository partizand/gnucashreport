import unittest

from test.baseopentest import BaseOpenTest


class SQLOpenTest(unittest.TestCase, BaseOpenTest):
    """
    Тестирование чтения данных из xml
    """

    pickle_prices = 'prices-xml.pkl'
    pickle_splits = 'splits-xml.pkl'
    pickle_accounts = 'accounts-xml.pkl'
    pickle_tr = 'transactions-xml.pkl'
    pickle_commodities = 'commodities-xml.pkl'

    # bookfile = "u:/sqllite_book/real-2017-01-26.gnucash"

    test_name = 'open_xml_test'

    @classmethod
    def setUpClass(cls):
        cls.open_xml()

    # def __init__(self, *args, **kwargs):
    #     super(SQLOpenTest, self).__init__(*args, **kwargs)
    #     self.open_xml()

if __name__ == '__main__':
    unittest.main()
