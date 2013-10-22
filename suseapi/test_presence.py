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
Testing of presence module connector
'''

from unittest import TestCase, skipIf

import datetime
import os

from suseapi.presence import (
    trim_weekends,
    Presence
)

SKIP_NET = 'SKIP_NET_TEST' in os.environ


class PresenceTest(TestCase):
    def test_trim_weekends(self):
        self.assertEqual(
            datetime.date(2013, 7, 15),
            trim_weekends(datetime.date(2013, 7, 13)),
        )
        self.assertEqual(
            datetime.date(2013, 7, 12),
            trim_weekends(datetime.date(2013, 7, 13), -1),
        )
        self.assertEqual(
            datetime.date(2013, 7, 15),
            trim_weekends(datetime.date(2013, 7, 15)),
        )

    @skipIf(SKIP_NET, 'No network access')
    def test_presence(self):
        presence = Presence()
        self.assertIsNone(
            presence.is_absent('mcihar', datetime.date(2013, 7, 15))
        )
