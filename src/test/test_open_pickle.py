import unittest

from test.baseopentest import BaseOpenTest


class PickleOpenTest(unittest.TestCase, BaseOpenTest):

    test_name = 'test_open_pickle'

    @classmethod
    def setUpClass(cls):
        cls.rep._read_book_pickle(folder=cls.dir_testdata)


if __name__ == '__main__':
    unittest.main()
