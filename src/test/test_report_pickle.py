import unittest

from test.basereporttest import BaseReportTest


class PickleReportTest(unittest.TestCase, BaseReportTest):

    @classmethod
    def setUpClass(cls):
        # cls.open_pickle()
        cls.rep._open_book_pickle(folder=cls.dir_testdata)

if __name__ == '__main__':
    unittest.main()
