import unittest

from test.basereporttest import BaseReportTest


class SQLReportTest(unittest.TestCase, BaseReportTest):

    def __init__(self, *args, **kwargs):
        super(SQLReportTest, self).__init__(*args, **kwargs)
        self.open_sql()

if __name__ == '__main__':
    unittest.main()