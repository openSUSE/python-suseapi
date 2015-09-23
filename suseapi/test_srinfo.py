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
Testing of SR info fetcher.
'''

from unittest import TestCase
import httpretty
from suseapi.srinfo import SRInfo

TEST_RESPONSE = '''<?xml version='1.0'?>

  <sr>
    <id><![CDATA[1234567890]]></id>
    <srtype>sr</srtype>
    <cus_account><![CDATA[SOFTWARE]]></cus_account>
    <cus_num><![CDATA[123456789]]></cus_num>
    <cus_firstname><![CDATA[Bar]]></cus_firstname>
    <cus_lastname><![CDATA[Foo]]></cus_lastname>
    <cus_title><![CDATA[Experience]]></cus_title>
    <cus_email><![CDATA[foo.bar@example.com]]></cus_email>
    <cus_phone><![CDATA[1234569789]]></cus_phone>
    <cus_onsitephone><![CDATA[12345689]]></cus_onsitephone>
    <owner><![CDATA[]]></owner>
    <severity><![CDATA[Medium]]></severity>
    <status><![CDATA[Solution Provided]]></status>
    <bdesc><![CDATA[kernel oops]]></bdesc>
    <ddesc><![CDATA[Completely broken

It does not work at all!
]]></ddesc>
    <bug><![CDATA[123456]]></bug>
    <bug_desc><![CDATA[NULL pointer dereference]]></bug_desc>
    <geo><![CDATA[USA]]></geo>
    <hours><![CDATA[24x7]]></hours>
    <contract><![CDATA[Contract]]></contract>
    <service_level><![CDATA[2]]></service_level>
    <created>2013-01-01 21:22:23</created>
    <lastupdate>2013-10-10 20:21:22</lastupdate>
  </sr>

'''


class SRInfoTest(TestCase):
    '''
    Test SR information retrieval.
    '''

    @httpretty.activate
    def test_status(self):
        '''
        Test getting SR status.
        '''
        httpretty.register_uri(
            httpretty.GET,
            'http://kueue.hwlab.suse.de:8080/srstatus/1234567890/',
            body='Closed'
        )
        srinfo = SRInfo()
        self.assertEquals(
            'Closed',
            srinfo.get_status(1234567890)
        )

    @httpretty.activate
    def test_info(self):
        '''
        Test getting SR information.
        '''
        httpretty.register_uri(
            httpretty.GET,
            'http://kueue.hwlab.suse.de:8080/srinfo/1234567890/',
            body=TEST_RESPONSE,
        )
        srinfo = SRInfo()
        info = srinfo.get_info(1234567890)
        self.assertEquals(info['cus_account'], 'SOFTWARE')
        self.assertEquals(info['service_level'], '2')
