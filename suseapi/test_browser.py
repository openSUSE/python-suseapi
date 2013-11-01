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
Testing of Bugzilla connector
'''

from unittest import TestCase
import httpretty
from suseapi.browser import WebScraper, WebScraperError

TEST_BASE = 'http://example.net'


class WebSraperTest(TestCase):
    @httpretty.activate
    def test_basic(self):
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
        scraper = WebScraper(None, None, TEST_BASE)
        cookies = scraper.get_cookies()
        scraper.set_cookies(cookies)
        self.assertEquals(len(cookies), 0)
