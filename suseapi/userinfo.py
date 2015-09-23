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
Simple wrapper around LDAP module to allow easier search.
'''

import ldap
from suseapi.cacher import CacherMixin, DjangoCacherMixin


class UserInfo(CacherMixin):
    '''
    Class for LDAP access.
    '''

    cache_key_template = 'userinfo-%s'

    searches = [
        ('mail', '{0}@novell.com'),
        ('mail', '{0}@suse.com'),
        ('uid', '{0}'),
        ('cn', '{0}'),
    ]

    department_fixups = {
        'Business Support Nurenburg': u'Business Support Nürnberg',
        'L3 Maintenance': 'L3/Maintenance',
    }

    def __init__(self, server, base):
        self._ldap = ldap.initialize(server)
        self._base = base

    def search_uid(self, uid, attribs=None):
        '''
        Performs uid based search.
        '''
        if attribs is None:
            attribs = ['cn', 'mail', 'ou', 'sn', 'givenName']

        for attr, val in self.searches:
            val = val.format(uid)
            result = self.search_by(attr, val, attribs)
            if len(result) > 0:
                return result
        return []

    def search_by(self, attr, val, attribs=None):
        """
        :param attr: attribute name to search by
        :param val: value of the attribute to search for
        :param attribs: attributes to return
        """
        filterstring = '({0}={1})'.format(attr, val)
        try:
            return self._ldap.search_s(
                self._base,
                # pylint: disable=E1101
                ldap.SCOPE_SUBTREE,
                filterstring,
                attribs
            )
        # pylint: disable=E1101
        except ldap.NO_SUCH_OBJECT:
            return []

    def fixup_department(self, name):
        '''
        Fixups some common mistakes in department name.
        '''
        if name in self.department_fixups:
            return self.department_fixups[name]

        return name

    def get_department(self, user):
        '''
        Returns user department.
        '''
        department = self.cache_get(user)
        if department is not None:
            return department

        if user == 'security-team@suse.de':
            department = 'Security team'
        else:
            if user.find('@') == -1:
                username = user
            else:
                if user[-9:] == '@suse.com':
                    username = user[:-9]
                elif user[-11:] == '@novell.com':
                    username = user[:-11]
                else:
                    return 'External'

            userdata = self.search_uid(username)

            try:
                dept = userdata[0][1]['ou'][0]
            except IndexError:
                return 'N/A'

            department = self.fixup_department(dept)

        self.cache_set(user, department)

        return department


class DjangoUserInfo(UserInfo, DjangoCacherMixin):
    '''
    Django caching for user information.
    '''

    def __init__(self, server=None, base=None):
        from django.conf import settings
        if server is None:
            server = settings.LDAP_HOST
        if base is None:
            base = settings.LDAP_BASE
        super(DjangoUserInfo, self).__init__(server, base)
