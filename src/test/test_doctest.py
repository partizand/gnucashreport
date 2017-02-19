"""
Doctest implementation into unittest
"""

import unittest
import doctest

import gcreports
import gcreports.gnucashreport


def load_tests(*args, **kwargs):
    test_all_doctests = unittest.TestSuite()
    test_all_doctests.addTest(doctest.DocTestSuite(gcreports.gnucashreport))
    return test_all_doctests


if __name__ == '__main__':
    unittest.main()