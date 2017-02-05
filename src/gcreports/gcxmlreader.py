import decimal
import gzip

from dateutil.parser import parse as parse_date
from xml.etree import ElementTree


class GNUCashXMLBook:
    """
    Reads contents of GNUCash xml file into arrays
    """
    def __init__(self):
        self.commodities = []
        self.prices = []
        self.accounts = []
        self.transactions = []
        self.splits = []
        self.root_account_guid = None


    ##################################################################
    # XML file parsing

    def read_from_xml(self, filename):
        """
        Read a GNU Cash xml file
        :param filename:
        :return:
        """
        """Parse a GNU Cash file and return a dictionary object."""
        try:
            # try opening with gzip decompression
            self.parse(gzip.open(filename, "rb"))
        except IOError:
            # try opening without decompression
            self.parse(open(filename, "rb"))

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
        self._book_from_tree(root.find("{http://www.gnucash.org/XML/gnc}book"))

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
            comm = self._commodity_from_tree(child)
            self.commodities.append(comm)
            # commoditydict[(comm.space, comm.name)] = comm

        # ret_dict['commodities'] = commodities

        # Prices

        # prices = []

        for child in tree.findall('{http://www.gnucash.org/XML/gnc}pricedb/price'):
            price = self._price_from_tree(child)
            self.prices.append(price)
        # ret_dict['prices'] = prices

        # root_account = None
        # accountdict = {}
        # accounts = []
        for child in tree.findall('{http://www.gnucash.org/XML/gnc}account'):
            acc = self._account_from_tree(child)
            self.accounts.append(acc)

        # ret_dict['accounts'] = accounts

        # transactions = []
        # splits = []
        for child in tree.findall('{http://www.gnucash.org/XML/gnc}'
                                  'transaction'):
            transaction = self._transaction_from_tree(child)
            self.transactions.append(transaction)
            for split in transaction.splits:
                self.splits.append(split)

        # ret_dict['transactions'] = transactions
        # ret_dict['splits'] = splits

        # slots = _slots_from_tree(tree.find('{http://www.gnucash.org/XML/book}slots'))

        # book = Book(commodities=commodities, prices=prices, accounts=accounts, transactions=transactions, splits=splits)

        # return book

        # return Book(guid=guid,
        #             transactions=transactions,
        #             root_account=root_account,
        #             commodities=commodities,
        #             slots=slots)

    # <gnc:commodity version="2.0.0">
    #   <cmdty:space>Metal</cmdty:space>
    #   <cmdty:id>VTB.AG</cmdty:id>
    #   <cmdty:name>VTB.AG (Серебро ВТБ24)</cmdty:name>
    #   <cmdty:fraction>1</cmdty:fraction>
    # </gnc:commodity>

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
        name = tree.find('{http://www.gnucash.org/XML/cmdty}id').text
        space = tree.find('{http://www.gnucash.org/XML/cmdty}space').text
        return Commodity(name=name, space=space)

    # <gnc:transaction version="2.0.0">
    #   <trn:id type="guid">0ca8dd03d731d95319f0d6d09ff6b45d</trn:id>
    #   <trn:currency>
    #     <cmdty:space>ISO4217</cmdty:space>
    #     <cmdty:id>RUB</cmdty:id>
    #   </trn:currency>
    #   <trn:date-posted>
    #     <ts:date>2014-10-07 15:00:00 +0400</ts:date>
    #   </trn:date-posted>
    #   <trn:date-entered>
    #     <ts:date>2014-10-07 14:22:25 +0400</ts:date>
    #   </trn:date-entered>
    #   <trn:description>Аванс за входную дверь, Планета дверей</trn:description>
    #   <trn:slots>
    #     <slot>
    #       <slot:key>date-posted</slot:key>
    #       <slot:value type="gdate">
    #         <gdate>2014-10-07</gdate>
    #       </slot:value>
    #     </slot>
    #   </trn:slots>
    #   <trn:splits>
    #     <trn:split>
    #       <split:id type="guid">f96428bdff47ac0a8b76e86b80eb53c6</split:id>
    #       <split:reconciled-state>n</split:reconciled-state>
    #       <split:value>900000/100</split:value>
    #       <split:quantity>900000/100</split:quantity>
    #       <split:account type="guid">051af5c19d228a5fec92055c62832f8d</split:account>
    #     </trn:split>
    #     <trn:split>
    #       <split:id type="guid">0f2f309c4e895ea374849a41dfec2cfa</split:id>
    #       <split:reconciled-state>y</split:reconciled-state>
    #       <split:reconcile-date>
    #         <ts:date>2016-09-12 23:59:59 +0300</ts:date>
    #       </split:reconcile-date>
    #       <split:value>-900000/100</split:value>
    #       <split:quantity>-900000/100</split:quantity>
    #       <split:account type="guid">e3905b3497e2341a0730e62b614f7c56</split:account>
    #     </trn:split>
    #   </trn:splits>
    # </gnc:transaction>

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

    def _price_from_tree(self, tree):
        pr = '{http://www.gnucash.org/XML/price}'
        cmdty = '{http://www.gnucash.org/XML/cmdty}'
        ts = '{http://www.gnucash.org/XML/ts}'

        # guid = tree.find('{http://www.gnucash.org/XML/price}id').text
        # source = tree.find('{http://www.gnucash.org/XML/price}source').text
        # price_type = tree.find('{http://www.gnucash.org/XML/price}type').text
        # str_value = tree.find('{http://www.gnucash.org/XML/price}value').text



        # split = '{http://www.gnucash.org/XML/split}'

        # currency = '{http://www.gnucash.org/XML/currency}'
        # commodity = '{http://www.gnucash.org/XML/commodity}'
        # price_time = '{http://www.gnucash.org/XML/time}'

        guid = tree.find(pr + "id").text
        source = tree.find(pr + "source").text
        tree_type = tree.find(pr + "type")
        if tree_type:
            price_type = tree_type.text
        else:
            price_type = None
        str_value = tree.find(pr + "value").text
        value = self._parse_number(str_value)
        currency_space = tree.find(pr + "currency/" +
                                   cmdty + "space").text
        currency_name = tree.find(pr + "currency/" +
                                  cmdty + "id").text
        currency_guid = Commodity.get_commodity_guid(space=currency_space, name=currency_name)
        # currency = commoditydict[(currency_space, currency_name)]

        commodity_space = tree.find(pr + "commodity/" +
                                    cmdty + "space").text
        commodity_name = tree.find(pr + "commodity/" +
                                   cmdty + "id").text
        commodity_guid = Commodity.get_commodity_guid(space=commodity_space, name=commodity_name)
        # commodity = commoditydict[(commodity_space, commodity_name)]

        date = parse_date(tree.find(pr + "time/" +
                                    ts + "date").text)

        price = Price(guid=guid, commodity_guid=commodity_guid, currency_guid=currency_guid, date=date, source=source,
                      price_type=price_type, value=value)

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

        name = tree.find(act + 'name').text
        guid = tree.find(act + 'id').text
        actype = tree.find(act + 'type').text
        description = tree.find(act + "description")
        if description is not None:
            description = description.text
        slots = self._slots_from_tree(tree.find(act + 'slots'))

        if 'hidden' in slots.keys():
            hid = slots['hidden']
            if hid.lower() == 'true':
                hidden = True
            else:
                hidden = False
        else:
            hidden = False
        # hidden = slots['hidden']
        # {'reconcile-info': {'include-children': 0, 'last-date': 1324151999, 'last-interval': {'days': 7, 'months': 0}},
        #  'color': 'Not Set', 'hidden': 'true', 'placeholder': 'true'}
        if actype == 'ROOT':
            parent_guid = None
            commodity = None
            commodity_scu = None
            commodity_guid = None
            self.root_account_guid = guid
        else:
            parent_guid = tree.find(act + 'parent').text
            commodity_space = tree.find(act + 'commodity/' +
                                        cmdty + 'space').text
            commodity_name = tree.find(act + 'commodity/' +
                                       cmdty + 'id').text
            commodity_scu = tree.find(act + 'commodity-scu').text
            # commodity = commoditydict[(commodity_space, commodity_name)]

            commodity_guid = Commodity.get_commodity_guid(space=commodity_space, name=commodity_name)

        account = Account(name=name,
                          description=description,
                          guid=guid,
                          actype=actype,
                          hidden=hidden,
                          commodity_guid=commodity_guid,
                          commodity_scu=commodity_scu,
                          slots=slots,
                          parent_guid=parent_guid)

        return account

    # Implemented:
    # - trn:id
    # - trn:currency
    # - trn:date-posted
    # - trn:date-entered
    # - trn:description
    # - trn:splits / trn:split
    # - trn:slots

    # <gnc:transaction version="2.0.0">
    #   <trn:id type="guid">0ca8dd03d731d95319f0d6d09ff6b45d</trn:id>
    #   <trn:currency>
    #     <cmdty:space>ISO4217</cmdty:space>
    #     <cmdty:id>RUB</cmdty:id>
    #   </trn:currency>
    #   <trn:date-posted>
    #     <ts:date>2014-10-07 15:00:00 +0400</ts:date>
    #   </trn:date-posted>
    #   <trn:date-entered>
    #     <ts:date>2014-10-07 14:22:25 +0400</ts:date>
    #   </trn:date-entered>
    #   <trn:description>Аванс за входную дверь, Планета дверей</trn:description>
    #   <trn:slots>
    #     <slot>
    #       <slot:key>date-posted</slot:key>
    #       <slot:value type="gdate">
    #         <gdate>2014-10-07</gdate>
    #       </slot:value>
    #     </slot>
    #   </trn:slots>
    #   <trn:splits>
    #     <trn:split>
    #       <split:id type="guid">f96428bdff47ac0a8b76e86b80eb53c6</split:id>
    #       <split:reconciled-state>n</split:reconciled-state>
    #       <split:value>900000/100</split:value>
    #       <split:quantity>900000/100</split:quantity>
    #       <split:account type="guid">051af5c19d228a5fec92055c62832f8d</split:account>
    #     </trn:split>
    #     <trn:split>
    #       <split:id type="guid">0f2f309c4e895ea374849a41dfec2cfa</split:id>
    #       <split:reconciled-state>y</split:reconciled-state>
    #       <split:reconcile-date>
    #         <ts:date>2016-09-12 23:59:59 +0300</ts:date>
    #       </split:reconcile-date>
    #       <split:value>-900000/100</split:value>
    #       <split:quantity>-900000/100</split:quantity>
    #       <split:account type="guid">e3905b3497e2341a0730e62b614f7c56</split:account>
    #     </trn:split>
    #   </trn:splits>
    # </gnc:transaction>

    # def _commodity_guid(self, ):

    def _transaction_from_tree(self, tree):
        trn = '{http://www.gnucash.org/XML/trn}'
        cmdty = '{http://www.gnucash.org/XML/cmdty}'
        ts = '{http://www.gnucash.org/XML/ts}'
        split = '{http://www.gnucash.org/XML/split}'

        guid = tree.find(trn + "id").text
        currency_space = tree.find(trn + "currency/" +
                                   cmdty + "space").text
        currency_name = tree.find(trn + "currency/" +
                                  cmdty + "id").text
        currency_guid = Commodity.get_commodity_guid(space=currency_space, name=currency_name)
        # currency = commoditydict[(currency_space, currency_name)]
        date = parse_date(tree.find(trn + "date-posted/" +
                                    ts + "date").text)
        date_entered = parse_date(tree.find(trn + "date-entered/" +
                                            ts + "date").text)
        description = tree.find(trn + "description").text
        slots = self._slots_from_tree(tree.find(trn + "slots"))
        transaction = Transaction(guid=guid,
                                  currency_guid=currency_guid,
                                  date=date,
                                  date_entered=date_entered,
                                  description=description)

        for subtree in tree.findall(trn + "splits/" + trn + "split"):
            split = self._split_from_tree(tree=subtree, transaction_guid=transaction.guid)
            self.splits.append(split)
            # transaction.splits.append(split)

        return transaction

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
        split = '{http://www.gnucash.org/XML/split}'
        ts = "{http://www.gnucash.org/XML/ts}"

        guid = tree.find(split + "id").text
        memo = tree.find(split + "memo")
        if memo is not None:
            memo = memo.text
        reconciled_state = tree.find(split + "reconciled-state").text
        reconcile_date = tree.find(split + "reconcile-date/" + ts + "date")
        if reconcile_date is not None:
            reconcile_date = parse_date(reconcile_date.text)
        value = self._parse_number(tree.find(split + "value").text)
        quantity = self._parse_number(tree.find(split + "quantity").text)
        account_guid = tree.find(split + "account").text
        # account = accountdict[account_guid]
        slots = self._slots_from_tree(tree.find(split + "slots"))
        split = Split(guid=guid,
                      memo=memo,
                      reconcile_state=reconciled_state,
                      reconcile_date=reconcile_date,
                      value=value,
                      quantity=quantity,
                      account_guid=account_guid,
                      transaction_guid=transaction_guid,
                      slots=slots)
        # account.splits.append(split)
        return split

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

    @staticmethod
    def _parse_number(numstring):
        num, denum = numstring.split("/")
        return decimal.Decimal(num) / decimal.Decimal(denum)


