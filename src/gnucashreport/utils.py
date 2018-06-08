import calendar
import os

import pandas
import re

from decimal import Decimal

# from datetime import date
import datetime

# from gnucashreport import const

DIR_EXCEL = "v:/tables"




def dataframe_to_excel(dataframe, filename, sheet='Sheet1'):
    """
    Записывает dataFrame в excel. Можно указывать только имя файла без расширения
    :param dataframe:
    :param filename: fullname of file or only basename ('file'), then writes to dir_excel
    :param sheet:
    :param datetime_format: May be date format, e.g. dd-mm-yyyy,
                    or may be period letter: D, M, Q, Y (day, month, quarter, year)
                    or may be None, then dd-mm-yyyy sets
    :return:
    """
    # datetime_format = 'dd-mm-yyyy'
    if not filename.endswith('.xlsx'):
        filename = os.path.join(DIR_EXCEL, filename + ".xlsx")

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    # writer = pandas.ExcelWriter(filename, engine='xlsxwriter', datetime_format=datetime_format)
    # dateformat = dateformat_from_period(datetime_format)
    writer = pandas.ExcelWriter(filename, datetime_format='dd-mm-yyyy')

    # Convert the dataframe to an XlsxWriter Excel object.
    dataframe.to_excel(writer, sheet_name=sheet)

    # Get the xlsxwriter objects from the dataframe writer object.
    workbook = writer.book
    # worksheet = writer.sheets[sheet] # Так работает
    # worksheet = workbook.active # Так тоже работает

    # worksheet['A1'] = 'A1'

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()


def dataframe_to_html(dataframe, filename):
    if not filename.endswith('.html'):
        filename = os.path.join(DIR_EXCEL, filename + ".html")
    html = dataframe.to_html()
    with open(filename, "w") as text_file:
        text_file.write(html)


def shift_account_name(account_name: str, root_account=None, delimiter=':', filler=' '):
    """
    Для получения сдвинутого вправо имени счета для отображения иерархии счетов
    Возвращает сроку от исходной строки S, заполненную до последнего встреченного символа colon, символами filler

    >>> shift_account_name('assets:current assets:cash', filler='-')
    '--------------------cash'
    >>> shift_account_name('assets:current assets:cash', root_account='assets', filler='-')
    '--------------------cash'
    >>> shift_account_name('assets:current assets:cash', root_account='assets:current assets', filler='-')
    '----------cash'

    :param filler: 
    :return: 
    """

    level = account_name.count(delimiter)
    if root_account:
        skip_level = root_account.count(delimiter)
    else:
        skip_level = 0
    str_fill = filler * 10 * (level - skip_level)
    last_index = account_name.rfind(delimiter)
    # str_fill = filler * last_index
    str_end = account_name[last_index + 1:]
    return str_fill + str_end


def split_by_years(from_date, to_date):
    """
    Splits two dates interval on array of intervals by years

    >>> split_by_years(datetime.datetime(2014,1,2), datetime.datetime(2017, 1, 20))
    [[datetime.datetime(2014, 2, 1, 0, 0), datetime.datetime(2014, 12, 31, 0, 0)], \
[datetime.datetime(2015, 1, 1, 0, 0), datetime.datetime(2015, 12, 31, 0, 0)], \
[datetime.datetime(2016, 1, 1, 0, 0), datetime.datetime(2016, 12, 31, 0, 0)]]

    :param from_date:
    :param to_date:
    :return: Array of tuples date
    """
    dates = []
    from_date, to_date = complete_month(from_date, to_date)
    cur_year = from_date.year
    not_end_cycle = True
    while not_end_cycle:
        first_date = datetime.datetime(cur_year, 1, 1)
        end_date = datetime.datetime(cur_year, 12, 31)
        if first_date < from_date:
            first_date = from_date
        if end_date > to_date:
            end_date = to_date
            # end cycle
            not_end_cycle = False
        if first_date >= end_date:
            break
        dates.append([first_date, end_date])
        cur_year += 1

    return dates

