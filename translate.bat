set pygettext="c:\Python35\Tools\i18n\pygettext.py"
rem python.exe "%pygettext%" --output-dir=locale --default-domain=gnucashreport src/i-test.py src/gcreports/gnucashreport.py
python.exe "%pygettext%" --output-dir=locale --default-domain=gnucashreport src/

set msgfmt="c:\Python35\Tools\i18n\msgfmt.py"
python.exe "%msgfmt%" locale/messages.po
