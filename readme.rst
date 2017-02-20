GnuCash reports
===============

Sorry for my English!

Library for get reports from `GnuCash <http://gnucash.org>`_ to excel.

Connect directly to GnuCash book (xml or sql) and use `Pandas <http://pandas.pydata.org/>`_ for calculation reports.
No cycles for calculation, less errors, less code.

Install
-------

To install

    python setup.py install

You may use virtualenv.

depending on (install automatically)

- pandas
- piecash

Examples
--------

>>> import gnucashreport
>>> gcrep = gnucashreport.GNUCashReport()

open sql book

>>> gcrep.open_book_sql('v:/gnucash-base/sqlite/GnuCash-base.gnucash', open_if_lock=True)

save all splits to Excel (with account name, decription, currency mnemonic and other)

>>> from gnucashreport.utils import dataframe_to_excel
>>> dataframe_to_excel(gcrep.df_splits, 'v:/tables/splits.xlsx')

save reports by years in xlsx file

>>> gcrep.all_reports_excel('v:/tables/ex-test.xlsx', glevel=1)

Explain glevel
--------------

glevel - group level of accounts: array of levels or single int level

Examples:

Accounts structure:

======= =============== ========
account levels
------- --------------- --------
0       1               2
======= =============== ========
Assets: Current assets: Cash
Assets: Current assets: Card
Assets: reserve:        Deposite
Assets: reserve:        Cash
======= =============== ========

Example 1::

    glevel=[0, 1]

Group accounts for 0 and 1 level, into 2 rows and 2 columns (Multiindex dataframe):

+------------+----------------+
| 0          | 1              |
+============+================+
| Assets     | Current assets |
+            +----------------+
|            | Reserve        |
+------------+----------------+

Example 2::

    glevel=1

Groups only 1 level, into 2 rows and 1 column:

+----------------+
| 1              |
+================+
| Current assets |
+----------------+
| reserve        |
+----------------+



Testing
-------

All my testing data is real. Then all testing function use external folder.
For create test data, save sql book file and xml book file into any folder. Use the same data for sql and xml.
Create empty folder for test data.
Set this options in src/test/basetest.py

.. code-block:: python

    bookfile_sql = your_sql_base
    bookfile_xml = your_xml_base
    dir_testdata = folder_for_test_data


Run the script src/test/savetestdata.py. Run only on working branch version!

Now you may run tests.

    setup.py test

license
-------

GNU GPL 3

author
------

Partizand

