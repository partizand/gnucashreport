import unittest

from test.baseopentest import BaseOpenTest


class SQLOpenTest(unittest.TestCase, BaseOpenTest):
    """
    Тестирование чтения данных из sql
    """

    # bookfile = "u:/sqllite_book/real-2017-01-26.gnucash"

    test_name = 'open_sql_test'

    @classmethod
    def setUpClass(cls):
        cls.open_sql()

    # def __init__(self, *args, **kwargs):
    #     super(SQLOpenTest, self).__init__(*args, **kwargs)
    #     self.open_sql()
        # self.rep.open_book_sql(self.bookfile_sql, open_if_lock=True)

if __name__ == '__main__':
    unittest.main()
