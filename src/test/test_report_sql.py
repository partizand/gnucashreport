import unittest

from test.basereporttest import BaseReportTest

from gnucashreport.gnucashdata import GNUCashData


class SQLReportTest(unittest.TestCase, BaseReportTest):

    test_name = 'report_sql_test'

    # rep = GNUCashData().open_book_file(BaseReportTest.bookfile_sql)

    @classmethod
    def setUpClass(cls):
        cls.set_locale()
        # cls.open_sql()
        cls.rep.open_book_file(BaseTest.bookfile_sql)

if __name__ == '__main__':
    unittest.main()
