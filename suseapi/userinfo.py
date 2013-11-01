# -*- coding: UTF-8 -*-
'''
Simple wrapper around LDAP module to allow easier search.
'''

import ldap
from suseapi.cacher import CacherMixin, DjangoCacherMixin


DEPARTMENT_FIXUPS = {
    'Business Support Nurenburg': 'Business Support Nürnberg',
    'L3 Maintenance': 'L3/Maintenance',
}


class UserInfo(CacherMixin):
    '''
    Class for LDAP access.
    '''

    cache_key = 'userinfo-%s'

    searches = [
        '(mail={0}@novell.com)',
        '(mail={0}@suse.com)',
        '(uid={0})',
        '(cn={0})',
    ]

    def __init__(self, server, base):
        self._ldap = ldap.initialize(server)
        self._base = base

    def search_uid(self, uid, attribs=None):
        '''
        Performs uid based search.
        '''
        if attribs is None:
            attribs = ['cn', 'mail', 'ou', 'sn', 'givenName']

        for search in self.searches:
            filterstring = search.format(uid)
            result = self._ldap.search_s(
                self._base,
                ldap.SCOPE_SUBTREE,
                filterstring,
                attribs
            )
            if len(result) > 0:
                return result
        return []

    def fixup_department(self, name):
        '''
        Fixups some common mistakes in department name.
        '''
        if name in DEPARTMENT_FIXUPS:
            return DEPARTMENT_FIXUPS[name]

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
