"""
Doctest implementation into unittest
"""

import unittest
import doctest

import gnucashreport
import gnucashreport.gnucashreport


def load_tests(*args, **kwargs):
    test_all_doctests = unittest.TestSuite()
    # test_all_doctests.addTest(doctest.DocTestSuite(gnucashreport.gnucashreport))
    # test_all_doctests.addTest(doctest.testfile('D:\\Documents\\programming\\gcreports\\readme.rst'))
    return test_all_doctests


if __name__ == '__main__':
    # doctest.testfile('D:\\Documents\\programming\\gcreports\\readme.rst')
    unittest.main()