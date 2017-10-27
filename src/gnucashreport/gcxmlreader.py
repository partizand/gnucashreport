import decimal
import gzip
import pandas

from operator import attrgetter

from dateutil.parser import parse as parse_date
from xml.etree import ElementTree

from gnucashreport.abstractreader import AbstractReader
import gnucashreport.cols as cols

class GNUCashXMLBook(AbstractReader):
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

    @staticmethod
    def get_commodity_guid(space, name):
        return space + ":" + name

    @staticmethod
    def _parse_number(numstring):
        num, denum = numstring.split("/")
        return decimal.Decimal(num) / decimal.Decimal(denum)

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

    def _create_df(self, fields):
        df = pandas.DataFrame(columns=fields)
        # df.set_index(fields[0], inplace=True)
        return df

    def _create_dfs(self):
        # Accounts

        fields = [cols.GUID, cols.SHORTNAME, cols.ACCOUNT_TYPE,
                  "commodity_guid", "commodity_scu",
                  "parent_guid", "description", "hidden", "notes"]

        self.df_accounts = self._create_df(fields)



        # Transactions

        fields = [cols.GUID, cols.CURRENCY_GUID, cols.POST_DATE, "description"]

        self.df_transactions = self._create_df(fields)
        # self.df_transactions.rename(columns={'date': cols.POST_DATE}, inplace=True)

        # Splits
        fields = [cols.GUID, "transaction_guid", "account_guid",
                  "memo", "reconcile_state", "value", "quantity"]

        self.df_splits = self._create_df(fields)

        # commodity

        fields = [cols.GUID, cols.MNEMONIC, cols.NAMESPACE]
        self.df_commodities = self._create_df(fields)
        # self.df_commodities.rename(columns={'space': 'namespace'}, inplace=True)
        # self.df_commodities = self.df_commodities[self.df_commodities['namespace'] != 'template']

        # Prices
        fields = [cols.GUID, "commodity_guid", cols.CURRENCY_GUID,
                  "date", "source", "type", "value"]
        self.df_prices = self._create_df(fields)

        # Accounts

        fields = [cols.GUID, cols.SHORTNAME, cols.ACCOUNT_TYPE,
                  "commodity_guid", "commodity_scu",
                  "parent_guid", "description", "hidden", "notes"]

        self.df_accounts = self._create_df(fields)
        # self.df_accounts.rename(columns={'actype': cols.ACCOUNT_TYPE}, inplace=True)
        # self.root_account_guid = book.root_account_guid

        # Transactions

        fields = [cols.GUID, cols.CURRENCY_GUID, cols.POST_DATE, "description"]

        self.df_transactions = self._create_df(fields)

        # Splits
        fields = [cols.GUID, cols.TRANSACTION_GUID, cols.ACCOUNT_GUID,
                   "memo", "reconcile_state", cols.VALUE, cols.QUANTITY]

        self.df_splits = self._create_df(fields)

        # commodity

        fields = [cols.GUID, cols.MNEMONIC, cols.NAMESPACE]
        self.df_commodities = self._object_to_dataframe(self.commodities, fields)

        # Prices
        fields = [cols.GUID, cols.COMMODITY_GUID, cols.CURRENCY_GUID,
                  "date", "source", "type", cols.VALUE]
        self.df_prices = self._create_df(fields)


    def read_book(self, filename):
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
        self._create_dfs()  # Create dataframes with field and indexes
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
            # comm = self._commodity_from_tree(child)
            self._commodity_from_tree(child)
            # self.commodities.append(comm)



        # Prices

        # prices = []

        for child in tree.findall('{http://www.gnucash.org/XML/gnc}pricedb/price'):
            # price = self._price_from_tree(child)
            self._price_from_tree(child)
            # self.prices.append(price)

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
            comm = {cols.NAMESPACE: namespace, cols.MNEMONIC: mnemonic}
            self.df_commodities.loc[guid] = comm


        # return self.Commodity(guid=guid, namespace=namespace, mnemonic=mnemonic)

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
        currency_guid = self.get_commodity_guid(space=currency_space, name=currency_name)
        # currency = commoditydict[(currency_space, currency_name)]

        commodity_space = tree.find(pr + "commodity/" +
                                    cmdty + "space").text
        commodity_name = tree.find(pr + "commodity/" +
                                   cmdty + "id").text
        commodity_guid = self.get_commodity_guid(space=commodity_space, name=commodity_name)
        # commodity = commoditydict[(commodity_space, commodity_name)]

        xml_date = tree.find(pr + "time/" + ts + "date").text

        # print('xml_date={}'.format(xml_date))

        # date = parse_date(tree.find(pr + "time/" +
        #                             ts + "date").text)

        pd_date = pandas.to_datetime(xml_date)
        # pd_date = pandas.to_datetime(pd_date.date())


        # price = self.Price(guid=guid, commodity_guid=commodity_guid, currency_guid=currency_guid, date=date, source=source,
        #               price_type=price_type, value=value)
        # print('date = {}'.format(date))
        price = {cols.GUID: guid,
                    cols.COMMODITY_GUID: commodity_guid,
                 cols.CURRENCY_GUID: currency_guid,
                 "date": pd_date,
                 "source": source,
                 "type": price_type,
                 "value": value
                 }

        # df = pandas.DataFrame(price)


        self.df_prices =  self.df_prices.append(price, ignore_index=True)


        # self.df_prices.loc[guid] = price

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

        name = tree.find(act + 'name').text
        guid = tree.find(act + 'id').text
        account_type = tree.find(act + 'type').text
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
            commodity_space = tree.find(act + 'commodity/' +
                                        cmdty + 'space').text
            commodity_name = tree.find(act + 'commodity/' +
                                       cmdty + 'id').text
            commodity_scu = tree.find(act + 'commodity-scu').text
            # commodity = commoditydict[(commodity_space, commodity_name)]

            commodity_guid = self.get_commodity_guid(space=commodity_space, name=commodity_name)

        account = self.Account(name=name,
                          description=description,
                          guid=guid,
                          account_type=account_type,
                          hidden=hidden,
                          commodity_guid=commodity_guid,
                          commodity_scu=commodity_scu,
                          parent_guid=parent_guid,
                          notes=notes)

        account = {cols.GUID: guid,
                   cols.SHORTNAME: name,
                   cols.ACCOUNT_TYPE: account_type,
                   "commodity_guid": commodity_guid,
                   "commodity_scu": commodity_scu,
                  "parent_guid": parent_guid,
                   "description": description,
                   "hidden": hidden,
                   "notes": notes,
                  }

        self.df_accounts = self.df_accounts.append(account, ignore_index=True)

        # return account

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
        currency_guid = self.get_commodity_guid(space=currency_space, name=currency_name)
        # currency = commoditydict[(currency_space, currency_name)]
        xml_date = tree.find(trn + "date-posted/" + ts + "date").text
        # post_date = parse_date(tree.find(trn + "date-posted/" +
        #                             ts + "date").text)
        post_date = pandas.to_datetime(xml_date)
        # date_entered = parse_date(tree.find(trn + "date-entered/" +
        #                                     ts + "date").text)
        description = tree.find(trn + "description").text
        # slots = self._slots_from_tree(tree.find(trn + "slots"))
        # transaction = self.Transaction(guid=guid,
        #                           currency_guid=currency_guid,
        #                           post_date=post_date,
        #                           date_entered=date_entered,
        #                           description=description)

        # fields = [cols.GUID, cols.CURRENCY_GUID, cols.POST_DATE, "description"]

        transaction = {cols.GUID: guid,
                       cols.CURRENCY_GUID: currency_guid,
                       cols.POST_DATE: post_date,
                       "description": description}

        self.df_transactions = self.df_transactions.append(transaction, ignore_index=True)

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
        splt = {}

        splt[cols.GUID] = tree.find(split + "id").text # guid
        memo = tree.find(split + "memo")
        if memo is not None:
            splt["memo"] = memo.text


        reconciled_state = tree.find(split + "reconciled-state").text
        reconcile_date = tree.find(split + "reconcile-date/" + ts + "date")
        if reconcile_date is not None:
            reconcile_date = parse_date(reconcile_date.text)
        value = self._parse_number(tree.find(split + "value").text)
        quantity = self._parse_number(tree.find(split + "quantity").text)
        account_guid = tree.find(split + "account").text
        # account = accountdict[account_guid]
        slots = self._slots_from_tree(tree.find(split + "slots"))
        split = self.Split(guid=guid,
                      memo=memo,
                      reconcile_state=reconciled_state,
                      reconcile_date=reconcile_date,
                      value=value,
                      quantity=quantity,
                      account_guid=account_guid,
                      transaction_guid=transaction_guid
                      )

        fields = [cols.GUID, "transaction_guid", "account_guid",
                  "memo", "reconcile_state", "value", "quantity"]

        split = {cols.GUID, cols.TRANSACTION_GUID, cols.ACCOUNT_GUID,
                   "memo", "reconcile_state", cols.VALUE, cols.QUANTITY

        }

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
    book_xml = GNUCashXMLBook()
    filename = "c:/Temp/andrey/prog/gnucashreport/src/test/data/xirr-test.gnucash"
    book_xml.read_book(filename)
    print(book_xml.df_prices['value'])



