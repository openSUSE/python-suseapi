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
Testing of cacher mixin
'''

from unittest import TestCase
import os

from suseapi.cacher import CacherMixin, DjangoCacherMixin


class CacherTest(TestCase):
    cache = None

    def setUp(self):
        self.cache = CacherMixin()

    def test_empty(self):
        self.assertTrue(self.cache.cache_get('empty') is None)

    def test_set(self):
        self.cache.cache_set('value', 42)
        self.assertEqual(self.cache.cache_get('value'), 42)


class DjangoCacherTest(CacherTest):
    def setUp(self):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'suseapi.django_test_settings'
        self.cache = DjangoCacherMixin()
