import unittest

from gnucashreport.gcreportcli import build_cli_report, parse_args

from test.testinfo import TestInfo

class CliProg_Test(unittest.TestCase):

    def test_parse_args(self):
        gnucash_file = 'my.gnucash'
        xlsx_file = 'my.xlsx'
        args = [gnucash_file, xlsx_file]
        p_args = parse_args(args)
        self.assertEqual(gnucash_file, p_args.gnucash_file, 'gnucash file arg parsing')
        self.assertEqual(xlsx_file, p_args.xlsx_file, 'xlsx file arg parsing')
        self.assertEqual(1, p_args.glevel, 'glevel arg parsing')

    def test_cli_build_report(self):
        gnucash_file = 'v:/gnucash-base/sqlite/GnuCash-base.gnucash'
        xlsx_file = 'v:/tables/ex-test.xlsx'
        build_cli_report(gnucash_file, xlsx_file, 1)
        # print('end build')