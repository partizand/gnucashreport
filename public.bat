rem register project on PyPi
rem Only once need!!!!

call ".pycharmrc.bat"

python setup.py sdist bdist_wheel --universal

twine.exe register dist/gnucashreport-0.1.0-py2.py3-none-any.whl

twine upload dist/*