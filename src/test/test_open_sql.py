import unittest

from test.baseopentest import BaseOpenTest


class SQLOpenTest(unittest.TestCase, BaseOpenTest):
    """
    Тестирование чтения данных из sql
    """

    bookfile = "u:/sqllite_book/real-2017-01-26.gnucash"

    test_name = 'open_sql_test'

    def __init__(self, *args, **kwargs):
        super(SQLOpenTest, self).__init__(*args, **kwargs)
        self.rep.open_book_sql(self.bookfile, open_if_lock=True)

if __name__ == '__main__':
    unittest.main()
