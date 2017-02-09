import unittest

from test.basereporttest import BaseReportTest


class PickleReportTest(unittest.TestCase, BaseReportTest):

    @classmethod
    def setUpClass(cls):
        cls.open_pickle()

if __name__ == '__main__':
    unittest.main()
