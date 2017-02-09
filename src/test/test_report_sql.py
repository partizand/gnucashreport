import unittest

from test.basereporttest import BaseReportTest


class SQLReportTest(unittest.TestCase, BaseReportTest):

    test_name = 'report_sql_test'

    @classmethod
    def setUpClass(cls):
        cls.open_sql()

    # def __init__(self, *args, **kwargs):
    #     super(SQLReportTest, self).__init__(*args, **kwargs)
    #     self.open_sql()

if __name__ == '__main__':
    unittest.main()