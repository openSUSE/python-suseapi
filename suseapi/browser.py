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
Web browser wrapper for convenient scraping of web based services.
'''
import mechanize
import urllib
import urllib2
import httplib
import socket
import cookielib


class TimeoutBrowser(mechanize.Browser):
    '''
    Browser with fixed timeout.
    '''

    def __init__(self,
                 factory=None,
                 history=None,
                 request_class=None,
                 timeout=10,
                 ):
        '''
        Creates browser object.
        '''
        mechanize.Browser.__init__(self, factory, history, request_class)
        self._forced_timeout = timeout

    def _request(self, url_or_req, data, visit, timeout=None):
        '''
        Forces timeout to _request method.
        '''
        if hasattr(url_or_req, 'timeout'):
            url_or_req.timeout = self._forced_timeout
        return mechanize.Browser._request(
            self, url_or_req, data, visit, self._forced_timeout
        )


class WebScraperError(Exception):
    '''
    Web scaper class.
    '''
    pass


class WebScraper(object):
    '''
    Web based scraper using mechanize.
    '''
    def __init__(self, user, password, base, useragent=None, timeout=10):
        self.base = base
        self.user = user
        self.password = password

        # Cookie storage
        self.cookiejar = cookielib.CookieJar()

        # Browser instance
        self.browser = TimeoutBrowser(timeout=timeout)

        # Set cookies
        self.browser.set_cookiejar(self.cookiejar)

        # Log information about HTTP redirects and Refreshes.
        #self.browser.set_debug_redirects(True)

        # Log HTTP response bodies (ie. the HTML, most of the time).
        #self.browser.set_debug_responses(True)

        # Print HTTP headers.
        #self.browser.set_debug_http(True)

        # Ignore robots.txt
        self.browser.set_handle_robots(False)

        # Are we anonymous?
        self.anonymous = (user == '')

        # Identify ourselves
        if useragent is not None:
            self.browser.addheaders = [('User-agent', useragent)]

    def _safely(self, call, *args, **kwargs):
        '''
        Wrapper to handle errors in HTTP requests.
        '''
        try:
            return call(*args, **kwargs)
        except urllib2.URLError as exc:
            for attrname in ('reason', 'msg', 'message'):
                if hasattr(exc, attrname):
                    raise WebScraperError(getattr(exc, attrname))
            raise WebScraperError('Unknown url error (%s)' % str(exc))
        except httplib.BadStatusLine as exc:
            raise WebScraperError('Bad status line (%s)' % str(exc))
        except socket.error as exc:
            raise WebScraperError('Socket error: %s' % str(exc))
        except IOError as exc:
            raise WebScraperError('IO error: %s' % str(exc))

    def _get_req_url(self, action):
        '''
        Formats request URL based on action.
        '''
        return '%s/%s' % (self.base, action)

    def request(self, action, paramlist=None, **kwargs):
        '''
        Performs single request on SWAMP (loads single page).
        '''
        url = self._get_req_url(action)
        if paramlist is not None:
            params = urllib.urlencode(paramlist)
        elif kwargs == {}:
            params = None
        else:
            params = urllib.urlencode(kwargs)
        return self._safely(self.browser.open, url, params)

    def _submit(self):
        '''
        Submits currently selected browser form.
        '''
        return self._safely(self.browser.submit)

    def set_cookies(self, cookies):
        '''
        Sets cookies needed for access.
        '''
        for cookie in cookies:
            self.cookiejar.set_cookie(cookie)

    def get_cookies(self):
        '''
        Returns cookies set in browser.
        '''
        return [cookie for cookie in self.cookiejar]
