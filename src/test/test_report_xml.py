import unittest

from test.basereporttest import BaseReportTest


class XMLReportTest(unittest.TestCase, BaseReportTest):

    def __init__(self, *args, **kwargs):
        super(XMLReportTest, self).__init__(*args, **kwargs)
        self.open_xml()

if __name__ == '__main__':
    unittest.main()
