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
Testing of user information connector
'''

from unittest import TestCase
from mockldap import MockLdap

from suseapi.userinfo import UserInfo


def start_ldap_mock():
    """
    Starts LDAP mocking.
    """
    mockldap = MockLdap({
        'o=Novell': {'o': 'Novell'},
        'cn=mcihar,o=Novell': {
            'mail': ['mcihar@suse.com'],
            'ou': ['TestDept'],
            'cn': ['mcihar'],
            'uid': ['mcihar'],
        },
        'cn=foobar,o=Novell': {
            'mail': ['foobar@suse.com'],
            'ou': ['L3 Maintenance'],
            'cn': ['foobar'],
            'uid': ['foobar'],
        },
    })
    mockldap.start()
    return mockldap


class UserInfoTest(TestCase):
    '''
    User information tests.
    '''

    def test_department(self):
        '''
        Test department lookups.
        '''
        mockldap = start_ldap_mock()
        try:
            userinfo = UserInfo('ldap://ldap', 'o=novell')
            # By mail with fixup
            self.assertEqual(
                'L3/Maintenance',
                userinfo.get_department('foobar@novell.com')
            )
            # By UID
            self.assertEqual(
                'TestDept',
                userinfo.get_department('mcihar')
            )
            # By UID from cache
            self.assertEqual(
                'TestDept',
                userinfo.get_department('mcihar')
            )
            # By email
            self.assertEqual(
                'TestDept',
                userinfo.get_department('mcihar@suse.com')
            )
            # Hardcoded entries
            self.assertEqual(
                'Security team',
                userinfo.get_department('security-team@suse.de')
            )
            # Non existing entry
            self.assertEqual(
                'N/A',
                userinfo.get_department('nobody')
            )
        finally:
            mockldap.stop()
