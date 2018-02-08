import unittest

import os

from test.baseopentest import BaseOpenTest

# @unittest.skip('Skip open sql test')
from test.testinfo import TestInfo


class SQLOpenTest(unittest.TestCase, BaseOpenTest):
    """
    Тестирование чтения данных из sql
    """

    test_name = 'open_sql_test'

    @classmethod
    def setUpClass(cls):
        # cls.open_sql()
        cls.set_locale()
        cls.open_book(TestInfo.GNUCASH_TESTBASE_SQL)

    # def test(self):
    #     self.assertNotEqual () assertGreater() IsInstance(obj, cls)


if __name__ == '__main__':
    unittest.main()
