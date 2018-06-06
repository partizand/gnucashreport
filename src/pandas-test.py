import decimal
import pandas
import numpy
import pytz
from decimal import Decimal
# import gnucashreport

from datetime import datetime


from gnucashreport.rawdata import RawData

line1 = [{'date': '01.01.2016', 'value': 10, 'account': 'Активы:Текущие:Карта', 'guid': '10'},
         {'date': '02.01.2016', 'value': 50, 'account': 'Активы:Текущие:Карта', 'guid': '10'},
         {'date': '01.02.2016', 'value': 100, 'account': 'Активы:Текущие:Карта', 'guid': '10'},
         {'date': '05.02.2016', 'value': 100.2, 'account': 'Активы:Текущие:Карта', 'guid': '10'},
         {'date': '05.03.2016', 'value': 500, 'account': 'Активы:Текущие:Карта', 'guid': '10'},
         {'date': '01.01.2016', 'value': 55, 'account': 'Активы:Текущие:Вклад', 'guid': '20'},
         {'date': '01.01.2016', 'value': 57, 'account': 'Активы:Текущие:Вклад', 'guid': '20'},
         {'date': '01.02.2016', 'value': 57, 'account': 'Активы:Текущие:Вклад', 'guid': '20'},
         {'date': '01.01.2016', 'value': 102, 'account': 'Активы:Резервы:Сбер вклад', 'guid': '30'},
         {'date': '02.01.2016', 'value': 50, 'account': 'Активы:Резервы:Сбер вклад', 'guid': '30'},
         {'date': '01.02.2016', 'value': 100, 'account': 'Активы:Резервы:Сбер вклад', 'guid': '30'},
         {'date': '05.02.2016', 'value': 100.2, 'account': 'Активы:Резервы:Сбер вклад', 'guid': '30'},
         {'date': '05.03.2016', 'value': 500, 'account': 'Активы:Резервы:Сбер вклад', 'guid': '30'},
         {'date': '01.01.2016', 'value': 55, 'account': 'Активы:Резервы:Наличность', 'guid': '40'},
         {'date': '01.01.2016', 'value': 57, 'account': 'Активы:Резервы:Наличность', 'guid': '40'},
         {'date': '01.02.2016', 'value': 57, 'account': 'Активы:Резервы:Наличность', 'guid': '40'},
         ]

prices = [
    {'date': '01.01.2016', 'value': '60', 'mnemonic': 'EUR'},
    {'date': '29.01.2016', 'value': '65', 'mnemonic': 'EUR'},
    {'date': '31.01.2016', 'value': '67', 'mnemonic': 'EUR'},
    {'date': '31.01.2016', 'value': '30', 'mnemonic': 'USD'},
    {'date': '01.02.2016', 'value': '68', 'mnemonic': 'EUR'},
    {'date': '29.02.2016', 'value': '65', 'mnemonic': 'EUR'},
    {'date': '28.02.2016', 'value': '63', 'mnemonic': 'EUR'},
    {'date': '28.04.2016', 'value': '70', 'mnemonic': 'EUR'},


]


def read_from_excel(filename, sheet):
    """
    Чтение dataframe из Excel
    :param filename:
    :param sheet:
    :return: DataFrame
    """
    xls = pandas.ExcelFile(filename)

    df = xls.parse(sheet)

    xls.close()
    return df

#guid = list(range(10, (len(line1)+1)*10, 10))
#index = list(map(chr, range(97, 97+len(line1))))
#index = list(range(10))

cur_date = datetime.now()

xml_date = "2016-12-31 00:00:00 +0300"
pd_date = pandas.to_datetime(xml_date)

value = decimal.Decimal('1')
# Test add row to dataframe
df = pandas.DataFrame(columns=['guid', 'col1', 'col2'])
# df.set_index('guid', inplace=True)
# print(df)
dict1 = {'guid': 1, 'col1':pd_date, 'col2':value, 'dec':decimal.Decimal('0.1')}
dict2 = {'guid': 2, 'col1':pd_date, 'col2':value, 'dec':decimal.Decimal('0.1')}
# df.loc['123'] = {'col1':1, 'col2':2}
df = df.append(dict1, ignore_index=True)
df = df.append(dict2, ignore_index=True)
df['col3'] = df['col2'].astype(Decimal)
# print(type(df.loc[0]['dec']))
print(type(df['col1'].dtype))
# if (df['col1'].dtype) == numpy.date .startswith('datetime'):
#     print('checked')
if pandas.api.types.is_datetime64_any_dtype(df['col1'].dtype):
    print('checked')
else:
    print('not checked')
exit()

rep = RawData()

# Исходный DataFrame
df = pandas.DataFrame(line1)
pr = pandas.DataFrame(prices)
# Дата в datetime формат
df['date']=pandas.to_datetime(df['date'], format='%d.%m.%Y')
pr['date']=pandas.to_datetime(pr['date'], format='%d.%m.%Y')

# df.rename(columns={'value': 'quant'}, inplace=True)
# df['value'] = df['value'].astype(numpy.dtype(Decimal))
# df['value'] = df['value'].map(lambda x:Decimal(repr(x)))
# df['value'] = df['value'].astype(numpy.float64)

