#!/usr/bin/python3
"""Setup
"""
import distutils.cmd
from setuptools import setup, find_packages

import gnucashreport


with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(name='gnucashreport',
      version=gnucashreport.__version__,
      author="Partizand",
      author_email="",
      url="https://github.com/partizand/gnucashreport",
      description="Reports from GnuCash to Excel",
      long_description=long_description,
      license="GPLv3",
      keywords=["GnuCash", "finance", "reports"],

      # cmdclass={'copyscript': CopyScript, 'genfiles': GenFiles},

      classifiers=[
          'Development Status :: 4 - Beta',
          'Programming Language :: Python :: 3',
          'Natural Language :: Russian',
          'Topic :: Office/Business :: Financial :: Accounting',
          'Topic :: Utilities',
          'Environment :: Console',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: GNU General Public License v3'],

      # packages=find_packages('src'),

      packages=['gnucashreport'],

      package_dir={'': 'src'},

      package_data={'gnucashreport': ['*.mo']},

      test_suite='test',

      install_requires=['setuptools', 'pandas', 'piecash', 'xlsxwriter'],
      #                   'appdirs'
      #                   ],
      # namespace_packages=["bankparser"],

      entry_points={
          'console_scripts':
              ['gcreport = src.gcreport:main'],
      },
      include_package_data=True,
      zip_safe=False
      )
