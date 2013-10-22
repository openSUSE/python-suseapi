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
Helper functions for write access to Bugzilla.
'''
import traceback
from suseapi.bugzilla import APIBugzilla


class DjangoBugzilla(APIBugzilla):
    '''
    Adds Django specific things to bugzilla class.
    '''
    def _log_parse_error(self, bugid, data):
        '''
        Sends email to admin on error.
        '''
        from django.core.mail import mail_admins
        subject = 'Error while fetching %s' % bugid
        message = 'Exception:\n\n%s\n\n\nData:\n\n%s\n' % (
            traceback.format_exc(),
            data,
        )
        mail_admins(subject, message, fail_silently=True)
        super(DjangoBugzilla, self).log_parse_error(bugid, data)


def get_bugzilla():
    '''
    Returns logged in bugzilla object. Access cookies are stored in django
    cache.
    '''
    from django.core.cache import cache
    from django.conf import settings
    bugzilla = DjangoBugzilla(
        settings.BUGZILLA_USERNAME,
        settings.BUGZILLA_PASSWORD,
        useragent=settings.EMAIL_SUBJECT_PREFIX.strip('[] '),
        timeout=settings.BUGZILLA_TIMEOUT
    )

    # Check for anonymous access
    if settings.BUGZILLA_USERNAME == '':
        return bugzilla

    cookies = cache.get('bugzilla-access-cookies')

    if cookies is None:
        bugzilla.login()
        cache.set('bugzilla-access-cookies', bugzilla.get_cookies())
    else:
        bugzilla.set_cookies(cookies)

    return bugzilla