def complete_years_dates (from_date: datetime.datetime, to_date: datetime.datetime):
    """
    Return tuple of first and last date of year from interval, which are full ended year
    >>> complete_years_dates(datetime.datetime(2016,1,2), datetime.datetime(2016,12,30))

    >>> complete_years_dates(datetime.datetime(2008,12,31), datetime.datetime(2017, 2, 15))
    (datetime.datetime(2009, 1, 1, 0, 0), datetime.datetime(2016, 12, 31, 0, 0))

    :param from_date:
    :param to_date:
    :return:
    """
    # Первая дата, выравниваем год
    from_year = from_date.year
    if not (from_date.month == 1 and from_date.day == 1):
        from_year += 1
        # if from_year > date.today().year:
        #     return None

    to_year = to_date.year
    if not (to_date.month == 12 and to_date.day == 31):
        to_year -= 1

    if from_year > to_year:
        return None

    if from_year == to_year:
        return None

    y_start_date = datetime.datetime(from_year, 1, 1)
    y_end_date = datetime.datetime(to_year, 12, 31)

    return y_start_date, y_end_date


def complete_years(from_date, to_date):
    """
    Return tuple of first and last year from interval, which are full ended
    >>> complete_years(datetime.datetime(2016,1,2), datetime.datetime(2016,12,30))

    >>> complete_years(datetime.datetime(2008,12,31), datetime.datetime(2017, 2, 15))
    (2009, 2016)

    :param from_date:
    :param to_date:
    :return:
    """
    # Первая дата, выравниваем год
    from_year = from_date.year
    if not (from_date.month == 1 and from_date.day == 1):
        from_year += 1
        if from_year > datetime.datetime.today().year:
            return None

    to_year = to_date.year
    if not (to_date.month == 12 and to_date.day == 31):
        to_year -= 1

    if from_year > to_year:
        return None

    if from_year == to_year:
        return None

    return from_year, to_year


def complete_month(from_date: datetime.datetime, to_date: datetime.datetime):
    """
    Return tuple of two dates, wich contain full months.
    Cut interval to start and end full months

    >>> complete_month(datetime.datetime(2016,1,2), datetime.datetime(2016,12,30))
    (datetime.datetime(2016, 2, 1, 0, 0), datetime.datetime(2016, 11, 30, 0, 0))
    >>> complete_month(datetime.datetime(2008,12,31), datetime.datetime(2017, 2, 15))
    (datetime.datetime(2009, 1, 1, 0, 0), datetime.datetime(2017, 1, 31, 0, 0))
    >>> complete_month(datetime.datetime(2008,12,31), datetime.datetime(2017, 1, 15))
    (datetime.datetime(2009, 1, 1, 0, 0), datetime.datetime(2016, 12, 31, 0, 0))

    :param from_date:
    :param to_date:
    :return:
    """
    # Первая дата, выравниваем на месяц
    new_from_date = from_date
    first_day = from_date.day
    if first_day != 1:
        new_from_date = add_months(from_date, 1)
        new_from_date = new_from_date.replace(day=1)

    # Вторая дата выравниваем на месяц
    new_to_date = to_date
    _, days_in_month = calendar.monthrange(to_date.year, to_date.month)
    if to_date.day != days_in_month:
        new_to_date = add_months(to_date, -1)
        _, new_days_in_month = calendar.monthrange(new_to_date.year, new_to_date.month)
        new_to_date = new_to_date.replace(day=new_days_in_month)

    return new_from_date, new_to_date


