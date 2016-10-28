import pandas
import numpy


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
    {'date': '01.01.2016', 'value': 60, 'mnemonic': 'EUR'},
    {'date': '29.01.2016', 'value': 65, 'mnemonic': 'EUR'},
    {'date': '31.01.2016', 'value': 67, 'mnemonic': 'EUR'},
    {'date': '31.01.2016', 'value': 30, 'mnemonic': 'USD'},
    {'date': '01.02.2016', 'value': 68, 'mnemonic': 'EUR'},
    {'date': '29.02.2016', 'value': 65, 'mnemonic': 'EUR'},
    {'date': '28.02.2016', 'value': 60, 'mnemonic': 'EUR'},
    {'date': '28.04.2016', 'value': 70, 'mnemonic': 'EUR'},


]

#guid = list(range(10, (len(line1)+1)*10, 10))
#index = list(map(chr, range(97, 97+len(line1))))
#index = list(range(10))

# Исходный DataFrame
df = pandas.DataFrame(line1)
pr = pandas.DataFrame(prices)
# Дата в datetime формат
df['date']=pandas.to_datetime(df['date'], format='%d.%m.%Y')
pr['date']=pandas.to_datetime(pr['date'], format='%d.%m.%Y')
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
pr.set_index(['date'], inplace=True)
# ndf = pr.resample('M').last()
ndf = pr.groupby([pandas.TimeGrouper('M'), 'mnemonic']).value.last().reset_index()
print(ndf)

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

