import pandas
import numpy
import pytz


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

# Исходный DataFrame
df = pandas.DataFrame(line1)
pr = pandas.DataFrame(prices)
# Дата в datetime формат
df['date']=pandas.to_datetime(df['date'], format='%d.%m.%Y')
pr['date']=pandas.to_datetime(pr['date'], format='%d.%m.%Y')

pr['value']=pandas.to_numeric(pr['value'])
pr['value']=pr['value'].astype('str')

print(pr['value'].dtype)

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

