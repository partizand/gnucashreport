import os

import pandas
import re

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


def parse_string_to_dict(string: str):
    """
    Получает из строки вида 'CS ID=123 HD=CT NE=HI THERE' 
    значения словаря
    Возвращает словарь
    >>> x = 'CS ID=123 HD=CT NE="HI THERE"'
    >>> entries = parse_string_to_dict(x)
    >>> entries['ID']
    '123'
    >>> entries['NE']
    'HI THERE'
    >>> x = '0.1'
    >>> entries = parse_string_to_dict(x)
    >>> entries
    {}
    
    :param string: 
    :return: dictionary
    """

    # Без кавычек:
    # x = '''CS ID=123 HD=CT NE="HI THERE"'''
    # >> > re.findall("""\w+="[^"]*"|\w+='[^']*'|\w+=\w+|\w+""", x)
    # ['CS', 'ID=123', 'HD=CT', 'NE="HI THERE"']

    array_strings = list(map(''.join, re.findall("""(\w+=)"([^"]*)"|(\w+=)'([^']*)'|(\w+=\w+)""", string)))
    dict1 = dict(map(lambda x1: x1.split('='), array_strings))

    return dict1
