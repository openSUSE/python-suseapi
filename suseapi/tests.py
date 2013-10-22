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
Testing of Bugzilla connector
'''

from django.test import TestCase
from django.utils.unittest import skipIf

import datetime
import os

from suseapi.bugzilla import (
    Bugzilla,
    BugzillaNotPermitted,
    BugzillaLoginFailed,
)
from suseapi.presence import (
    trim_weekends,
    Presence
)
from suseapi.userinfo import DjangoUserInfo
from suseapi.djangobugzilla import DjangoBugzilla
from suseapi.products import codestream_name

PRODUCT_TESTS = (
    ('sles9-sp3', 'SLE-9-SP3'),
    ('sles9', 'SLE-9'),
    ('sles11-sp2-pl3', 'SLE-11-SP2-HWRefresh'),
    ('sle11-pl', 'SLE-11-HWRefresh'),
)

SKIP_NET = 'SKIP_NET_TEST' in os.environ


class BugzillaTest(TestCase):
    @skipIf(SKIP_NET, 'No network access')
    def test_get_bug(self):
        bugzilla = Bugzilla('', '')
        bug = bugzilla.get_bug(81873)
        self.assertEqual(bug.bug_id, '81873')

    @skipIf(SKIP_NET, 'No network access')
    def test_get_private_bug(self):
        bugzilla = Bugzilla('', '')
        self.assertRaises(BugzillaNotPermitted, bugzilla.get_bug, 582198)

    @skipIf(SKIP_NET, 'No network access')
    def test_login(self):
        bugzilla = Bugzilla('', '')
        self.assertRaises(BugzillaLoginFailed, bugzilla.login)

    @skipIf(SKIP_NET, 'No network access')
    def test_recent(self):
        bugzilla = Bugzilla('', '')
        recent = bugzilla.get_recent_bugs(datetime.datetime.now())
        self.assertEqual(recent, [])


class DjangoBugzillaTest(TestCase):
    @skipIf(SKIP_NET, 'No network access')
    def test_get_bug(self):
        bugzilla = DjangoBugzilla('', '')
        bug = bugzilla.get_bug(81873)
        self.assertEqual(bug.bug_id, '81873')


class ProductTest(TestCase):
    def test_codestream_name(self):
        for product, expected in PRODUCT_TESTS:
            self.assertEqual(
                codestream_name(product),
                expected,
            )


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


class UserInfoTest(TestCase):
    @skipIf(SKIP_NET, 'No network access')
    def test_django_department(self):
        userinfo = DjangoUserInfo()
        self.assertEqual(
            'L3/Maintenance',
            userinfo.get_department('mcihar')
        )
        self.assertEqual(
            'L3/Maintenance',
            userinfo.get_department('mcihar@suse.com')
        )
        self.assertEqual(
            'Security team',
            userinfo.get_department('security-team@suse.de')
        )
