import argparse

import sys

import gnucashreport

__version__ = '0.1.0'


def main(args=None):
    parser = argparse.ArgumentParser(description='Simple cli tool for gnucashreport.'
                                                 ' Builds xlsx reports from GnuCash database ' +
                                                 'Tool ver {}. gnucashreport ver. {}'.format(__version__,
                                                                                             gnucashreport.__version__))

    parser.add_argument('gnucash_file', help="Path to GnuCash database file (xml or sqlite)")
    parser.add_argument('xlsx_file', help="Path to xlsx file for save reports")
    parser.add_argument('--glevel', type=int, action='append', default=1,
                        help="level number for grouping accounts. May be multiple --glevel 0 --glevel 1")
    parser.add_argument('--open_if_lock', action='store_true', default=False,
                        help="open the sqlite file even if it is locked by another user")

    p_args = parser.parse_args(args)

    gcrep = gnucashreport.GNUCashReport()
    print('Opening file {} ...'.format(p_args.gnucash_file))
    gcrep.open_book_file(p_args.gnucash_file, open_if_lock=p_args.open_if_lock)
    print('Buiding reports into {} ...'.format(p_args.xlsx_file))
    gcrep.all_reports_excel(p_args.xlsx_file, glevel=p_args.glevel)


if __name__ == "__main__":
    sys.exit(main())
