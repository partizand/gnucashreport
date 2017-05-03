GnuCash reports
===============

Sorry for my English!

Python library for get reports from `GnuCash <http://gnucash.org>`_ to xlsx files.

It connects directly to the GnuCash book (xml or sql) and `Pandas <http://pandas.pydata.org/>`_ use to building reports.
No cycles for calculation, less errors, less code.

The library is cross-platform, Excel is not required, you can use LibreOffice/OpenOffice

GnuCash python bindings not use, because it platform depended and unstable.
Piecash need only for get data from sql and in the future it may be replaced by bindings or sqlalchemy,
without changing the architecture. Not using piecash calculation and walk functions.
All data from GnuCash loads into DataFrames as is, table to table. Then data are processed only thru Pandas.

Install
-------

#. Install `Python <https://www.python.org/downloads/>`_ version 3 (version 2 should work, but I have not tested)

#. Install gnucashreport::

    pip install gnucashreport

Now, you may use cli tool gcreport

.. [#] Pandas need install before, because numpy have `installation thru install_requires directive issue <https://github.com/numpy/numpy/issues/2434>`_

Simple command line tool
------------------------

Library contain the simple cli tool, usage::

    gcreport gnucash_file xlsx_file [--glevel glevel] [--open_if_lock]

gnucash_file
       Your gnucash database file

xlsx_file
       Path to xlsx file for saving reports

--glevel glevel    Level to group accounts, may be multiple (--glevel 0 --glevel 1)

--open_if_lock     Open sqlite base even if opened other user

It's save all reports to excel file. (As all_reports_excel function)

Examples
--------

>>> import gnucashreport
>>> gcrep = GCReport()

open gnucash book (sql or xml)

>>> gcrep.open_book_file('v:/gnucash-base/sqlite/GnuCash-base.gnucash', open_if_lock=True)

save all splits to Excel (with account name, decription, currency mnemonic and other)

>>> from gnucashreport.utils import dataframe_to_excel
>>> dataframe_to_excel(gcrep.df_splits, 'v:/tables/splits.xlsx')

Save complex reports in xlsx file:

This report contain:

- Income, expense, profit, assets, loans, equity by months each year (sheet on each year)
- Income, expense, profit, assets, loans, equity by years on each full year
- Personal inflation (annual expenditure growth)
- Return on assets
- Some charts

>>> gcrep.all_reports_excel('v:/tables/ex-test.xlsx', glevel=1)

Return on assets
----------------

This option is experimental. A few tests written. But it looks like the truth :)

The library may consider the profitability of accounts taking into account the hierarchy.
Any asset accounts: deposit, liability, bank, not only stock. You can calculate the yield for all time or a specified period.
You can calculate the portfolio return of the stock or all of the assets.

You should mark the account of incomes and expenses for calculation of yield.
Set **%invest%** in notes of account. Then the account and its descendants will be taken into when calculating profitability.
If you mark the account **%no_invest%** in notes, it and its descendants will not be considered in calculating the yield

.. code-block:: python

    # open gnucash book
    import gnucashreport
    gcrep = GCReport()
    gcrep.open_book_file(your_gnucash_file)

    # Get return on assets
    df_return = gcrep.yield_calc()

    # Save results
    dataframe_to_excel(df_return, 'returns.xlsx')


See the sheet 'return' in .xlsx file after launch command line tool

All results are displayed in percent per annum:

Total
     The total return on asset taking into account the costs

Money flow
    Profitability money flow from account. Dividends, interests on other account, etc

Expense
    The costs of servicing the account (per annum)

Capital
    Capital gains


Explain glevel
--------------

glevel - how group accounts by levels: array of levels or single int level

Examples:

Accounts structure:

======= =============== ========
 account levels
--------------------------------
0       1               2
======= =============== ========
Assets: Current assets: Cash
Assets: Current assets: Card
Assets: Reserve:        Deposite
Assets: Reserve:        Cash
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
| Reserve        |
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


Run the script src/test/savetestdata.py. Run only on working commit version!

Now you may run tests.

    setup.py test

license
-------

`GNU GPL 3 <https://www.gnu.org/licenses/gpl.html>`_

author
------

Partizand

