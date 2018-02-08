import unittest

from test.baseopentest import BaseOpenTest

# @unittest.skip('Skip open sql test')
class SQLOpenTest(unittest.TestCase, BaseOpenTest):
    """
    Тестирование чтения данных из sql
    """

    test_name = 'open_sql_test'

    @classmethod
    def setUpClass(cls):
        # cls.open_sql()
        cls.set_locale()
        cls.open_sql()

    # def test(self):
    #     self.assertIsInstance(obj, cls)


if __name__ == '__main__':
    unittest.main()
