#!/usr/bin/python3
"""Setup
pandas need install before (numpy issue install_requires)

    pip install pandas

"""
import distutils.cmd
import os

import re

import io
from setuptools import setup, find_packages


# find version in init file
def find_version(filename):
    with open(filename, 'r') as f:
        version_file = f.read()
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                                  version_file, re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string.")

version = find_version("src/gnucashreport/__init__.py")

with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(name='gnucashreport',
      version=version,
      author="Partizand",
      author_email="",
      url="https://github.com/partizand/gnucashreport",
      description="Reports from GnuCash to xlsx files",
      long_description=long_description,
      license="GPLv3",
      keywords=["GnuCash", "finance", "reports"],

      # cmdclass={'copyscript': CopyScript, 'genfiles': GenFiles},

      classifiers=[
          'Development Status :: 4 - Beta',
          'Programming Language :: Python :: 3',
          # 'Natural Language :: Russian',
          'Topic :: Office/Business :: Financial :: Accounting',
          'Topic :: Utilities',
          'Environment :: Console',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'],

      # packages=find_packages('src'),

      packages=['gnucashreport'],

      package_dir={'': 'src'},

      package_data={'gnucashreport': ['*.mo']},

      test_suite='test',

      install_requires=['numpy', 'pandas', 'xlsxwriter', 'python-dateutil'],
      #                   'appdirs'
      #                   ],

      entry_points={
          'console_scripts':
              ['gcreport = gnucashreport.gcreportcli:main'],
      },
      include_package_data=True,
      zip_safe=False
      )
