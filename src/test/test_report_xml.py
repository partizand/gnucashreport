import unittest

from test.basereporttest import BaseReportTest


class XMLReportTest(unittest.TestCase, BaseReportTest):

    test_name = 'report_xml_test'

    @classmethod
    def setUpClass(cls):
        cls.set_locale()
        cls.open_xml()

if __name__ == '__main__':
    unittest.main()