def add_months(sourcedate: datetime.datetime, months):
    """
    Add months to date

    >>> add_months(datetime.datetime(2016,1,2), 1)
    datetime.datetime(2016, 2, 2, 0, 0)
    >>> add_months(datetime.datetime(2016,12,31), 1)
    datetime.datetime(2017, 1, 31, 0, 0)
    >>> add_months(datetime.datetime(2017,2,28), 1)
    datetime.datetime(2017, 3, 28, 0, 0)
    >>> add_months(datetime.datetime(2017,2,28), -1)
    datetime.datetime(2017, 1, 28, 0, 0)
    >>> add_months(datetime.datetime(2017,1,1), -1)
    datetime.datetime(2016, 12, 1, 0, 0)

    :param months:
    :return: datetime.date = sourcedate + months
    """

    month = sourcedate.month - 1 + months

    year = int(sourcedate.year + month / 12)

    month = month % 12 + 1

    day = min(sourcedate.day, calendar.monthrange(year, month)[1])

    return datetime.datetime(year, month, day)

# def dateformat_from_period(period: str):
#     """
#     Get Excel date format from period letter (D, M, Y ...)
#     :param period: May be date format, e.g. dd-mm-yyyy,
#                     or may be period letter: D, M, Q, Y (day, month, quarter, year)
#                     or may be None, then dd-mm-yyyy returns
#     :return: datetime_format for excel
#     """
#
#     if period:
#         dateformat = period
#     else:
#         dateformat = 'dd-mm-yyyy'
#
#     if period:
#         if period.upper() == 'D':
#             dateformat = 'dd-mm-yyyy'
#         if period.upper() == 'M':
#             dateformat = 'mmm yyyy'
#         if period.upper() == 'A':
#             dateformat = 'yyyy'
#         if period.upper() == 'Q':
#             dateformat = 'Q YY'  # ???
#     return dateformat


def parse_string_to_dict(string: str, parse_to_decimal=False):
    """
    Получает из строки вида 'CS ID=123 HD=CT NE=HI THERE' 
    значения словаря
    Возвращает словарь
    >>> entries = parse_string_to_dict('CS ID=123 HD=CT NE=HI THERE')
    >>> entries['ID']
    '123'
    >>> entries['NE']
    'HI THERE'
    >>> parse_string_to_dict('0.1')
    {}
    >>> entries = parse_string_to_dict('ID=12.3')
    >>> entries['ID']
    '12.3'
    >>> entries = parse_string_to_dict('ID=12.3', parse_to_decimal=True)
    >>> entries['ID']
    Decimal('12.3')
    
    todate=01-01-2017 total=-0.0242 expense=0.0242
    
    :param string: 
    :return: dictionary
    """

    # Без кавычек:
    # x = '''CS ID=123 HD=CT NE="HI THERE"'''
    # >> > re.findall("""\w+="[^"]*"|\w+='[^']*'|\w+=\w+|\w+""", x)
    # ['CS', 'ID=123', 'HD=CT', 'NE="HI THERE"']

    # array_strings = list(map(''.join, re.findall("""(\w+=)"([^"]*)"|(\w+=)'([^']*)'|(\w+=\w+)""", string)))
    # dict1 = dict(map(lambda x1: (x1.split('=')[0], decimal_from_string(x1.split('=')[1]) if parse_to_decimal else x1.split('=')[1]), array_strings))
    # if parse_to_decimal:
    #     pass

    pat = re.compile(r'''([^\s=]+)=\s*((?:[^\s=]+(?:\s|$))*)''')
    c = pat.findall(string)
    if parse_to_decimal:
        entries = dict((k, decimal_from_string(v.strip())) for k, v in c)
    else:
        entries = dict((k, v.strip()) for k, v in c)
    # print(entries)
    # print(entries['ID'])

    return entries


def decimal_from_string(str_decimal:str):
    """
    Parse string to decimal
    
    >>> decimal_from_string('0.1')
    Decimal('0.1')
    
    >>> decimal_from_string('0,1')
    Decimal('0.1')
    
    :param str_decimal: 
    :return: 
    """
    # if str_decimal and str_decimal != '':
    dec = Decimal(str_decimal.replace(',', '.'))
    # else:
    #     dec = Decimal(0)
    return dec
