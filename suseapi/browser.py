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
Web browser wrapper for convenient scraping of web based services.
'''
# import mechanize
import grab
# pylint: disable=import-error
from six.moves.urllib.parse import urlencode
# pylint: disable=import-error
from six.moves.urllib.error import URLError
# pylint: disable=import-error
from six.moves.http_client import HTTPException
import socket

# The default timeout has to be an integer.
DEFAULT_TIMEOUT = 5


class WebScraperError(Exception):
    '''
    Web scraper error class.
    '''
    def __init__(self, message, original=None):
        super(WebScraperError, self).__init__(message)
        self.original = original


def webscraper_safely(call, *args, **kwargs):
    '''
    Wrapper to handle errors in HTTP requests.
    '''
    try:
        result = call(*args, **kwargs)
        if result.code >= 400:
            raise WebScraperError('Status code error: {0!s}'.format(
                result.code
            ), result)
        return result
    except grab.error.GrabError as exc:
        raise WebScraperError('Grab error occurred: {0!s}'.format(exc), exc)
    except URLError as exc:
        for attrname in ('reason', 'msg', 'message'):
            value = getattr(exc, attrname, '')
            if value:
                raise WebScraperError('URL error: {0!s}'.format(value), exc)
        raise WebScraperError('Unknown URL error: {0!s}'.format(exc), exc)
    except HTTPException as exc:
        raise WebScraperError(
            'HTTP error {0!s}: {1!s}'.format(type(exc).__name__, exc),
            exc
        )
    except socket.error as exc:
        raise WebScraperError('Socket error: {0!s}'.format(exc), exc)
    # There doesn't seem to be an oserror that is already caught here?
    except IOError as exc:  # pylint: disable=duplicate-except
        raise WebScraperError('IO error: {0!s}'.format(exc), exc)


class WebScraper(object):
    '''
    Web based scraper using mechanize.
    '''
    def __init__(self, user, password, base, useragent=None):
        self.base = base
        self.user = user
        self.password = password

        self.cookie_set = False

        # Browser instance
        self.browser = grab.Grab(
            timeout=DEFAULT_TIMEOUT, transport="urllib3"
        )
        # Grab automatically handles cookies.

        # Are we anonymous?
        self.anonymous = (user == '')

        # Identify ourselves
        if useragent is not None:
            self.browser.setup(headers={'User-agent': useragent})

    def _get_req_url(self, action):
        '''
        Formats request URL based on action.
        '''
        return '%s/%s' % (self.base, action)

    def request(self, action, paramlist=None, **kwargs):
        '''
        Performs single request on a server (loads single page).
        '''
        url = self._get_req_url(action)
        if paramlist is not None:
            params = urlencode(paramlist)
        elif kwargs == {}:
            params = None
        else:
            params = urlencode(kwargs)
        return webscraper_safely(
            self.browser.go,
            url, post=params
        )

    def submit(self):
        '''
        Submits currently selected browser form.
        '''
        return webscraper_safely(
            self.browser.submit,
        )

    def set_cookies(self, cookies):
        '''
        Sets cookies needed for access.
        '''
        for cookie in cookies:
            self.browser.cookies.set(cookie.name, cookie.value)
        self.cookie_set = True

    def get_cookies(self):
        '''
        Returns cookies set in browser.
        '''
        return [cookie for cookie in self.browser.cookies.cookiejar]

    def viewing_html(self):
        if not self.browser.doc:
            return False
        return 'text/html' in self.browser.doc.headers['Content-Type']
