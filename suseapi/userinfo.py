# -*- coding: UTF-8 -*-
'''
Simple wrapper around LDAP module to allow easier search.
'''

import ldap
from suseapi.cacher import CacherMixin, DjangoCacherMixin


class UserInfo(CacherMixin):
    '''
    Class for LDAP access.
    '''

    cache_key = 'userinfo-%s'

    def __init__(self, server, base):
        self._ldap = ldap.initialize(server)
        self._base = base

    def search_uid(self, uid, attribs=None):
        '''
        Performs uid based search.
        '''
        if attribs is None:
            attribs = ['cn', 'mail', 'ou', 'sn', 'givenName']
        result = self._ldap.search_s(
            self._base,
            ldap.SCOPE_SUBTREE,
            '(mail=%s@novell.com)' % uid,
            attribs)
        if len(result) > 0:
            return result
        return self._ldap.search_s(
            self._base,
            ldap.SCOPE_SUBTREE,
            '(uid=%s)' % uid,
            attribs)

    def fixup_department(self, name):
        '''
        Fixups some common mistakes in department name.
        '''
        if name == 'Business Support Nurenburg':
            return 'Business Support Nürnberg'
        elif name == 'L3 Maintenance':
            return 'L3/Maintenance'

        return name

    def get_department(self, user):
        '''
        Returns user department.
        '''
        department = self._cache_get(user)
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

        self._cache_set(user, department)

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
