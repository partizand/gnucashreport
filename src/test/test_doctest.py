"""
Doctest implementation into unittest
"""

import unittest
import doctest

import gnucashreport
# import gnucashreport.gcreport
import gnucashreport.xlsxreport
import gnucashreport.financial
import gnucashreport.utils
import gnucashreport.reportset


def load_tests(*args, **kwargs):
    test_all_doctests = unittest.TestSuite()
    # test_all_doctests.addTest(doctest.DocTestSuite(gnucashreport.gcreport))
    # test_all_doctests.addTest(doctest.DocTestSuite(gnucashreport.xlsxreport))
    test_all_doctests.addTest(doctest.DocTestSuite(gnucashreport.financial))
    test_all_doctests.addTest(doctest.DocTestSuite(gnucashreport.utils))
    test_all_doctests.addTest(doctest.DocTestSuite(gnucashreport.reportset))
    # test_all_doctests.addTest(doctest.testfile('D:\\Documents\\programming\\gcreports\\readme.rst'))
    return test_all_doctests


if __name__ == '__main__':
    # doctest.testfile('D:\\Documents\\programming\\gcreports\\readme.rst')
    unittest.main()