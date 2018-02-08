from datetime import date

import os


class TestInfo:

    # Данные для генерации тестовых данных и тестирования
    # Test info, change before generate test data!
    BOOKFILE_SQL = 'v:/gnucash-base/sqlite/GnuCash-base.gnucash'
    BOOKFILE_XML = 'v:/gnucash-base/xml/GnuCash-base.gnucash'
    DIR_TESTDATA = 'v:/test_data'
    GNUCASH_TESTBASE_XML = 'data/xirr-test.gnucash'
    GNUCASH_TESTBASE_SQL = 'data/xirr-test-sql.gnucash'

    # end folder options---------------------------------------
    TEST_FROM_DATE = date(2016, 1, 1)
    TEST_TO_DATE = date(2016, 12, 31)
    TEST_FROM_DATE_Y = date(2009, 1, 1)
    TEST_TO_DATE_Y = date(2016, 12, 31)
    TEST_PERIOD = 'M'
    TEST_GLEVEL = 1
    TEST_GLEVEL2 = [0, 1]
    TEST_LEVEL2_SUFFIX = '-2'
    # end test info--------------------------------------------

    # rep = GNUCashData()


    # dir_testdata = GNUCashData.dir_testdata

    # pickle_prices = 'prices.pkl'
    # pickle_splits = 'splits.pkl'
    # pickle_accounts = 'accounts.pkl'
    # pickle_tr = 'transactions.pkl'
    # pickle_commodities = 'commodities.pkl'

    # pickle_prices = GNUCashData.pickle_prices  # 'prices.pkl'
    # pickle_splits = GNUCashData.pickle_splits  # 'splits.pkl'
    # pickle_accounts = GNUCashData.pickle_accounts  # 'accounts.pkl'
    # pickle_tr = GNUCashData.pickle_tr  # 'transactions.pkl'
    # pickle_commodities = GNUCashData.pickle_commodities  # 'commodities.pkl'

    PICKLE_ASSETS = 'assets.pkl'
    PICKLE_LOANS = 'loans.pkl'
    PICKLE_EXPENSE = 'expense.pkl'
    PICKLE_INCOME = 'income.pkl'
    PICKLE_PROFIT = 'profit.pkl'
    PICKLE_EQUITY = 'equity.pkl'
    PICKLE_INFLATION = 'inflation.pkl'

    @classmethod
    def get_abs_filename(cls, filename):
        if os.path.isabs(filename):
            return filename
        else:
            base_path = os.path.dirname(os.path.realpath(__file__))
            base_path = os.path.join(base_path, filename)
            return base_path