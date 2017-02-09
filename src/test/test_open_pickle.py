import unittest

from test.baseopentest import BaseOpenTest


class PickleOpenTest(unittest.TestCase, BaseOpenTest):

    test_name = 'test_open_pickle'

    @classmethod
    def setUpClass(cls):
        cls.open_pickle()


if __name__ == '__main__':
    unittest.main()
