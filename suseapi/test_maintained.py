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
'''
Testing of maintained data parser.
'''

from unittest import TestCase
import os.path

from suseapi.maintained import (
    MaintainedData, load_maintained_data, get_revision
)

TEST_DATA = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'testdata',
    'maintained',
)


class MaintainedTest(TestCase):
    '''
    Maintained data tests.
    '''

    def test_opensuse(self):
        '''
        Test parsing openSUSE data.
        '''
        with open(os.path.join(TEST_DATA, 'opensuse')) as fileobj:
            maintained = MaintainedData('opensuse', fileobj)
        self.assertFalse(maintained.is_maintained())

    def test_sles(self):
        '''
        Test parsing SLES data.
        '''
        with open(os.path.join(TEST_DATA, 'sles')) as fileobj:
            maintained = MaintainedData('sles', fileobj)
        self.assertTrue(maintained.is_maintained())

    def test_load(self):
        '''
        Test loading directory.
        '''
        data = load_maintained_data(TEST_DATA)
        data = list(data)
        self.assertEquals(2, len(data))

    def test_revision(self):
        '''
        Test parsing revision info out of SVN.
        '''
        self.assertEquals(
            1235,
            get_revision(TEST_DATA)
        )