df = df.set_index('guid', append=True)
# print(df)
print(df.index)

df_new = pandas.DataFrame(data=None, index=df.index, columns=df.columns)
df_new = df_new.dropna()
# df_sum= df.sum()
df_new.loc[0, '10'] = df.sum()
print(df_new.index)
print(df_new)
exit()


arrays = [['bar', 'bar', 'baz', 'baz', 'foo', 'foo', 'qux', 'qux'],
            ['one', 'two', 'one', 'two', 'one', 'two', 'one', 'two']]


tuples = list(zip(*arrays))

index = pandas.MultiIndex.from_tuples(tuples, names=['first', 'second'])

s = pandas.Series(numpy.random.randn(8), index=index)

d = {'values': s}

# df = pandas.DataFrame(d)


for col in df.index.names:
     df = df.unstack(col)
     df[('values', 'total')] = df.sum(axis=1)
     df = df.stack()

print(df)

# Удаляет все из DataFrame
# df = df.drop(df.index)
# print(df.index)
exit()

df_sum=pandas.DataFrame(data=df.sum()).T
df_sum=df_sum.reindex(columns=df.columns)
df_final=df.append(df_sum,ignore_index=False)
print(df_final)

# Работает но не суммирует decimal и нет строки итого

# print(df_t)



exit()

# Создание datarame c одной строкой итогов
if isinstance(df.index, pandas.core.index.MultiIndex):
    icount = len(df.index.names)
    icols = ['' for i in range(1, icount)]
    icols = ['Total'] + icols
    index = tuple(icols)
    # cols = ['1', '2', '3']

    mindex = pandas.MultiIndex.from_tuples([index])
    # df_ret = dataframe
    # df_ret.loc[index] = df_ret.sum()

    # df_total = pandas.DataFrame( index=mindex, columns=cols)
else:
    index = ['Total']
df_total = df.drop(df.index)
print(df.index)
print(df_total.index)
# df_total.loc[index] = 1
print(df_total)

# Работает но не суммирует decimal и нет строки итого
# df = df.append(df.sum(), ignore_index=True)
# print(df)

exit()

# df = df.drop(['date', 'account', 'guid'], axis=1)
df_t = RawData.add_row_total(df)
print(df_t)
exit()

cols = 3
c = ['' for i in range(1, cols)]
c = ['Profit'] + c
index = tuple(c)
cols = ['1','2','3']

mindex = pandas.MultiIndex.from_tuples([index])

df_t = pandas.DataFrame(index=mindex, columns=cols)
if isinstance(df_t.index, pandas.core.index.MultiIndex):
    print('isMulti')
else:
    print('isSingle')
print(df_t)
# print(df_t.index)

# Получение имени колонок
# cols = df.columns.values.tolist()
# print(type(cols))
# print(cols)
#
# df.set_index('date', inplace=True)
# idxs = df.index.names
# print(type(idxs))
# print(idxs)

exit()

list1 = [0, 0, 0, 0]
list2 = [0, 1, 0, 0]
df_n = pandas.DataFrame(list1)
df_nn = pandas.DataFrame(list2)
# print(df_n)
# exit()
# ar = df_nn[0].nonzero()
# print(ar)
# exit()
# print(df_nn[0].apply(lambda x: x == 0).all())
has_bal = not (df_n[0].apply(lambda x: x == 0).all())
if has_bal:
    print('Значения')
else:
    print('Пусто')
exit()

# Загрузка балансов из excel
filename = "U:/tables/balances.xlsx"
df_bal = read_from_excel(filename, "Sheet1")
# print(df_bal)
df_bal.set_index(['post_date','fullname'], inplace=True)
# df_bal = df_bal.resample('D').ffill()
rep.dataframe_to_excel(df_bal, 'df_bal')
exit()

# df['value'] = df['value'].map(lambda x:float64)

# a=df['value'][6]
# print(a)
# print(type(a))
# print(df['value'].dtype)
# exit()
# fil = df[df['value'].isin([100, 57])]

# Индекс по периоду
idx = pandas.date_range("2016-01-01", "2016-12-31", freq="M")
print(idx)

# df['cumsum'] = df.groupby(['account'])['value'].transform(pandas.Series.cumsum)

# print(df)
exit()

# sel_df = df.groupby(['account', 'date', 'guid']).value.sum().groupby(level=[0]).cumsum() #.reset_index()
# sel_df = sel_df.apply(lambda x:Decimal(repr(x)))

# df['cumvalue']=df['value'].cumsum()
# a = sel_df[5]
# print(a)
# print(type(a))

print(sel_df)

exit()


# Загрузка сводной таблицы из excel
filename = "U:/tables/grouped_acc1.xlsx"
group_acc = read_from_excel(filename, "Sheet1")
filename = "U:/tables/prices.xlsx"
group_prices = read_from_excel(filename, "Sheet1")

# добавляем Курс рубля
# idx = pandas.date_range("2016-01-01", "2016-12-31", freq="M")
# rub = {'value': 1., 'mnemonic': 'RUB'}
# df_rub=pandas.DataFrame(rub ,idx)
# group_prices = group_prices.append(df_rub)