class Commodity(object):
    """
    A commodity is something that's stored in GNU Cash accounts.

    Consists of a name (or id) and a space (namespace).
    """
    def __init__(self, name, space=None):
        self.guid = self.get_commodity_guid(space, name)
        self.mnemonic = name
        self.name = name
        self.space = space

    @staticmethod
    def get_commodity_guid(space, name):
        return space + ":" + name

    def __str__(self):
        return self.name

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
        self.price_type = price_type
        self.value = value

    def __str__(self):
        return self.guid

    def __repr__(self):
        return "<Price {}>".format(self.guid)

class Account(object):
    """
    An account is part of a tree structure of accounts and contains splits.
    """

    def __init__(self, name, guid, actype, hidden, parent_guid=None,
                 commodity_guid=None, commodity_scu=None,
                 description=None):
        self.name = name
        self.guid = guid
        self.actype = actype
        self.description = description
        self.parent_guid = parent_guid
        # self.children = []
        self.commodity_guid = commodity_guid
        self.commodity_scu = commodity_scu
        self.hidden = hidden
        # self.splits = []
        # self.slots = slots or {}

    def __repr__(self):
        return "<Account {}>".format(self.guid)

class Transaction(object):
    """
    A transaction is a balanced group of splits.
    """

    def __init__(self, guid=None, currency_guid=None,
                 date=None, date_entered=None, description=None):
        self.guid = guid
        self.currency_guid = currency_guid
        self.date = date
        self.date_entered = date_entered
        self.description = description
        # self.splits = splits or []
        # self.slots = slots or {}

    def __repr__(self):
        return u"<Transaction {}>".format(self.guid)

    def __lt__(self, other):
        # For sorted() only
        if isinstance(other, Transaction):
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
                 slots=None):
        self.guid = guid
        self.reconcile_state = reconcile_state
        self.reconcile_date = reconcile_date
        self.value = value
        self.quantity = quantity
        self.account_guid = account_guid
        # self.transaction = transaction
        self.transaction_guid = transaction_guid
        self.memo = memo
        self.slots = slots

    def __repr__(self):
        return "<Split {}>".format(self.guid)

    # def __lt__(self, other):
    #     # For sorted() only
    #     if isinstance(other, Split):
    #         return self.transaction < other.transaction
    #     else:
    #         False




if __name__ == '__main__':
    filename = 'U:/xml_book/GnuCash-base.gnucash'
    book = GNUCashXMLBook()
    book.read_from_xml(filename)

    print(book.prices)

