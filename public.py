"""
Script for public package on PyPi
"""
import unittest
import subprocess

import re

# Public to test pypi
test_public = False
suf_test = ['-r', 'pypitest']
# sdist command
cmd_sdist = ['python', 'setup.py', 'sdist', 'bdist_wheel', '--universal']



def find_version(filename):
    with open(filename, 'r') as f:
        version_file = f.read()
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                                  version_file, re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string.")

ver = find_version('src/gnucashreport/__init__.py')
reg_name = 'gnucashreport-{}-py2.py3-none-any.whl'.format(ver)

# public command
cmd_public = ['twine', 'upload', 'dist/{}'.format(reg_name)]
cmd_public_test = cmd_public + suf_test

# register command

cmd_register = ['twine.exe', 'register', 'dist/{}'.format(reg_name)]
cmd_register_test = cmd_register + suf_test

def run_all_test():
    print('Run all tests...')
    test_suite = unittest.defaultTestLoader.discover('src/test')
    test_runner = unittest.TextTestRunner(resultclass=unittest.TextTestResult)
    result = test_runner.run(test_suite)

    if not result.wasSuccessful():
        print('Tests fails! Exit')
        exit(2)
    return result


def build():
    # build
    print('Build dist')
    ret = subprocess.run(cmd_sdist)

    if ret.returncode != 0:
        print('setup.py sdist error! Exit.')
        exit(3)

    return ret


def register():
    # register
    print('Register')
    if test_public:
        ret = subprocess.run(cmd_register_test)
    else:
        ret = subprocess.run(cmd_register)

    if ret.returncode != 0:
        print('setup.py sdist error! Exit.')
        exit(3)

    return ret


def public():
    # Public
    print('Public')
    if test_public:
        ret = subprocess.run(cmd_public_test)
    else:
        ret = subprocess.run(cmd_public)

    if ret.returncode == 0:
        print('Public is successful')
    else:
        print('Error public')

    return ret






print('Publishing version {}'.format(ver))

# Run all tests
# run_all_test()

# build
build()

# register
# register()

# public
public()




