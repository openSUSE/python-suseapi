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
Testing of browser wrapper.
'''

from unittest import TestCase
import httpretty
import time
import threading
import suseapi.browser
from suseapi.browser import WebScraper, WebScraperError
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

TEST_BASE = 'http://example.net'


class TimeoutHTTPHandler(BaseHTTPRequestHandler):
    """
    HTTP handler to emulate server timeouts.
    """
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", 'text/html')
        self.send_header('Connection', 'close')
        self.end_headers()

        print self.path

        if self.path == '/foo':
            self.wfile.write('<form method="GET" action="/bar" name="test">')
            self.wfile.write('<input type="submit" value="Submit">')
            self.wfile.write('</form>')
        elif self.path == '/bar?':
            time.sleep(1)


class WebSraperTest(TestCase):
    '''
    Tests web sraping.
    '''

    @httpretty.activate
    def test_basic(self):
        '''
        Test basic operation.
        '''
        httpretty.register_uri(
            httpretty.GET,
            '{0}/{1}'.format(TEST_BASE, 'action'),
            body='TEST'
        )
        scraper = WebScraper(None, None, TEST_BASE)
        self.assertEquals(
            'TEST',
            scraper.request('action').read()
        )

    @httpretty.activate
    def test_error(self):
        '''
        Test error handling.
        '''
        httpretty.register_uri(
            httpretty.GET,
            '{0}/{1}'.format(TEST_BASE, '404'),
            status=404
        )
        scraper = WebScraper(None, None, TEST_BASE)
        self.assertRaises(
            WebScraperError,
            scraper.request, '404'
        )

    def test_cookies(self):
        '''
        Test cookie getting and setting.
        '''
        scraper = WebScraper(None, None, TEST_BASE)
        cookies = scraper.get_cookies()
        scraper.set_cookies(cookies)
        self.assertEquals(len(cookies), 0)

    def test_timeout(self):
        '''
        Test timeout handling for stale requests.
        '''
        original_timeout = suseapi.browser.DEFAULT_TIMEOUT
        suseapi.browser.DEFAULT_TIMEOUT = 0.5
        server = HTTPServer(('localhost', 8888), TimeoutHTTPHandler)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = False
        server_thread.start()
        try:
            scraper = WebScraper(None, None, 'http://localhost:8888')
            scraper.request('foo')
            # pylint: disable=E1102
            scraper.browser.select_form(nr=0)
            self.assertRaises(WebScraperError, scraper.submit)
            self.assertRaises(WebScraperError, scraper.request, 'bar?')
        finally:
            suseapi.browser.DEFAULT_TIMEOUT = original_timeout
            server.shutdown()
            server_thread.join()
