import unittest

from test.basereporttest import BaseReportTest


class PickleReportTest(unittest.TestCase, BaseReportTest):

    def __init__(self, *args, **kwargs):
        super(PickleReportTest, self).__init__(*args, **kwargs)
        self.open_pickle()

if __name__ == '__main__':
    unittest.main()
