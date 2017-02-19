GnuCash reports
===============

Get reports from `GnuCash <http://gnucash.org>`_ to excel.

Попытка получить отчеты из `GnuCash <http://gnucash.org>`_

Testing
-------

All my testing data is real. Then all testing function use external folder.
For create test data, save sql book file and xml book file into any folder. Use the same data for sql and xml.
Create empty folder for test data.
Set this options in src/test/basetest

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

