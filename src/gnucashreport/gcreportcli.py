"""
Simple cli tool for gnucashreport
"""
import argparse

import sys

import gnucashreport

__version__ = '0.2.0'


def main(args=None):
    parser = argparse.ArgumentParser(description='Simple cli tool for gnucashreport.'
                                                 ' Builds xlsx reports from GnuCash database ' +
                                                 'Tool ver {}. gnucashreport ver. {}'.format(__version__,
                                                                                             gnucashreport.__version__))

    parser.add_argument('gnucash_file', help="Path to GnuCash database file (xml or sqlite)")
    parser.add_argument('xlsx_file', help="Path to xlsx file for save reports")
    parser.add_argument('--glevel', type=int, action='append', default=1,
                        help="level number for grouping accounts. May be multiple --glevel 0 --glevel 1")
    # parser.add_argument('--open_if_lock', action='store_true', default=False,
    #                     help="open the sqlite file even if it is locked by another user")

    p_args = parser.parse_args(args)

    print('Opening file {} ...'.format(p_args.gnucash_file))
    raw_data = RawData(p_args.gnucash_file)
    builder = BuildReport(raw_data)
    print('Building reports into {} ...'.format(p_args.xlsx_file))
    reportset = builder.get_reportset_all(glevel=p_args.glevel)
    outputer_excel = XLSXReport(p_args.xlsx_file)
    outputer_excel.add_reportset(reportset)
    outputer_excel.close()


if __name__ == "__main__":
    sys.exit(main())
