import unittest

from test.basereporttest import BaseReportTest


class SQLReportTest(unittest.TestCase, BaseReportTest):

    test_name = 'report_sql_test'

    @classmethod
    def setUpClass(cls):
        cls.set_locale()
        cls.open_sql()

if __name__ == '__main__':
    unittest.main()
