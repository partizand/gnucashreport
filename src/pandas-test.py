import pandas
import numpy

# id     date        value   account
# 0  01.01.2016       10     Активы
# 1  02.01.2016       100     Активы
# 1  02.01.2016       100     Активы



line1 = [{'date': '01.01.2016', 'value': 10, 'account': 'Активы:Текущие:Карта'},
         {'date': '02.01.2016', 'value': 50, 'account': 'Активы:Текущие:Карта'},
         {'date': '01.02.2016', 'value': 100, 'account': 'Активы:Текущие:Карта'},
         {'date': '05.02.2016', 'value': 100.2, 'account': 'Активы:Текущие:Карта'},
         {'date': '05.03.2016', 'value': 500, 'account': 'Активы:Текущие:Карта'},
         {'date': '01.01.2016', 'value': 55, 'account': 'Активы:Текущие:Вклад'},
         {'date': '01.01.2016', 'value': 57, 'account': 'Активы:Текущие:Вклад'},
         {'date': '01.02.2016', 'value': 57, 'account': 'Активы:Текущие:Вклад'},
         {'date': '01.01.2016', 'value': 10, 'account': 'Активы:Резервы:Сбер вклад'},
         {'date': '02.01.2016', 'value': 50, 'account': 'Активы:Резервы:Сбер вклад'},
         {'date': '01.02.2016', 'value': 100, 'account': 'Активы:Резервы:Сбер вклад'},
         {'date': '05.02.2016', 'value': 100.2, 'account': 'Активы:Резервы:Сбер вклад'},
         {'date': '05.03.2016', 'value': 500, 'account': 'Активы:Резервы:Сбер вклад'},
         {'date': '01.01.2016', 'value': 55, 'account': 'Активы:Резервы:Наличность'},
         {'date': '01.01.2016', 'value': 57, 'account': 'Активы:Резервы:Наличность'},
         {'date': '01.02.2016', 'value': 57, 'account': 'Активы:Резервы:Наличность'},
         ]

#index = list(range(10, (len(line1)+1)*10, 10))
index = list(map(chr, range(97, 97+len(line1))))
#index = list(range(10))

# Исходный DataFrame
df = pandas.DataFrame(line1)
# Дата в datetime формат
df['date']=pandas.to_datetime(df['date'], format='%d.%m.%Y')
# Разбить полное имя счета на колонки
s = df['account'].str.split(':', expand=True)
df = pandas.concat([df, s], axis=1)
#print(df)

# Доступ по индексу
s = pandas.Series(index)
df['id']= s #.set_index(index, inplace=True)
df.set_index('id',inplace=True)
row=df.ix['l']['account']
print(row)
#print(index)

exit(0)

# Перебрать построчно
for index, row in df.iterrows():
    print(row['date'], row['account'], row['value'])

exit(0)

# Групировка по сумме
df_group = df.groupby([0,1]).sum() #.sum()
#print(df_group.head())
#exit(0)


# Группировка по месяцу
df.set_index('date', inplace=True)
ndf = df.resample('M').sum()
print(ndf)
exit(0)
#df_mon = df.resample() ('M', how='sum')
#print(df_mon)

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
pivot_t2 = pandas.pivot_table(df_group, index=pandas.DatetimeIndex(df['date']), columns='account', values=['value'],aggfunc=numpy.sum, fill_value=0)
pivot_t3 = pivot_t2.resample('M').sum()
print('\nСводная таблица наоборот resample\n')
print(pivot_t3)

pivot_t4 = pivot_t3.transpose()
print('\nСводная таблица pivot\n')
print(pivot_t4)