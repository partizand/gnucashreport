"""
Doctest implementation into unittest
"""

import unittest
import doctest

import gnucashreport
import gnucashreport.gnucashreport


def load_tests(*args, **kwargs):
    test_all_doctests = unittest.TestSuite()
    test_all_doctests.addTest(doctest.DocTestSuite(gnucashreport.gnucashreport))
    return test_all_doctests


if __name__ == '__main__':
    unittest.main()