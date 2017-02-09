import unittest

from test.baseopentest import BaseOpenTest
from test.basepickle import BasePickle


class PickleOpenTest(BasePickle, BaseOpenTest, unittest.TestCase):

    test_name = 'test_open_pickle'

if __name__ == '__main__':
    unittest.main()
