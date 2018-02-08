import unittest

import os

from decimal import Decimal

import datetime

import gnucashreport.gnucashdata
import gnucashreport.cols as cols
# from gnucashreport.utils import dataframe_to_excel
from gnucashreport.utils import *

from test.basetest import BaseTest

from test.baseopentest import BaseOpenTest

TOTAL = 'total'
INCOME = 'income'
EXPENSE = 'expense'
CAPITAL = 'capital'
TO_DATE = 'todate'
FROM_DATE = 'fromdate'

# GNUCASH_TESTBASE = 'data/xirr-test-sql.gnucash'

class XIRRTest(unittest.TestCase):
    """
    Тестирование правильности расчета доходности
    
    Доходность проверяется за весь период существования счета
    
    Для тестирования, создайте базу GnuCash (xml или sqlite) с именем xirr-test.gnucash в подкаталоге data этого файла
    Создайте проводки
    Для тестируемых счетов, задайте их эталонные доходности в описании счета
    Если счет тестировать не нужно, описание счета не заполняйте, или добавьте skip в описание
    Доходность в описании можно задать либо просто итоговую, числом доходоности
    Например 0,1 - доходность 10% годовых, остальные доходности = 0, capital_gain = 0,1
    Или задавайте доходности парами тип_доходности1=значение1 тип_доходности2=значение2
    Тип доходности можно посмотреть константах сверху этого файла 
    """

    gcrep = gnucashreport.gnucashdata.GNUCashData()
    test_datas = []

    @classmethod
    def setUpClass(cls):

        base_path = os.path.dirname(os.path.realpath(__file__))
        base_path = os.path.join(base_path, BaseTest.GNUCASH_TESTBASE_XML)
        cls.gcrep.open_book_file(base_path)
        cls.get_testaccounts()

    @classmethod
    def get_testaccounts(cls):
        """
        Получает список account_guid и его доходности из описания
        :return: 
        """

        only_test = None
        # df_test = cls.gcrep.df_accounts[~cls.gcrep.df_accounts[cols.DESCRIPTION].isnull()]
        df_test = cls.gcrep.df_accounts[cls.gcrep.df_accounts[cols.DESCRIPTION]!='']
        for index, row in df_test.iterrows():
            if 'skip' not in row[cols.DESCRIPTION]:
                entries = parse_string_to_dict(row[cols.DESCRIPTION])
                if not entries:
                    # yield_etalon = Decimal((row[cols.DESCRIPTION]).replace(',','.'))
                    entries[TOTAL] = decimal_from_string(row[cols.DESCRIPTION])
                    # entries[cols.YIELD_CAPITAL] = entries[cols.YIELD_TOTAL]
                # test_data = {cols.ACCOUNT_GUID: index, 'yield_etalon': yield_etalon}
                test_data = {cols.ACCOUNT_GUID: index, cols.SHORTNAME: row[cols.SHORTNAME]}
                test_data.update(entries)
                cls.test_datas.append(test_data)
                if 'only' in row[cols.DESCRIPTION]:
                    only_test = test_data

        if only_test:
            cls.test_datas = [only_test]


    def test_accounts(self):
        for test_data in self.test_datas:
            account_guid = test_data[cols.ACCOUNT_GUID]
            etalon_yield_total = Decimal(test_data.get(TOTAL, Decimal(0)))
            etalon_yield_income = Decimal(test_data.get(INCOME, Decimal(0)))
            etalon_yield_expense = Decimal(test_data.get(EXPENSE, Decimal(0)))
            etalon_yield_capital = Decimal(test_data.get(CAPITAL, etalon_yield_total-etalon_yield_income))

            # str_from_date = test_data.get(FROM_DATE, None)
            # str_to_date = test_data.get(TO_DATE, None)

            from_date = self._date_from_str(test_data.get(FROM_DATE, None))
            to_date = self._date_from_str(test_data.get(TO_DATE, None))

            xirr_yield = self.gcrep.yield_calc(account_guid=account_guid,
                                               from_date=from_date, to_date=to_date,
                                               recurse=False, rename_col=False)
            # if xirr_yield.empty
            checking_yield_total = xirr_yield.iloc[0][cols.YIELD_TOTAL]
            checking_yield_income = xirr_yield.iloc[0][cols.YIELD_INCOME]
            checking_yield_expense = xirr_yield.iloc[0][cols.YIELD_EXPENSE]
            checking_yield_capital = xirr_yield.iloc[0][cols.YIELD_CAPITAL]

            self.assertEqual(etalon_yield_total, checking_yield_total,
                              'testing {gain} in account {shortname}'.
                              format(shortname=test_data[cols.SHORTNAME], gain=cols.YIELD_TOTAL))
            self.assertEqual(etalon_yield_income, checking_yield_income,
                              'testing {gain} in account {shortname}'.
                              format(shortname=test_data[cols.SHORTNAME], gain=cols.YIELD_INCOME))
            self.assertEqual(etalon_yield_expense, checking_yield_expense,
                              'testing {gain} in account {shortname}'.
                              format(shortname=test_data[cols.SHORTNAME], gain=cols.YIELD_EXPENSE))
            self.assertEqual(etalon_yield_capital, checking_yield_capital,
                              'testing {gain} in account {shortname}'.
                              format(shortname=test_data[cols.SHORTNAME], gain=cols.YIELD_CAPITAL))

    def _date_from_str(self, str_date):
        if str_date:
            a_date = datetime.datetime.strptime(str_date, '%d-%m-%y').date()
            return a_date
        else:
            return None

if __name__ == '__main__':
    unittest.main()