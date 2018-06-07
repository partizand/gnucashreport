"""
Simple cli tool for gnucashreport
"""
import argparse

import sys

import gnucashreport

from gnucashreport.buildreport import BuildReport
from gnucashreport.rawdata import RawData
from gnucashreport.xlsxreport import XLSXReport

__version__ = '0.2.1'

def parse_args(args):
    """
    Parsing arguments
    :param args: Array
    :return: arguments: p_args.gnucash_file, p_args.xlsx_file, p_args.glevel
    """
    parser = argparse.ArgumentParser(description='Simple cli tool for gnucashreport.'
                                                 ' Builds xlsx reports from GnuCash database ' +
                                                 'Tool ver {}. gnucashreport ver. {}'.format(__version__,
                                                                                             gnucashreport.__version__))

    parser.add_argument('gnucash_file', help="Path to GnuCash database file (xml or sqlite)")
    parser.add_argument('xlsx_file', help="Path to xlsx file for save reports")
    parser.add_argument('--glevel', type=int, action='append', default=1,
                        help="level number for grouping accounts. May be multiple --glevel 0 --glevel 1")

    p_args = parser.parse_args(args)
    return p_args


def build_cli_report(gnucash_file, xlsx_file, glevel):
    # Build report from cli programm
    print('Opening file {} ...'.format(gnucash_file))
    raw_data = RawData(gnucash_file)
    builder = BuildReport(raw_data)
    print('Building reports into {} ...'.format(xlsx_file))
    reportset = builder.get_reportset_all(glevel=glevel)
    outputer_excel = XLSXReport(xlsx_file)
    outputer_excel.add_reportset(reportset)
    outputer_excel.close()



def main(args=None):

    # Parsing arguments
    p_args = parse_args(args)
    # Building report
    build_cli_report(p_args.gnucash_file, p_args.xlsx_file, p_args.glevel)


if __name__ == "__main__":
    sys.exit(main())
