import decimal
import gzip
import pandas

from operator import attrgetter

from dateutil.parser import parse as parse_date
from xml.etree import ElementTree

from gnucashreport.gnucashbook import GNUCashBook
import gnucashreport.cols as cols


class GNUCashBookXML(GNUCashBook):
    """
    Reads contents of GNUCash xml file into dataframes
    """

    def __init__(self, timeing=False):
        super(GNUCashBookXML, self).__init__(timeing=timeing)
        self.commodities = []
        self.prices = []
        self.accounts = []
        self.transactions = []
        self.splits = []
        self.root_account_guid = None

    @staticmethod
    def get_commodity_guid(space, name):
        return space + ":" + name

    @staticmethod
    def _parse_number(numstring):
        num, denum = numstring.split("/")
        return decimal.Decimal(num) / decimal.Decimal(denum)



    # def _create_df(self, fields):
    #     df = pandas.DataFrame(columns=fields)
    #     # df.set_index(fields[0], inplace=True)
    #     return df

    def _create_dfs(self):
        # Accounts

        fields = [cols.GUID, cols.SHORTNAME, cols.ACCOUNT_TYPE,
                  cols.COMMODITY_GUID, "commodity_scu",
                  cols.PARENT_GUID, cols.DESCRIPTION, cols.HIDDEN, "notes"]
        self.df_accounts = pandas.DataFrame(columns=fields)

        # Transactions

        fields = [cols.GUID, cols.CURRENCY_GUID, cols.POST_DATE, cols.DESCRIPTION]
        self.df_transactions = pandas.DataFrame(columns=fields)

        # Splits
        fields = [cols.GUID, cols.TRANSACTION_GUID, cols.ACCOUNT_GUID,
                  "memo", "reconcile_state", cols.VALUE, cols.QUANTITY]

        self.df_splits = pandas.DataFrame(columns=fields)

        # commodity

        fields = [cols.GUID, cols.MNEMONIC, cols.NAMESPACE]
        self.df_commodities = pandas.DataFrame(columns=fields)

        # Prices
        fields = [cols.GUID, cols.COMMODITY_GUID, cols.CURRENCY_GUID,
                  "date", "source", "type", cols.VALUE]
        self.df_prices = pandas.DataFrame(columns=fields)

    def _set_df_indexes(self):
        self.df_accounts.set_index('guid', inplace=True)
        self.df_transactions.set_index('guid', inplace=True)
        self.df_splits.set_index('guid', inplace=True)
        self.df_commodities.set_index('guid', inplace=True)
        self.df_prices.set_index('guid', inplace=True)

    def _to_dfs(self):

        # Accounts

        fields = [cols.GUID, cols.SHORTNAME, cols.ACCOUNT_TYPE,
                  "commodity_guid", "commodity_scu",
                  "parent_guid", "description", "hidden", "notes"]

        self.df_accounts = self._object_to_dataframe(self.accounts, fields)
        self.root_account_guid = self.root_account_guid

        # Transactions

        fields = [cols.GUID, cols.CURRENCY_GUID, cols.POST_DATE, cols.DESCRIPTION]

        self.df_transactions = self._object_to_dataframe(self.transactions, fields)

        # Splits
        fields = [cols.GUID, cols.TRANSACTION_GUID, cols.ACCOUNT_GUID,
                  "memo", "reconcile_state", cols.VALUE, cols.QUANTITY]

        self.df_splits = self._object_to_dataframe(self.splits, fields)

        # commodity

        fields = [cols.GUID, 'namespace', "mnemonic"]
        self.df_commodities = self._object_to_dataframe(self.commodities, fields)
        self.df_commodities = self.df_commodities[self.df_commodities['namespace'] != 'template']

        # Prices
        fields = [cols.GUID, cols.COMMODITY_GUID, cols.CURRENCY_GUID,
                  "date", "source", "type", cols.VALUE]
        self.df_prices = self._object_to_dataframe(self.prices, fields)

    @staticmethod
    def _object_to_dataframe(pieobject, fields, slot_names=None):
        """
        Преобразовывае объект piecash в DataFrame с заданными полями
        :param pieobject:
        :param fields:
        :return:
        """
        # build dataframe
        # fields_getter = [attrgetter(fld) for fld in fields]
        fields_getter = [(fld, attrgetter(fld)) for fld in fields]

        # array_old = [[fg(sp) for fg in fields_getter] for sp in pieobject]

        # у строки есть массив slots
        # в поле name = notes
        # в поле value = значение


        # Разложение цикла
        array = []
        for sp in pieobject:
            line = {}
            for field in fields:
                line[field] = getattr(sp, field, None)
            # for fld, fg in fields_getter:
            #     line[fld] = fg(sp)
            if slot_names:
                for slot_name in slot_names:
                    line[slot_name] = None
                for slot in sp.slots:
                    if slot.name in slot_names:
                        line[slot.name] = slot.value


            array.append(line)



        # df_obj = pandas.DataFrame([[fg(sp) for fg in fields_getter] for sp in pieobject], columns=fields)
        # df_obj = pandas.DataFrame(array, columns=all_fields)
        if array:
            df_obj = pandas.DataFrame(array)
        else:
            if slot_names:
                all_fields = fields + slot_names
            else:
                all_fields = fields
            df_obj = pandas.DataFrame(columns=all_fields)
        df_obj.set_index(fields[0], inplace=True)
        return df_obj

    def read_book(self, filename):
        """
        Read a GNU Cash xml file

        Parse a GNU Cash file and return a dictionary object.
        :param filename:
        :return:
        """

        # self._start_timing('Start book reading')
        try:

            # try opening with gzip decompression
            self.parse(gzip.open(filename, "rb"))
        except IOError:
            # try opening without decompression
            # f = open(filename, "rb")
            # self.parse(f)
            self.parse(filename)
        # self._end_timing('Book readed')



    # Implemented:
    # - gnc:book
    #
    # Not implemented:
    # - gnc:count-data
    #   - This seems to be primarily for integrity checks?
    def parse(self, fobj):
        """Parse GNU Cash XML data from a file object and return a Book object."""

        tree = ElementTree.parse(fobj)

        root = tree.getroot()
        if root.tag != 'gnc-v2':
            raise ValueError("File stream was not a valid GNU Cash v2 XML file")
        # self._create_dfs()  # Create dataframes with fields
        self._book_from_tree(root.find("{http://www.gnucash.org/XML/gnc}book"))
        self._to_dfs()
        # self._set_df_indexes()
        # self._get_guid_rootaccount()

    # <gnc:pricedb version="1">
    #   <price>
    #     <price:id type="guid">b9f8ca82cfe48ae412cabb76d0d57aa0</price:id>
    #     <price:commodity>
    #       <cmdty:space>Bond</cmdty:space>
    #       <cmdty:id>OFZ25080</cmdty:id>
    #     </price:commodity>
    #     <price:currency>
    #       <cmdty:space>ISO4217</cmdty:space>
    #       <cmdty:id>RUB</cmdty:id>
    #     </price:currency>
    #     <price:time>
    #       <ts:date>2016-11-23 00:00:00 +0300</ts:date>
    #     </price:time>
    #     <price:source>user:price</price:source>
    #     <price:type>transaction</price:type>
    #     <price:value>1001600000/1000000</price:value>
    #   </price>

    # <gnc:commodity version="2.0.0">
    #   <cmdty:space>Bond</cmdty:space>
    #   <cmdty:id>OFZ25080</cmdty:id>
    #   <cmdty:name>ОФЗ ПД 25080 (19.04.2017)</cmdty:name>
    #   <cmdty:fraction>10000</cmdty:fraction>
    #   <cmdty:slots>
    #     <slot>
    #       <slot:key>user_symbol</slot:key>
    #       <slot:value type="string">OFZ25080</slot:value>
    #     </slot>
    #   </cmdty:slots>
    # </gnc:commodity>

    # Implemented:
    # - book:id
    # - book:slots
    # - gnc:commodity
    # - gnc:account
    # - gnc:transaction
    #
    # Not implemented:
    # - gnc:schedxaction
    # - gnc:template-transactions
    # - gnc:count-data
    #   - This seems to be primarily for integrity checks?
    def _book_from_tree(self, tree):
        """
        Parse a GNU Cash xml tree and return a dictionary object.
        Dictionary contains keys:
        commodities, prices, accounts, transactions, splits
        Example:
        ret = _book_from_tree(tree)
        all_accounts = ret['accounts']
        :param tree:
        :return: dictionary
        """
        # book guid
        # guid = tree.find('{http://www.gnucash.org/XML/book}id').text

        # Возвращаемый словарь
        # ret_dict = {}

        # commodities = []
        # commoditydict = {}
        for child in tree.findall('{http://www.gnucash.org/XML/gnc}commodity'):
            # comm = self._commodity_from_tree(child)
            self._commodity_from_tree(child)
            # self.commodities.append(comm)



        # Prices

        # prices = []

        self._start_timing('Reading prices')
        for child in tree.findall('{http://www.gnucash.org/XML/gnc}pricedb/price'):
            # price = self._price_from_tree(child)
            self._price_from_tree(child)
            # self.prices.append(price)
        self._end_timing('read prices')

        self._start_timing()
        for child in tree.findall('{http://www.gnucash.org/XML/gnc}account'):
            self._account_from_tree(child)
            # self.accounts.append(acc)
        self._end_timing('read accounts')

        # ret_dict['accounts'] = accounts

        # transactions = []
        # splits = []
        self._start_timing()
        for child in tree.findall('{http://www.gnucash.org/XML/gnc}'
                                  'transaction'):
            self._transaction_from_tree(child)
            # self.transactions.append(transaction)
        self._end_timing('read transactions')

    # Implemented:
    # - cmdty:id
    # - cmdty:space
    #
    # Not implemented:
    # - cmdty:get_quotes => unknown, empty, optional
    # - cmdty:quote_tz => unknown, empty, optional
    # - cmdty:source => text, optional, e.g. "currency"
    # - cmdty:name => optional, e.g. "template"
    # - cmdty:xcode => optional, e.g. "template"
    # - cmdty:fraction => optional, e.g. "1"
    def _commodity_from_tree(self, tree):

        namespace = tree.find('{http://www.gnucash.org/XML/cmdty}space').text

        if namespace.lower() != 'template':
            mnemonic = tree.find('{http://www.gnucash.org/XML/cmdty}id').text
            guid = self.get_commodity_guid(space=namespace, name=mnemonic)
            # comm = {cols.GUID: guid, cols.NAMESPACE: namespace, cols.MNEMONIC: mnemonic}
            comm_obj = self.Commodity(guid=guid, mnemonic=mnemonic, namespace=namespace)
            self.commodities.append(comm_obj)
            # self.df_commodities = self.df_commodities.append(comm, ignore_index=True)

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
        currency_guid = self.get_commodity_guid(space=currency_space, name=currency_name)

        commodity_space = tree.find(pr + "commodity/" + cmdty + "space").text
        commodity_name = tree.find(pr + "commodity/" + cmdty + "id").text
        commodity_guid = self.get_commodity_guid(space=commodity_space, name=commodity_name)

        # xml_date = tree.find(pr + "time/" + ts + "date").text

        date = parse_date(tree.find(pr + "time/" + ts + "date").text)

        # price["date"] = pandas.to_datetime(tree.find(pr + "time/" + ts + "date").text)
        # pd_date = pandas.to_datetime(pd_date.date())

        price = self.Price(guid=guid,
                           commodity_guid=commodity_guid,
                           currency_guid=currency_guid,
                           date=date,
                           source=source,
                           price_type=price_type,
                           value=value)
        self.prices.append(price)
        # self.df_prices =  self.df_prices.append(price, ignore_index=True)

        # return price

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
            description = None

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
            commodity_guid = self.get_commodity_guid(space=commodity_space, name=commodity_name)
            commodity_scu = tree.find(act + 'commodity-scu').text



        account = self.Account(name=name,
                          description=description,
                          guid=guid,
                          account_type=account_type,
                          hidden=hidden,
                          commodity_guid=commodity_guid,
                          commodity_scu=commodity_scu,
                          parent_guid=parent_guid,
                          notes=notes)

        self.accounts.append(account)
        # self.df_accounts = self.df_accounts.append(account, ignore_index=True)

        # return account

    # Implemented:
    # - trn:id
    # - trn:currency
    # - trn:date-posted
    # - trn:date-entered
    # - trn:description
    # - trn:splits / trn:split
    # - trn:slots

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
        currency_guid = self.get_commodity_guid(space=currency_space, name=currency_name)

        # currency = commoditydict[(currency_space, currency_name)]
        xml_date = tree.find(trn + "date-posted/" + ts + "date").text
        post_date = parse_date(xml_date)

        date_entered = parse_date(tree.find(trn + "date-entered/" + ts + "date").text)
        description = tree.find(trn + "description").text
        # slots = self._slots_from_tree(tree.find(trn + "slots"))
        transaction_obj = self.Transaction(guid=guid,
                                  currency_guid=currency_guid,
                                  post_date=post_date,
                                  date_entered=date_entered,
                                  description=description)
        # transaction = {cols.GUID: guid,
        #                cols.CURRENCY_GUID: currency_guid,
        #                cols.POST_DATE: pandas.to_datetime(xml_date),
        #                cols.DESCRIPTION: description,
        #                }
        self.transactions.append(transaction_obj)
        # self.df_transactions = self.df_transactions.append(transaction, ignore_index=True)

        for subtree in tree.findall(trn + "splits/" + trn + "split"):
            self._split_from_tree(tree=subtree, transaction_guid=guid)
            # self.splits.append(split)
            # transaction.splits.append(split)

        # return transaction



    # Implemented:
    # - split:id
    # - split:memo
    # - split:reconciled-state
    # - split:reconcile-date
    # - split:value
    # - split:quantity
    # - split:account
    # - split:slots
    def _split_from_tree(self, tree, transaction_guid):
        splt_path = '{http://www.gnucash.org/XML/split}'
        ts = "{http://www.gnucash.org/XML/ts}"
        # split = {}
        # split[cols.TRANSACTION_GUID] = transaction_guid
        guid = tree.find(splt_path + "id").text # guid
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
        # slots = self._slots_from_tree(tree.find(split + "slots"))
        # split = {cols.GUID: guid,
        #          cols.TRANSACTION_GUID: transaction_guid,
        #          'memo': memo_text,
        #          "reconcile_state": reconciled_state,
        #          cols.VALUE: value,
        #          cols.QUANTITY: quantity,
        #          cols.ACCOUNT_GUID: account_guid,
        #          }
        split_obj = self.Split(guid=guid,
                      memo=memo,
                      reconcile_state=reconciled_state,
                      # reconcile_date=reconcile_date,
                      value=value,
                      quantity=quantity,
                      account_guid=account_guid,
                      transaction_guid=transaction_guid
                      )
        self.splits.append(split_obj)

        # self.df_splits = self.df_splits.append(split, ignore_index=True)


        # return split

    # Implemented:
    # - slot
    # - slot:key
    # - slot:value
    # - ts:date
    # - gdate
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

    # @staticmethod
    # def _parse_number(numstring):
    #     num, denum = numstring.split("/")
    #     return decimal.Decimal(num) / decimal.Decimal(denum)


    class Commodity(object):
        """
        A commodity is something that's stored in GNU Cash accounts.

        Consists of a name (or id) and a space (namespace).
        """

        def __init__(self, guid, mnemonic, namespace):
            self.guid = guid
            self.mnemonic = mnemonic
            # self.name = name
            self.namespace = namespace



        def __str__(self):
            return self.mnemonic

        def __repr__(self):
            return "<Commodity {}>".format(self.guid)


    class Price(object):
        """
        A commodity is something that's stored in GNU Cash accounts.

        Consists of a name (or id) and a space (namespace).
        """

        def __init__(self, guid, commodity_guid, currency_guid, date, source, price_type, value):
            self.guid = guid
            self.commodity_guid = commodity_guid
            self.currency_guid = currency_guid
            self.date = date
            self.source = source
            self.type = price_type
            self.value = value

        def __str__(self):
            return self.guid

        def __repr__(self):
            return "<Price {}>".format(self.guid)


    class Account(object):
        """
        An account is part of a tree structure of accounts and contains splits.
        """

        def __init__(self, name, guid, account_type, hidden, parent_guid=None,
                     commodity_guid=None, commodity_scu=None,
                     description=None, notes=None):
            self.name = name
            self.guid = guid
            self.account_type = account_type
            self.description = description
            self.parent_guid = parent_guid
            self.commodity_guid = commodity_guid
            self.commodity_scu = commodity_scu
            self.hidden = hidden
            self.notes = notes


        def __repr__(self):
            return "<Account {}>".format(self.guid)


    class Transaction(object):
        """
        A transaction is a balanced group of splits.
        """

        def __init__(self, guid=None, currency_guid=None,
                     post_date=None, date_entered=None, description=None):
            self.guid = guid
            self.currency_guid = currency_guid
            self.post_date = post_date
            self.date_entered = date_entered
            self.description = description
            # self.splits = splits or []
            # self.slots = slots or {}

        def __repr__(self):
            return u"<Transaction {}>".format(self.guid)

        def __lt__(self, other):
            # For sorted() only
            if isinstance(other, self.Transaction):
                return self.date < other.date
            else:
                False


    class Split(object):
        """
        A split is one entry in a transaction.
        """

        def __init__(self, guid=None, memo=None,
                     reconcile_state=None, reconcile_date=None, value=None,
                     quantity=None, account_guid=None, transaction_guid=None,
                     ):
            self.guid = guid
            self.reconcile_state = reconcile_state
            self.reconcile_date = reconcile_date
            self.value = value
            self.quantity = quantity
            self.account_guid = account_guid
            # self.transaction = transaction
            self.transaction_guid = transaction_guid
            self.memo = memo
            # self.slots = slots

        def __repr__(self):
            return "<Split {}>".format(self.guid)


if __name__ == "__main__":
    book_xml = GNUCashBookXML(timeing=True)
    filename = "c:/Temp/andrey/prog/gnucashreport/src/test/data/xirr-test.gnucash"
    book_xml.read_book(filename)
    print(book_xml.df_accounts.hidden[23])



