#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2012 - 2015 Michal Čihař <mcihar@suse.cz>
#
# This file is part of python-suseapi
# <https://github.com/openSUSE/python-suseapi>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""Setup file for easy installation"""
from setuptools import setup
import os

VERSION = __import__('suseapi').__version__

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    LONG_DESCRIPTION = readme.read()

REQUIRES = open('requirements.txt').read().split()

setup(
    name='python-suseapi',
    version=VERSION,
    author='Michal Čihař',
    author_email='mcihar@suse.cz',
    description='Python module for SUSE APIs.',
    license='GPLv3+',
    keywords='suse, django',
    url='https://github.com/openSUSE/python-suseapi',
    download_url='https://pypi.python.org/pypi/python-suseapi',
    platforms=['any'],
    packages=[
        'suseapi',
    ],
    package_dir={'suseapi': 'suseapi'},
    package_data={'suseapi': [
        'testdata/*.xml',
        'testdata/maintained/opensuse',
        'testdata/maintained/sles',
        'testdata/maintained/_svn/*',
        'testdata/maintained/.svn-entries'
    ]},
    long_description=LONG_DESCRIPTION,
    install_requires=REQUIRES,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Internet',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

    entry_points={
        'console_scripts': ['suseapi = suseapi.main:main']
    },
)
