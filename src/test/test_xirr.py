import unittest

import os

from decimal import Decimal

import gnucashreport.gnucashdata
import gnucashreport.cols as cols

from test.baseopentest import BaseOpenTest


class SQLOpenTest(unittest.TestCase):
    """
    Тестирование правильности расчета доходности
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
            yield_etalon = Decimal((row[cols.DESCRIPTION]).replace(',','.'))
            test_data = {cols.ACCOUNT_GUID: index, 'yield_etalon': yield_etalon}
            cls.test_datas.append(test_data)


    def test_accounts(self):
        for test_data in self.test_datas:
            account_guid = test_data[cols.ACCOUNT_GUID]
            etalon_yield = test_data['yield_etalon']
            xirr_yield = self.gcrep._xirr_calc(account_guid=account_guid)
            checking_yield = xirr_yield['yield_total']

            self.assertEquals(etalon_yield, checking_yield)



if __name__ == '__main__':
    unittest.main()