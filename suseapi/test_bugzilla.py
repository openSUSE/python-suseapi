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
Testing of Bugzilla connector
'''

from unittest import TestCase

import datetime
import os
import httpretty

from suseapi.bugzilla import (
    APIBugzilla,
    Bugzilla,
    BugzillaNotPermitted,
    BugzillaLoginFailed,
    BugzillaInvalidBugId,
    BugzillaNotFound,
    WebScraperError,
    get_django_bugzilla,
)

TEST_DATA = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'testdata'
)


class BugzillaTest(TestCase):
    '''
    Bugzilla connector tests.
    '''
    _backup = {}

    @staticmethod
    def httpretty_login():
        httpretty.register_uri(
            httpretty.POST,
            'https://bugzilla.novell.com/index.cgi',
            body='<html><body><a href="#">Log\xc2\xa0out</a></body></html>',
            content_type='text/html',
        )
        httpretty.register_uri(
            httpretty.POST,
            'https://apibugzilla.novell.com/index.cgi',
            body='<html><body><a href="#">Log out</a></body></html>',
            content_type='text/html',
        )

    @httpretty.activate
    def test_get_bug(self):
        '''
        Test getting existing bug.
        '''
        httpretty.register_uri(
            httpretty.POST,
            'https://bugzilla.novell.com/show_bug.cgi?ctype=xml&id=81873',
            body=open(os.path.join(TEST_DATA, 'bug-81873.xml')).read(),
        )
        bugzilla = Bugzilla('', '')
        bug = bugzilla.get_bug(81873)
        self.assertEqual(bug.bug_id, '81873')
        self.assertTrue(bug.has_nonempty('classification'))

    @httpretty.activate
    def test_get_private_bug(self):
        '''
        Test getting private bug.
        '''
        httpretty.register_uri(
            httpretty.POST,
            'https://bugzilla.novell.com/show_bug.cgi?ctype=xml&id=582198',
            body=open(os.path.join(TEST_DATA, 'bug-582198.xml')).read(),
        )
        bugzilla = Bugzilla('', '')
        self.assertRaises(BugzillaNotPermitted, bugzilla.get_bug, 582198)

    @httpretty.activate
    def test_get_nonexisting_bug(self):
        '''
        Test getting non existing bug.
        '''
        httpretty.register_uri(
            httpretty.POST,
            'https://bugzilla.novell.com/show_bug.cgi?ctype=xml&id=20000000',
            body=open(os.path.join(TEST_DATA, 'bug-20000000.xml')).read(),
        )
        bugzilla = Bugzilla('', '')
        self.assertRaises(BugzillaNotFound, bugzilla.get_bug, 20000000)

    @httpretty.activate
    def test_get_invalid_bug(self):
        '''
        Test getting bug with invalid ID.
        '''
        httpretty.register_uri(
            httpretty.POST,
            'https://bugzilla.novell.com/show_bug.cgi?ctype=xml&id=none',
            body=open(os.path.join(TEST_DATA, 'bug-none.xml')).read(),
        )
        bugzilla = Bugzilla('', '')
        self.assertRaises(BugzillaInvalidBugId, bugzilla.get_bug, 'none')

    @httpretty.activate
    def test_login(self):
        '''
        Test login to novell bugzilla.
        '''
        httpretty.register_uri(
            httpretty.POST,
            'https://bugzilla.novell.com/index.cgi',
        )
        bugzilla = Bugzilla('', '')
        self.assertRaises(BugzillaLoginFailed, bugzilla.login)

    @httpretty.activate
    def test_get_flag_bug(self):
        '''
        Test that the bugzilla-flag are parsed as well.
        '''
        httpretty.register_uri(
            httpretty.POST,
            'https://bugzilla.novell.com/show_bug.cgi?ctype=xml&id=',
            body=open(os.path.join(TEST_DATA, 'bug-81872.xml')).read(),
        )
        bugzilla = Bugzilla('', '')
        bug = bugzilla.get_bug(81872)
        self.assertEqual(bug.bug_id, '81872')
        self.assertTrue(bug.has_nonempty('flags'))
        flag = bug.flags[0]
        self.assertEqual(flag['name'], 'needinfo')

    @httpretty.activate
    def test_get_multiple_flag_bug(self):
        '''
        Test that multiple flags can be handled as well.
        '''
        httpretty.register_uri(
            httpretty.POST,
            'https://bugzilla.novell.com/show_bug.cgi?ctype=xml&id=',
            body=open(os.path.join(TEST_DATA, 'bug-81871.xml')).read(),
        )
        bugzilla = Bugzilla('', '')
        bug = bugzilla.get_bug(81871)
        self.assertEqual(bug.bug_id, '81871')
        self.assertTrue(bug.has_nonempty('flags'))
        self.assertEqual(len(bug.flags), 2)

    def override_django_settings(self):
        if 'DJANGO_SETTINGS_MODULE' in os.environ:
            # Executed in Django context
            from django.conf import settings
            for setting in ('BUGZILLA_USERNAME', 'BUGZILLA_PASSWORD'):
                self._backup[setting] = getattr(settings, setting, '')
                setattr(settings, setting, 'test')
        else:
            # Non Django testing
            os.environ['DJANGO_SETTINGS_MODULE'] = \
                'suseapi.django_test_settings'

    def restore_django_settings(self):
        if 'BUGZILLA_USERNAME' in self._backup:
            from django.conf import settings
            for setting in ('BUGZILLA_USERNAME', 'BUGZILLA_PASSWORD'):
                setattr(settings, setting, self._backup[setting])

    @httpretty.activate
    def test_django_cache(self):
        self.override_django_settings()

        try:
            from django.core.cache import cache
            cache.set('bugzilla-access-cookies', [])

            bugzilla = get_django_bugzilla()
            self.assertTrue(bugzilla.cookie_set)
        finally:
            self.restore_django_settings()

    @httpretty.activate
    def test_django_login(self):
        self.override_django_settings()

        try:
            from django.core.cache import cache
            cache.delete('bugzilla-access-cookies')

            self.httpretty_login()
            bugzilla = get_django_bugzilla()
            self.assertFalse(bugzilla.cookie_set)
        finally:
            self.restore_django_settings()

    @httpretty.activate
    def test_django_relogin(self):
        self.override_django_settings()

        try:
            from django.core.cache import cache
            cache.set('bugzilla-access-cookies', [])

            bugzilla = get_django_bugzilla()
            self.assertTrue(bugzilla.cookie_set)
            self.httpretty_login()
            bugzilla.login(force=True)
        finally:
            self.restore_django_settings()

    @httpretty.activate
    def test_django_auto_relogin(self):
        self.override_django_settings()

        try:
            from django.core.cache import cache
            cache.set('bugzilla-access-cookies', [])

            bugzilla = get_django_bugzilla()
            self.assertTrue(bugzilla.cookie_set)

            httpretty.register_uri(
                httpretty.POST,
                'https://apibugzilla.novell.com/show_bug.cgi',
                status=502,
            )
            self.httpretty_login()
            self.assertRaises(WebScraperError, bugzilla.get_bug, 81873)

            self.assertFalse(bugzilla.cookie_set)
        finally:
            self.restore_django_settings()

    @httpretty.activate
    def test_apilogin(self):
        '''
        Test login to novell bugzilla.
        '''
        self.httpretty_login()
        bugzilla = APIBugzilla('test', 'test')
        bugzilla.login()

    @httpretty.activate
    def test_recent(self):
        '''
        Test fetching recent bugs.
        '''
        httpretty.register_uri(
            httpretty.POST,
            'https://bugzilla.novell.com/buglist.cgi',
            body=open(os.path.join(TEST_DATA, 'bug-list.xml')).read(),
        )
        bugzilla = Bugzilla('', '')
        recent = bugzilla.get_recent_bugs(datetime.datetime.now())
        self.assertEqual(
            recent,
            [
                847050,
                846768,
                846835,
                776687,
                843652,
                844761,
                845986,
                790286,
                846953,
                789222,
                844953
            ]
        )
