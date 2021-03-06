set pygettext="c:\Python35\Tools\i18n\pygettext.py"
set msgfmt="c:\Python35\Tools\i18n\msgfmt.py"
set domain=gnucashreport
set out-dir=src\gnucashreport\locale
set locale=ru

python.exe "%pygettext%" --output-dir="%out-dir%" --default-domain=%domain% src/gnucashreport/*

python.exe "%msgfmt%" "%out-dir%\%domain%.po"

copy "%out-dir%\%domain%.mo" "%out-dir%\%locale%\LC_MESSAGES\%domain%.mo"
copy "%out-dir%\%domain%.po" "%out-dir%\%locale%\LC_MESSAGES\%domain%.po"