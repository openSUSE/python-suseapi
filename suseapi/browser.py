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
import mechanize
import urllib
import urllib2
import httplib
import socket
import cookielib

DEFAULT_TIMEOUT = 5.0


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
        return call(*args, **kwargs)
    except urllib2.URLError as exc:
        for attrname in ('reason', 'msg', 'message'):
            value = getattr(exc, attrname, '')
            if value:
                raise WebScraperError('URL error: {0!s}'.format(value), exc)
        raise WebScraperError('Unknown URL error: {0!s}'.format(exc), exc)
    except httplib.HTTPException as exc:
        raise WebScraperError(
            'HTTP error {0!s}: {1!s}'.format(type(exc).__name__, exc),
            exc
        )
    except socket.error as exc:
        raise WebScraperError('Socket error: {0!s}'.format(exc), exc)
    except IOError as exc:
        raise WebScraperError('IO error: {0!s}'.format(exc), exc)


class TimeoutRequest(mechanize.Request):
    '''
    Request class with defined timeout.
    '''
    def __init__(self, url, data=None, headers=None,
                 origin_req_host=None, unverifiable=False, visit=None,
                 timeout=DEFAULT_TIMEOUT):
        if headers is None:
            headers = {}
        mechanize.Request.__init__(
            self, url, data, headers, origin_req_host,
            unverifiable, visit, timeout
        )
        self.timeout = DEFAULT_TIMEOUT


class WebScraper(object):
    '''
    Web based scraper using mechanize.
    '''
    def __init__(self, user, password, base, useragent=None):
        self.base = base
        self.user = user
        self.password = password

        # Cookie storage
        self.cookiejar = cookielib.CookieJar()
        self.cookie_set = False

        # Browser instance
        self.browser = mechanize.Browser(
            request_class=TimeoutRequest
        )

        # Set cookies
        self.browser.set_cookiejar(self.cookiejar)

        # Log information about HTTP redirects and Refreshes.
        # self.browser.set_debug_redirects(True)

        # Log HTTP response bodies (ie. the HTML, most of the time).
        # self.browser.set_debug_responses(True)

        # Print HTTP headers.
        # self.browser.set_debug_http(True)

        # Ignore robots.txt
        self.browser.set_handle_robots(False)

        # Are we anonymous?
        self.anonymous = (user == '')

        # Identify ourselves
        if useragent is not None:
            self.browser.addheaders = [('User-agent', useragent)]

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
            params = urllib.urlencode(paramlist)
        elif kwargs == {}:
            params = None
        else:
            params = urllib.urlencode(kwargs)
        return webscraper_safely(
            self.browser.open,
            url, params, timeout=DEFAULT_TIMEOUT
        )

    def submit(self):
        '''
        Submits currently selected browser form.
        '''
        return webscraper_safely(
            self.browser.submit,
            request_class=TimeoutRequest
        )

    def set_cookies(self, cookies):
        '''
        Sets cookies needed for access.
        '''
        for cookie in cookies:
            self.cookiejar.set_cookie(cookie)
        self.cookie_set = True

    def get_cookies(self):
        '''
        Returns cookies set in browser.
        '''
        return [cookie for cookie in self.cookiejar]
