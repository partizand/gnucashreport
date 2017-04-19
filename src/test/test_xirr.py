import unittest

import os

from decimal import Decimal



import gnucashreport.gnucashdata
import gnucashreport.cols as cols
# from gnucashreport.utils import dataframe_to_excel
from gnucashreport.utils import *

from test.baseopentest import BaseOpenTest


class XIRRTest(unittest.TestCase):
    """
    Тестирование правильности расчета доходности
    
    Доходность проверяется за весь период существования счета
    
    Для тестирования, создайте базу GnuCash с именем xirr-test.gnucash в подкаталоге data этого файла
    Создайте проводки
    Для тестируемых счетов, задайте их эталонные доходности в описании счета
    Если счет тестировать не нужно, описание счета не заполняйте!
    Доходность в описании можно задать либо просто итоговую, числом доходоности
    Например 0,1 - доходность 10% годовых, остальные доходности = 0, capital_gain = 0,1
    Или задавайте доходности парами тип_доходности1=значение1 тип_доходности2=значение2
    Тип доходности можно посмотреть в файле cols.py 
    """

    gcrep = gnucashreport.gnucashdata.GNUCashData()
    test_datas = []

    @classmethod
    def setUpClass(cls):

        base_path = os.path.dirname(os.path.realpath(__file__))
        base_path = os.path.join(base_path, 'data', 'xirr-test.gnucash')
        cls.gcrep.open_book_file(base_path, open_if_lock=True)
        cls.get_testaccounts()

    @classmethod
    def get_testaccounts(cls):
        """
        Получает список account_guid и его доходности из описания
        :return: 
        """

        df_test = cls.gcrep.df_accounts[~cls.gcrep.df_accounts[cols.DESCRIPTION].isnull()]
        for index, row in df_test.iterrows():
            entries = parse_string_to_dict(row[cols.DESCRIPTION], parse_to_decimal=True)
            if not entries:
                # yield_etalon = Decimal((row[cols.DESCRIPTION]).replace(',','.'))
                entries[cols.YIELD_TOTAL] = decimal_from_string(row[cols.DESCRIPTION])
                entries[cols.YIELD_CAPITAL] = entries[cols.YIELD_TOTAL]
            # test_data = {cols.ACCOUNT_GUID: index, 'yield_etalon': yield_etalon}
            test_data = {cols.ACCOUNT_GUID: index, cols.SHORTNAME: row[cols.SHORTNAME]}
            test_data.update(entries)
            cls.test_datas.append(test_data)


    def test_accounts(self):
        for test_data in self.test_datas:
            account_guid = test_data[cols.ACCOUNT_GUID]
            etalon_yield_total = test_data.get(cols.YIELD_TOTAL, Decimal(0))
            etalon_yield_income = test_data.get(cols.YIELD_INCOME, Decimal(0))
            etalon_yield_expense = test_data.get(cols.YIELD_EXPENSE, Decimal(0))
            etalon_yield_capital = test_data.get(cols.YIELD_CAPITAL, Decimal(0))

            xirr_yield = self.gcrep._xirr_calc(account_guid=account_guid)
            checking_yield_total = xirr_yield[cols.YIELD_TOTAL]
            checking_yield_income = xirr_yield[cols.YIELD_INCOME]
            checking_yield_expense = xirr_yield[cols.YIELD_EXPENSE]
            checking_yield_capital = xirr_yield[cols.YIELD_CAPITAL]

            self.assertEquals(etalon_yield_total, checking_yield_total,
                              'testing {gain} in account {shortname}'.
                              format(shortname=test_data[cols.SHORTNAME], gain=cols.YIELD_TOTAL))
            self.assertEquals(etalon_yield_income, checking_yield_income,
                             'testing {gain} in account {shortname}'.
                              format(shortname=test_data[cols.SHORTNAME], gain=cols.YIELD_INCOME))
            self.assertEquals(etalon_yield_expense, checking_yield_expense,
                              'testing {gain} in account {shortname}'.
                              format(shortname=test_data[cols.SHORTNAME], gain=cols.YIELD_EXPENSE))
            self.assertEquals(etalon_yield_capital, checking_yield_capital,
                              'testing {gain} in account {shortname}'.
                              format(shortname=test_data[cols.SHORTNAME], gain=cols.YIELD_CAPITAL))


if __name__ == '__main__':
    unittest.main()