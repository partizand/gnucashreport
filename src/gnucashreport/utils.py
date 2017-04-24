import os

import pandas
import re

from decimal import Decimal

DIR_EXCEL = "v:/tables"


def dataframe_to_excel(dataframe, filename, sheet='Sheet1', datetime_format='dd-mm-yyyy'):
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
    if not filename.endswith('.xlsx'):
        filename = os.path.join(DIR_EXCEL, filename + ".xlsx")

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    # writer = pandas.ExcelWriter(filename, engine='xlsxwriter', datetime_format=datetime_format)
    dateformat = dateformat_from_period(datetime_format)
    writer = pandas.ExcelWriter(filename, datetime_format=dateformat)

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


def dateformat_from_period(period: str):
    """
    Get Excel date format from period letter (D, M, Y ...)
    :param period: May be date format, e.g. dd-mm-yyyy,
                    or may be period letter: D, M, Q, Y (day, month, quarter, year)
                    or may be None, then dd-mm-yyyy returns
    :return: datetime_format for excel
    """

    if period:
        dateformat = period
    else:
        dateformat = 'dd-mm-yyyy'

    if period:
        if period.upper() == 'M':
            dateformat = 'mmm yyyy'
        if period.upper() == 'A':
            dateformat = 'yyyy'
        if period.upper() == 'Q':
            dateformat = 'Q YY'  # ???
    return dateformat


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
    dec = Decimal(str_decimal.replace(',', '.'))
    return dec
