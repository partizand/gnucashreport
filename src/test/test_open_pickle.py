import unittest

from test.baseopentest import BaseOpenTest


class PickleOpenTest(unittest.TestCase, BaseOpenTest):
    """
    Тестирование чтения данных из pickle
    """

    # bookfile = "u:/sqllite_book/real-2017-01-26.gnucash"

    test_name = 'open_pickle_test'

    def __init__(self, *args, **kwargs):
        super(PickleOpenTest, self).__init__(*args, **kwargs)
        self.rep.open_pickle()

if __name__ == '__main__':
    unittest.main()
