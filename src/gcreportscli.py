import argparse
import datetime
import time
import pandas
from pandas.util.testing import assert_frame_equal
from gcreports.repbuilder import RepBuilder
# import gcreports.repbuilder as repbuilder




rep = RepBuilder()
# from_date = datetime.datetime(2016,1,1,0,0,0,0)
# to_date = datetime.datetime(2016,12,31,23,59,59,0)
from_date = datetime.date(2016, 1, 1)
to_date = datetime.date(2016, 12, 31)
# start_time = time.time()
rep.open_book("u:/sqllite_book/real-2017-01-26.gnucash", open_if_lock=True)
# print("Loading from sqlite --- %s seconds ---" % (time.time() - start_time))
# rep.to_excel()

# start_time = time.time()
# rep.read_from_excel()
# print("Loading from excel --- %s seconds ---" % (time.time() - start_time))

# print(rep.df_prices)
# RUB GUID b2532663368050adfeb100f2887a56f8
# eur = rep.df_prices.loc[rep.df_prices['mnemonic'] == 'EUR', ['date', 'value']]
# print(eur)
#
# filename='U:/test_data/prices.pkl'
pr = rep.group_prices_by_period(from_date=from_date, to_date=to_date)
# pr.to_pickle(filename)
# pr = pr.reset_index()
# rep.dataframe_to_excel(pr, filename)

# pr_etalon = pandas.read_pickle(filename)

# pr_etalon = RepBuilder.read_dataframe_from_excel(filename)
# pr_etalon.set_index(['commodity_guid', 'date'], inplace=True)

# print(pr_etalon['date'].dtype)
# print(pr['date'].dtype)
# pr = pandas.DataFrame()
# print(pr_etalon.columns)
# print(pr_etalon.index)
# assert_frame_equal(pr, pr_etalon, check_like=True) #, check_names=False)
# a = pr_etalon == pr
# print(a)


# print(pr.head())

# acc = 'Активы:Текущие активы:Карта ВТБ'
# acc = 'Активы:Долгосрочные активы:Ценные бумаги:Промсвязь ИИС:Газпром а.о.'
# acc = 'Активы:Долгосрочные активы:Ценные бумаги:Промсвязь ИИС:МТС'
# acc = 'Активы:Долгосрочные активы:Ценные бумаги:Альфа-Директ:Югра Рентный Фонд'
# balance = rep.get_balance_stock(acc)
# print(balance)

# df = rep.balance_by_period(from_date=from_date, to_date=to_date)
# rep.dataframe_to_excel(df, 'balance-exp')
# filename='U:/test_data/assets.pkl'
# df.to_pickle(filename)
# pr = pr.reset_index()

# a = rep.get_balance(acc)
# print(a)

# df = rep.turnover_by_period(from_date=from_date, to_date=to_date, account_type=RepBuilder.EXPENSE)
# filename='U:/test_data/expense.pkl'
# df.to_pickle(filename)
# rep.dataframe_to_excel(df, "itog-expense2")

#print(df)