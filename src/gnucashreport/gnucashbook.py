import datetime
import decimal
import gzip

import os
import pandas

from dateutil.parser import parse as parse_date
from dateutil import tz
from xml.etree import ElementTree

import gnucashreport.cols as cols

# Признак, что счет не участвует в расчете доходности
MARKER_NO_INVEST = '%no_invest%'
# Признак, что счет участвует в расчете доходности
MARKER_INVEST = '%invest%'

class GNUCashBook:
    """
    Read GnuCash book tables into pandas dataframes
    df_accounts
    df_splits
    etc
    """

    #__metaclass__ = abc.ABCMeta

    # book types
    # BOOKTYPE_XML = 'xml'
    # BOOKTYPE_SQLITE = 'sqlite'

    # _DIR_PICKLE = 'V:/test_data'



    # GnuCash account types
    CASH = 'CASH'
    BANK = 'BANK'
    ASSET = 'ASSET'
    STOCK = 'STOCK'
    MUTUAL = 'MUTUAL'
    INCOME = 'INCOME'
    EXPENSE = 'EXPENSE'
    EQUITY = 'EQUITY'
    LIABILITY = 'LIABILITY'
    ROOT = 'ROOT'
    # GNUCash all account assets types
    ALL_ASSET_TYPES = [CASH, BANK, ASSET, STOCK, MUTUAL]

    # All account types for calc yield by xirr
    ALL_XIRR_TYPES = [BANK, ASSET, STOCK, MUTUAL, LIABILITY]
    ASSET_XIRR_TYPES = [BANK, ASSET, LIABILITY]
    STOCK_XIRR_TYPES = [STOCK, MUTUAL]
    INCEXP_XIRR_TYPES = [INCOME, EXPENSE]

    def __init__(self, filename=None):

        # self.book = None

        # for debbuging
        self._PICKLE_PRICES = 'prices.pkl'
        self._PICKLE_SPLITS = 'splits.pkl'
        self._PICKLE_ACCOUNTS = 'accounts.pkl'
        self._PICKLE_TR = 'transactions.pkl'
        self._PICKLE_COMMODITIES = 'commodities.pkl'

        self.df_accounts = pandas.DataFrame()
        self.df_transactions = pandas.DataFrame()
        self.df_commodities = pandas.DataFrame()
        self.df_splits = pandas.DataFrame()
        self.df_prices = pandas.DataFrame()

        # self.book_name = None
        self._book_type = None
        self._book_filename = None

        self.root_account_guid = None
        self._splits = []

        if filename:
            self.open_file(filename)

        # self._startTime = None

    def open_file(self, filename):
        # Get abs filename
        # if os.path.isabs(filename):
        #     fullfilename = filename
        # else:
        #     base_path = os.path.dirname(os.path.realpath(__file__))
        #     fullfilename = os.path.join(base_path, filename)
        fullfilename = filename

        if os.path.isdir(fullfilename):
            self._open_pickle(folder=fullfilename)
            self._book_type = 'pickle'
        else:
            with open(fullfilename, "rb") as f:
                bytes = f.read(16)
            if bytes == b'SQLite format 3\x00':
                self._open_sqlite(fullfilename)
                self._book_type = 'sql'
            else:
                self._open_xml(fullfilename)
                self._book_type = 'xml'

            #  Get fullname of accounts
            self.df_accounts[cols.FULLNAME] = self.df_accounts.index.map(self._get_fullname_account)
            # Add xirr enable column
            self.df_accounts[cols.XIRR_ENABLE] = self.df_accounts.index.map(self._get_xirr_enable)

            self._after_open()



        self._get_guid_rootaccount()


        self._book_filename = os.path.basename(filename)

    def _after_open(self):

        # Add commodity mnemonic to accounts
        mems = self.df_commodities[cols.MNEMONIC].to_frame()
        # А после этой не пропадает
        self.df_accounts = self.df_accounts.merge(mems, how='left', left_on=cols.COMMODITY_GUID, right_index=True)

        # Convert datetme to date in transactions (skip time)
        self.df_transactions[cols.POST_DATE] = self.df_transactions[cols.POST_DATE].apply(
            lambda x: pandas.to_datetime(x.date()))

        # Merge prices with commodities
        self.df_prices = pandas.merge(self.df_prices, self.df_commodities, left_on=cols.COMMODITY_GUID,
                                      right_index=True)
        # Convert datetme to date in prices (skip time)
        self.df_prices['date'] = self.df_prices['date'].apply(lambda x: pandas.to_datetime(x.date()))

        # merge splits and accounts
        df_acc_splits = pandas.merge(self.df_splits, self.df_accounts, left_on=cols.ACCOUNT_GUID,
                                     right_index=True)
        df_acc_splits.rename(columns={'description': 'description_account'}, inplace=True)
        # merge splits and accounts with transactions
        self.df_splits = pandas.merge(df_acc_splits, self.df_transactions, left_on=cols.TRANSACTION_GUID,
                                      right_index=True)

        # Оставляем только одну цену за день в df_prices
        # Установка нового индекса
        self.df_prices.set_index([cols.COMMODITY_GUID, 'date'], inplace=True)
        # отсечение повторов по индексу
        self.df_prices = self.df_prices[~self.df_prices.index.duplicated(keep='last')]

        # Минимальная и максимальная даты в базе
        self.min_date = self.df_splits[cols.POST_DATE].min().date()
        self.max_date = self.df_splits[cols.POST_DATE].max().date()

        # Подсчитываем нарастающий итог
        self.df_splits.sort_values(by=cols.POST_DATE, inplace=True)
        self.df_splits[cols.CUM_SUM] = self.df_splits.groupby(cols.FULLNAME)[cols.QUANTITY].transform(
            pandas.Series.cumsum)

    def __repr__(self):
        return 'book {book_type} <{filename}>'.format(book_type=self._book_type, filename=self._book_filename)

    def _get_xirr_enable(self, account_guid):
        """
        Returns True for account with xirr calculate, and False for account without xirr
        :param account_guid:
        :return: Boolean True for xirr account, False - for account without xirr
        """

        # account is ROOT, then False
        if self._is_root_account(account_guid):
            return False

        # CASH and EQUITY always False
        account_type = self.df_accounts.loc[account_guid, cols.ACCOUNT_TYPE]
        if (account_type == GNUCashBook.CASH) or (account_type == GNUCashBook.EQUITY):
            return False

        # account notes contain MARKER, then marker value
        notes = self.df_accounts.loc[account_guid, cols.NOTES]
        if notes:
            if MARKER_NO_INVEST in notes:
                return False
            if MARKER_INVEST in notes:
                return True

        # account immediately after the root, no markers, then depending on the type account
        # INCOME, EXPENSE - False
        # others - True (except CASH and EQUITY)
        parent_guid = self.df_accounts.loc[account_guid, cols.PARENT_GUID]
        if self._is_root_account(parent_guid):
            account_type = self.df_accounts.loc[account_guid, cols.ACCOUNT_TYPE]
            if (account_type == GNUCashBook.CASH) or (account_type == GNUCashBook.EQUITY) or \
                    (account_type == GNUCashBook.INCOME) or (account_type == GNUCashBook.EXPENSE):
                return False
            else:
                return True

        # other cases, the value of the parent account
        return self._get_xirr_enable(parent_guid)

    def _is_root_account(self, account_guid):
        """
        Returns True if account is ROOT, False - not ROOT
        :param account_guid:
        :return:
        """
        account_type = self.df_accounts.loc[account_guid][cols.ACCOUNT_TYPE]
        if account_type == self.ROOT:
            return True
        else:
            return False

    def _get_fullname_account(self, account_guid):
        """
        Get fullname account by guid. Return semicolon path Expenses:Food:...
        :param account_guid:
        :return:
        """
        if self._is_root_account(account_guid):
            return 'root'
        fullname = self.df_accounts.loc[account_guid][cols.SHORTNAME]
        parent_guid = self.df_accounts.loc[account_guid][cols.PARENT_GUID]

        if parent_guid in self.df_accounts.index:
            if self._is_root_account(parent_guid):
                return fullname
            else:
                return self._get_fullname_account(parent_guid) + ':' + fullname
        else:
            return 'error'

    def _open_pickle(self, folder):
        """
        For testing
        :param folder:
        :return:
        """
        self.df_accounts = self._dataframe_from_pickle(self._PICKLE_ACCOUNTS, folder=folder)
        # dataframe_to_excel(self.df_accounts, 'accounts-source')
        self.df_commodities = self._dataframe_from_pickle(self._PICKLE_COMMODITIES, folder=folder)
        self.df_prices = self._dataframe_from_pickle(self._PICKLE_PRICES, folder=folder)
        self.df_transactions = self._dataframe_from_pickle(self._PICKLE_TR, folder=folder)
        self.df_splits = self._dataframe_from_pickle(self._PICKLE_SPLITS, folder=folder)
        # self._get_guid_rootaccount()

    def _dataframe_from_pickle(self, filename, folder):
        """
        Get dataframe from pickle file
        :param filename: Полное или короткое имя файла
        :param folder: Каталог с файлом
        :return: DataFrame
        """

        fullfilename = os.path.join(folder, filename)
        df = pandas.read_pickle(fullfilename)
        return df

    def _open_sqlite(self, filename):

        # Open sqlite base
        uri = 'sqlite:///{}'.format(filename)
        # Read tables

        # commodities
        self.df_commodities = pandas.read_sql_table('commodities', uri)
        # set index
        self.df_commodities.set_index(cols.GUID, inplace=True)

        self.df_prices = pandas.read_sql_table('prices', uri)
        #self.df_prices[cols.VALUE] = (self.df_prices['value_num'] / self.df_prices['value_denom']).astype(Decimal, copy=False)
        self.df_prices[cols.VALUE] = self.df_prices.apply(lambda row: ((decimal.Decimal(row['value_num']) / decimal.Decimal(row['value_denom']))),
                                                          axis=1)
        self.df_prices.set_index(cols.GUID, inplace=True)
        # Convert sqlite date strings to date
        # date stores in UTC on start day of local tz!.
        # if my tz = UTC+3 and date in price i set 2017-12-31, then in table stores 2017-12-30 21-00 - it is begin my date in UTC
        # I think it is bug (in xml stores all ok, it will be 2017-12-31 10-59)
        # And in transactions dates stores right - 2017-12-31 10-59
        # Only in sqlite and price date column has this bug (GnuCash 2.6.18)

        # new_date = date + offset

        dt = datetime.datetime.now()
        tzinfo = tz.tzlocal()
        offset = tzinfo.utcoffset(dt)
        # new_dt = dt + a

        self.df_prices['date'] = self.df_prices['date'].apply(lambda x: (parse_date(x) + offset ))
        # self.df_prices['date'] = pandas.to_datetime(self.df_prices['date'])

        # Transactions
        self.df_transactions = pandas.read_sql_table('transactions', uri)
        # Convert sqlite date strings to date
        self.df_transactions[cols.POST_DATE] = pandas.to_datetime(self.df_transactions[cols.POST_DATE])
        self.df_transactions[cols.ENTER_DATE] = pandas.to_datetime(self.df_transactions[cols.ENTER_DATE])
        # set index
        self.df_transactions.set_index(cols.GUID, inplace=True)


        self.df_splits = pandas.read_sql_table('splits', uri)
        #self.df_splits[cols.VALUE] = (self.df_splits['value_num'] / self.df_splits['value_denom']).astype(Decimal, copy=False)
        self.df_splits[cols.VALUE] = self.df_splits.apply(lambda row: ((decimal.Decimal(row['value_num']) / decimal.Decimal(row['value_denom']))), axis=1)

        #self.df_splits[cols.QUANTITY] = (self.df_splits['quantity_num'] / self.df_splits['quantity_denom']).astype(Decimal, copy=False)
        self.df_splits[cols.QUANTITY] = self.df_splits.apply(lambda row: ((decimal.Decimal(row['quantity_num']) / decimal.Decimal(row['quantity_denom']))),
                                                          axis=1)
        # rename column to standard name
        self.df_splits.rename(columns={'tx_guid': cols.TRANSACTION_GUID}, inplace=True)
        self.df_splits.set_index(cols.GUID, inplace=True)

        # Read accounts notes from slots
        sql_text = """
            select
                accounts.*,
                slot_notes.string_val as notes
            from accounts
                left join (select obj_guid, name, string_val from slots where slots.name = 'notes') as slot_notes
                    on accounts.guid = slot_notes.obj_guid
            """
        self.df_accounts = pandas.read_sql(sql_text, uri)
        # set index
        self.df_accounts.set_index(cols.GUID, inplace=True)

        # self._get_guid_rootaccount()

    def _get_guid_rootaccount(self):
        """
        Get root account guid from df_accounts
        :return:
        """
        df_root = self.df_accounts[(self.df_accounts[cols.ACCOUNT_TYPE] == self.ROOT) &
                                   (self.df_accounts[cols.SHORTNAME] == 'Root Account')]
        self.root_account_guid = df_root.index.values[0]

    #====================================================================
    #  XML Book

    @staticmethod
    def _get_commodity_guid(space, name):
        return space + ":" + name

    @staticmethod
    def _parse_number(numstring):
        num, denum = numstring.split("/")
        return decimal.Decimal(num) / decimal.Decimal(denum)

    def _open_xml(self, filename):
        """
        Read a GNU Cash xml file into DataFrames objects

        :param filename:
        :return:
        """

        # self._start_timing('Start book reading')
        try:

            # try opening with gzip decompression
            self._parse_xml(gzip.open(filename, "rb"))
        except IOError:
            # try opening without decompression
            # f = open(filename, "rb")
            # self.parse(f)
            self._parse_xml(filename)

    def _parse_xml(self, fobj):
        """Parse GNU Cash XML data from a file object into pandas DataFrame objects"""

        root_tree = ElementTree.parse(fobj)

        root = root_tree.getroot()
        if root.tag != 'gnc-v2':
            raise ValueError("File stream was not a valid GNU Cash v2 XML file")
        tree = root.find("{http://www.gnucash.org/XML/gnc}book")
        # self._book_from_tree(root.find("{http://www.gnucash.org/XML/gnc}book"))
        array = []
        for child in tree.findall('{http://www.gnucash.org/XML/gnc}commodity'):
            # comm = self._commodity_from_tree(child)
            # self._commodity_from_tree(child)
            line = self._commodity_from_tree(child)
            if line:
                array.append(line)
        self.df_commodities = pandas.DataFrame(array)
        self.df_commodities.set_index(cols.GUID, inplace=True)

        array = []
        for child in tree.findall('{http://www.gnucash.org/XML/gnc}pricedb/price'):
            # price = self._price_from_tree(child)
            line = self._price_from_tree(child)
            if line:
                array.append(line)
        self.df_prices = pandas.DataFrame(array)
        self.df_prices.set_index(cols.GUID, inplace=True)

        array = []
        for child in tree.findall('{http://www.gnucash.org/XML/gnc}account'):
            line = self._account_from_tree(child)
            if line:
                array.append(line)
        self.df_accounts = pandas.DataFrame(array)
        self.df_accounts.set_index(cols.GUID, inplace=True)

        trans = []
        for child in tree.findall('{http://www.gnucash.org/XML/gnc}'
                                  'transaction'):
            line = self._transaction_from_tree(child)
            if line:
                trans.append(line)
        self.df_transactions = pandas.DataFrame(trans)
        self.df_transactions.set_index(cols.GUID, inplace=True)

        self.df_splits = pandas.DataFrame(self._splits)
        self.df_splits.set_index(cols.GUID, inplace=True)

    def _commodity_from_tree(self, tree):

        namespace = tree.find('{http://www.gnucash.org/XML/cmdty}space').text

        if namespace.lower() != 'template':
            mnemonic = tree.find('{http://www.gnucash.org/XML/cmdty}id').text
            guid = self._get_commodity_guid(space=namespace, name=mnemonic)
            comm = {cols.GUID: guid, cols.NAMESPACE: namespace, cols.MNEMONIC: mnemonic}
            # comm_obj = self.Commodity(guid=guid, mnemonic=mnemonic, namespace=namespace)
            # self.commodities.append(comm_obj)
            # self.df_commodities = self.df_commodities.append(comm, ignore_index=True)
            return comm

    def _price_from_tree(self, tree):
        pr = '{http://www.gnucash.org/XML/price}'
        cmdty = '{http://www.gnucash.org/XML/cmdty}'
        ts = '{http://www.gnucash.org/XML/ts}'

        # price = {}

        guid = tree.find(pr + "id").text
        source = tree.find(pr + "source").text
        tree_type = tree.find(pr + "type")
        if tree_type:
            price_type = tree_type.text
        else:
            price_type = None
        value = self._parse_number(tree.find(pr + "value").text)

        currency_space = tree.find(pr + "currency/" + cmdty + "space").text
        currency_name = tree.find(pr + "currency/" + cmdty + "id").text
        currency_guid = self._get_commodity_guid(space=currency_space, name=currency_name)

        commodity_space = tree.find(pr + "commodity/" + cmdty + "space").text
        commodity_name = tree.find(pr + "commodity/" + cmdty + "id").text
        commodity_guid = self._get_commodity_guid(space=commodity_space, name=commodity_name)

        # xml_date = tree.find(pr + "time/" + ts + "date").text

        date = parse_date(tree.find(pr + "time/" + ts + "date").text,)

        # price["date"] = pandas.to_datetime(tree.find(pr + "time/" + ts + "date").text)
        # pd_date = pandas.to_datetime(pd_date.date())

        # price_obj = self.Price(guid=guid,
        #                    commodity_guid=commodity_guid,
        #                    currency_guid=currency_guid,
        #                    date=date,
        #                    source=source,
        #                    price_type=price_type,
        #                    value=value)

        price = {cols.GUID: guid,
                 cols.COMMODITY_GUID: commodity_guid,
                 cols.CURRENCY_GUID: currency_guid,
                 'date': date,
                 'source': source,
                 'type': price_type,
                 cols.VALUE: value
                 }
        # self.prices.append(price_obj)
        # self.df_prices =  self.df_prices.append(price, ignore_index=True)

        return price

    # Implemented:
    # - act:name
    # - act:id
    # - act:type
    # - act:description
    # - act:commodity
    # - act:commodity-scu
    # - act:parent
    # - act:slots
    def _account_from_tree(self, tree):
        act = '{http://www.gnucash.org/XML/act}'
        cmdty = '{http://www.gnucash.org/XML/cmdty}'
        # account = {}
        name = tree.find(act + 'name').text
        guid = tree.find(act + 'id').text
        account_type = tree.find(act + 'type').text
        # account[cols.ACCOUNT_TYPE] = account_type
        descr = tree.find(act + "description")
        if descr is not None:
            description = descr.text
        else:
            description = ''

        slots = self._slots_from_tree(tree.find(act + 'slots'))

        if 'hidden' in slots.keys():
            hid = slots['hidden']
            if hid.lower() == 'true':
                hidden = True
            else:
                hidden = False
        else:
            hidden = False

        if 'notes' in slots.keys():
            notes = slots['notes']
        else:
            notes = None

        # hidden = slots['hidden']
        # {'reconcile-info': {'include-children': 0, 'last-date': 1324151999, 'last-interval': {'days': 7, 'months': 0}},
        #  'color': 'Not Set', 'hidden': 'true', 'placeholder': 'true'}
        if account_type == 'ROOT':
            parent_guid = None
            commodity = None
            commodity_scu = None
            commodity_guid = None
            self.root_account_guid = guid
        else:
            parent_guid = tree.find(act + 'parent').text
            commodity_space = tree.find(act + 'commodity/' + cmdty + 'space').text
            commodity_name = tree.find(act + 'commodity/' + cmdty + 'id').text
            commodity_guid = self._get_commodity_guid(space=commodity_space, name=commodity_name)
            commodity_scu = tree.find(act + 'commodity-scu').text

        account = {cols.GUID: guid,
                   cols.SHORTNAME: name,
                   cols.DESCRIPTION: description,
                   cols.ACCOUNT_TYPE: account_type,
                   'hidden': hidden,
                   cols.COMMODITY_GUID: commodity_guid,
                   'commodity_scu': commodity_scu,
                   cols.PARENT_GUID: parent_guid,
                   'notes': notes
                   }

        return account

    def _transaction_from_tree(self, tree):
        trn = '{http://www.gnucash.org/XML/trn}'
        cmdty = '{http://www.gnucash.org/XML/cmdty}'
        ts = '{http://www.gnucash.org/XML/ts}'
        # split = '{http://www.gnucash.org/XML/split}'
        # transaction = {}

        guid = tree.find(trn + "id").text
        # transaction[cols.GUID] = guid
        currency_space = tree.find(trn + "currency/" + cmdty + "space").text
        currency_name = tree.find(trn + "currency/" + cmdty + "id").text
        currency_guid = self._get_commodity_guid(space=currency_space, name=currency_name)

        # currency = commoditydict[(currency_space, currency_name)]
        # xml_date = tree.find(trn + "date-posted/" + ts + "date").text
        post_date = parse_date(tree.find(trn + "date-posted/" + ts + "date").text)

        date_entered = parse_date(tree.find(trn + "date-entered/" + ts + "date").text)
        description = tree.find(trn + "description").text
        # transaction_obj = self.Transaction(guid=guid,
        #                           currency_guid=currency_guid,
        #                           post_date=post_date,
        #                           date_entered=date_entered,
        #                           description=description)
        transaction = {cols.GUID: guid,
                       cols.CURRENCY_GUID: currency_guid,
                       cols.POST_DATE: post_date,
                       cols.DESCRIPTION: description,
                       }
        # self.transactions.append(transaction_obj)
        # self.df_transactions = self.df_transactions.append(transaction, ignore_index=True)

        for subtree in tree.findall(trn + "splits/" + trn + "split"):
            split = self._split_from_tree(tree=subtree, transaction_guid=guid)
            # self._split_from_tree(tree=subtree, transaction_guid=guid)
            if split:
                self._splits.append(split)
            # transaction.splits.append(split)

        return transaction

    def _split_from_tree(self, tree, transaction_guid):
        splt_path = '{http://www.gnucash.org/XML/split}'
        ts = "{http://www.gnucash.org/XML/ts}"
        # split = {}
        # split[cols.TRANSACTION_GUID] = transaction_guid
        guid = tree.find(splt_path + "id").text  # guid
        memo = tree.find(splt_path + "memo")
        if memo is not None:
            memo_text = memo.text
        else:
            memo_text = ''

        reconciled_state = tree.find(splt_path + "reconciled-state").text
        # Not used
        # reconcile_date = tree.find(split + "reconcile-date/" + ts + "date")
        # if reconcile_date is not None:
        #     reconcile_date = parse_date(reconcile_date.text)

        value = self._parse_number(tree.find(splt_path + "value").text)
        quantity = self._parse_number(tree.find(splt_path + "quantity").text)
        account_guid = tree.find(splt_path + "account").text
        split = {cols.GUID: guid,
                 cols.TRANSACTION_GUID: transaction_guid,
                 'memo': memo_text,
                 "reconcile_state": reconciled_state,
                 cols.VALUE: value,
                 cols.QUANTITY: quantity,
                 cols.ACCOUNT_GUID: account_guid,
                 }
        # split_obj = self.Split(guid=guid,
        #               memo=memo_text,
        #               reconcile_state=reconciled_state,
        #               # reconcile_date=reconcile_date,
        #               value=value,
        #               quantity=quantity,
        #               account_guid=account_guid,
        #               transaction_guid=transaction_guid
        #               )
        # self.splits.append(split_obj)

        # self.df_splits = self.df_splits.append(split, ignore_index=True)

        return split

    def _slots_from_tree(self, tree):
        if tree is None:
            return {}
        slot = "{http://www.gnucash.org/XML/slot}"
        ts = "{http://www.gnucash.org/XML/ts}"
        slots = {}
        for elt in tree.findall("slot"):
            key = elt.find(slot + "key").text
            value = elt.find(slot + "value")
            type_ = value.get('type', 'string')
            if type_ == 'integer':
                slots[key] = int(value.text)
            elif type_ == 'numeric':
                slots[key] = self._parse_number(value.text)
            elif type_ in ('string', 'guid'):
                slots[key] = value.text
            elif type_ == 'gdate':
                slots[key] = parse_date(value.find("gdate").text)
            elif type_ == 'timespec':
                slots[key] = parse_date(value.find(ts + "date").text)
            elif type_ == 'frame':
                slots[key] = self._slots_from_tree(value)
            else:
                raise RuntimeError("Unknown slot type {}".format(type_))
        return slots

    # end XML Book
    #============================













