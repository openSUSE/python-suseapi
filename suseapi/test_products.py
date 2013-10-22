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
'''
Testing of product name manipulations.
'''

from unittest import TestCase

from suseapi.products import codestream_name

PRODUCT_TESTS = (
    ('sles9-sp3', 'SLE-9-SP3'),
    ('sles9', 'SLE-9'),
    ('sles11-sp2-pl3', 'SLE-11-SP2-HWRefresh'),
    ('sle11-pl', 'SLE-11-HWRefresh'),
)


class ProductTest(TestCase):
    def test_codestream_name(self):
        for product, expected in PRODUCT_TESTS:
            self.assertEqual(
                codestream_name(product),
                expected,
            )
