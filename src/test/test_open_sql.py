import unittest

from test.baseopentest import BaseOpenTest


class SQLOpenTest(unittest.TestCase, BaseOpenTest):
    """
    Тестирование чтения данных из sql
    """

    test_name = 'open_sql_test'

    @classmethod
    def setUpClass(cls):
        # cls.open_sql()
        cls.set_locale()
        cls.rep._read_book_sql(cls.bookfile_sql)


if __name__ == '__main__':
    unittest.main()
