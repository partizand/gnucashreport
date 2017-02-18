# Работает, но кривовато

import unittest
import doctest

import gcreports
import gcreports.gnucashreport


# def load_tests(loader, tests, ignore):
#     tests.addTests(doctest.DocTestSuite(GNUCashData))
#     return tests

def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(gcreports.gnucashdata.GNUCashData))

    return suite

# suite = unittest.TestSuite()
testSuite = unittest.TestSuite()
testSuite.addTest(doctest.DocTestSuite(gcreports.gnucashreport))
# testSuite.addTest(doctest.DocTestSuite('gcreports.gnucashreport'))
# testSuite.addTest(doctest.DocTestSuite())

unittest.TextTestRunner(verbosity = 2).run(testSuite)

# if __name__ == '__main__':
#     unittest.main()