group_prices = group_prices.reset_index()
group_prices.rename(columns={'index': 'date'}, inplace=True)
group_prices.rename(columns={'value': 'course'}, inplace=True)

# print(group_prices)
# exit()

# print(group_acc)
# exit()
# Добавление колонки курс
g_a_p = group_acc.merge(group_prices, left_on=['post_date','mnemonic'], right_on=['date','mnemonic'], how='left')
# Заполнить пустые поля еденицей
g_a_p['course'] = g_a_p['course'].fillna(1.)
# Пересчет в валюту представления
g_a_p['val']=g_a_p['value'] * g_a_p['course']
# Теперь в колонке val реальная сумма в рублях


gap_eur = g_a_p[(g_a_p['mnemonic'] == 'EUR')]
print(gap_eur)
print(g_a_p)

exit()



# guid
#df['guid']=guid
# Разбить полное имя счета на колонки
# s = df['account'].str.split(':', expand=True)
# cols = s.columns
# cols=cols.tolist()
# df = pandas.concat([df, s], axis=1)
# df.set_index(cols, append=True, inplace=True)
#mems= df.loc[df['date'] > '20160101', ['date', 'value']]
#print(mems)
#print(pr)

# Группировка по месяцу
# Индекс по периоду
idx = pandas.date_range("2016-01-01", "2016-12-31", freq="M")
t = pytz.timezone('Europe/Moscow')
print (t.zone)
idx.tz_localize(pytz.timezone('Europe/Moscow'))
print(idx.dtype)
exit()
# Попытка создать мультииндекс
# iterables = [idx, ['EUR', 'USD']]
# midx = pandas.MultiIndex.from_product(iterables, names=['date', 'mnemonic'])
# print(midx)

# Список mnemonic
mnem_list = pr['mnemonic'].drop_duplicates().tolist()
print(mnem_list)

# цикл по всем
group_prices = None
for mnemonic in mnem_list:

    # Берем только евро
    pr_eur=pr[pr['mnemonic'] == mnemonic]
    pr_eur.set_index(['date'], inplace=True)
    # print(pr)
    # ndf = pr.resample('M').last()
    # ndf = pr.groupby([pandas.TimeGrouper('M'), 'mnemonic']).value.last() #.reset_index()
    ndf = pr_eur.groupby([pandas.TimeGrouper('M'), 'mnemonic']).value.last().reset_index() #.set_index(['date'], inplace=True)
    ndf.set_index(['date'], inplace=True)
    ndf = ndf.reindex(idx, method='nearest')
    if group_prices is None:
        group_prices=ndf
    else:
        group_prices = group_prices.append(ndf)
    # print(ndf)
print(group_prices)

exit(0)

# Группировка по месяцу
df.set_index('date', inplace=True)
ndf = df.groupby([pandas.TimeGrouper('M'), 'account', 'guid']).value.sum().reset_index()
# Добавление MultiIndex по дате и названиям счетов
s = ndf['account'].str.split(':', expand=True)
cols = s.columns
cols=cols.tolist()
cols = ['date'] + cols
ndf = pandas.concat([ndf, s], axis=1)
ndf.set_index(cols, inplace=True)
print(ndf)

# Группировка по нужному уровню
ndf = ndf.groupby(level=[0,2]).sum().reset_index()
print(ndf)

# Переворот в сводную
pivot_t = pandas.pivot_table(ndf, index=1, values='value', columns='date',aggfunc=numpy.sum, fill_value=0)

print(pivot_t)
print(pivot_t.index)
exit(0)


s = ndf[ndf['date']=='20160131']
print(s)
s = ndf[ndf['guid']=='40'][ndf['date'] == '20160131']
print(s)
#val = s[s['guid'] == '40'] #['guid' == '40']

exit(0)

#df['month'] = df['date'].map(lambda x: x.strftime("%m-%Y"))
# print(df)


# Сводная таблица
# margins - выводить итоги
#fill_value - заполнять нулями
#months = df['date'].map(lambda x: x.month)
#pivot_t = pandas.pivot_table(df, index=['account'], columns='month', values=['value'],aggfunc=numpy.sum, fill_value=0, margins=True)
# print('\nСводная таблица\n')
# print(pivot_t)

# Сводная таблица наоборот
# margins - выводить итоги
#fill_value - заполнять нулями
#months = df['date'].map(lambda x: x.month)
#pivot_t2 = pandas.pivot_table(df, index=pandas.DatetimeIndex(df['date']), columns='account', values=['value'],aggfunc=numpy.sum, fill_value=0)
pivot_t2 = pandas.pivot_table(df, index='date', columns='guid', values='value', aggfunc='sum', fill_value=0)
pivot_t3 = pivot_t2.resample('M').sum()
print('\nСводная таблица наоборот resample\n')
print(pivot_t3)

#nal = pivot_t3.loc[pivot_t3['account'] == 40]

print(pivot_t3['10'])

exit(0)

pivot_t4 = pivot_t3.transpose()
print('\nСводная таблица pivot\n')
print(pivot_t4)

# Найти счет

print(pivot_t4['account'])

