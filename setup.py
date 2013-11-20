#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2012 - 2013 Michal Čihař <mcihar@suse.cz>
#
# This file is part of python-suseapi <https://github.com/nijel/python-suseapi>
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

version = __import__('suseapi').__version__

LONG_DESCRIPTION = """
python-suseapi is set of helpers to access various SUSE APIs.
"""

requires = [
    'Django>=1.4',
    'mechanize',
    'python-dateutil',
    'suds',
]

setup(
    name='python-suseapi',
    version=version,
    author='Michal Čihař',
    author_email='mcihar@suse.cz',
    description='Python module for SUSE APIs.',
    license='GPLv3+',
    keywords='suse, django',
    url='https://github.com/nijel/python-suseapi',
    download_url='https://pypi.python.org/pypi/python-suseapi',
    platforms=['any'],
    packages=[
        'suseapi',
    ],
    package_dir={'suseapi': 'suseapi'},
    package_data={'suseapi': [
        'testdata/*.xml', 'testdata/maintained/*',
        'testdata/maintained/.svn-entries'
    ]},
    long_description=LONG_DESCRIPTION,
    install_requires=requires,
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
)
