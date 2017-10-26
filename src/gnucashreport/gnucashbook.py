import decimal


class GNUCashBook:
    """
    Abstract GnuCashBook and objects
    """

    def __init__(self):
        self.commodities = []
        self.prices = []
        self.accounts = []
        self.transactions = []
        self.splits = []
        self.root_account_guid = None



    @staticmethod
    def _parse_number(numstring):
        num, denum = numstring.split("/")
        return decimal.Decimal(num) / decimal.Decimal(denum)


    class Commodity(object):
        """
        A commodity is something that's stored in GNU Cash accounts.

        Consists of a name (or id) and a space (namespace).
        """

        def __init__(self, guid, name, space=None):
            self.guid = guid
            self.mnemonic = name
            self.name = name
            self.space = space



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
                     description=None, notes=None):
            self.name = name
            self.guid = guid
            self.actype = actype
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





