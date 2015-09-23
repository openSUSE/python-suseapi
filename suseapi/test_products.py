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
Testing of product name manipulations.
'''

from unittest import TestCase

from suseapi.products import codestream_name, codestream_base

PRODUCT_TESTS = (
    ('sles9-sp3', 'SLE-9-SP3', 'SLE-9'),
    ('sles9', 'SLE-9', 'SLE-9'),
    ('sles11-sp2-pl3', 'SLE-11-SP2-HWRefresh', 'SLE-11'),
    ('sle11-pl', 'SLE-11-HWRefresh', 'SLE-11'),
    ('slepos10', 'SLE-10-SP4', 'SLE-10'),
    ('openSUSE:12.1', 'OPENSUSE:12.1', 'OPENSUSE:12.1'),
)


class ProductTest(TestCase):
    '''
    Tests for product names mapping.
    '''

    def test_codestream_name(self):
        '''
        Tests getting codestream name.
        '''
        for product, expected, dummy in PRODUCT_TESTS:
            self.assertEqual(
                codestream_name(product),
                expected,
            )

    def test_codestream_base(self):
        '''
        Test getting codestream base.
        '''
        for dummy, codestream, expected in PRODUCT_TESTS:
            self.assertEqual(
                codestream_base(codestream),
                expected
            )
