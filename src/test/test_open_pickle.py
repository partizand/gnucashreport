import unittest

from test.baseopentest import BaseOpenTest


class PickleOpenTest(unittest.TestCase, BaseOpenTest):

    test_name = 'test_open_pickle'

    def __init__(self, *args, **kwargs):
        super(PickleOpenTest, self).__init__(*args, **kwargs)
        self.open_pickle()

if __name__ == '__main__':
    unittest.main()
