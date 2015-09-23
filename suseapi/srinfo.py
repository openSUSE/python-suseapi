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
SR information fetcher.
'''

import urllib2
import xml.etree.cElementTree
import dateutil.parser
import suseapi

SRINFO_SERVER = 'http://kueue.hwlab.suse.de:8080/'


class SRInfo(object):
    '''
    Class for accessing SR information.
    '''
    def __init__(self):
        self.opener = urllib2.build_opener()
        self.opener.addheaders = [
            ('User-agent', suseapi.USER_AGENT),
        ]

    def req(self, operation, srid):
        '''
        Wrapper for invoking requests.
        '''
        return self.opener.open(
            '{0}{1}/{2}/'.format(SRINFO_SERVER, operation, srid),
            None,
            20
        )

    def get_status(self, srid):
        '''
        Returns string with SR status.
        '''
        response = self.req('srstatus', srid)
        return response.read()

    def get_info(self, srid):
        '''
        Return dictionary with SR information.
        '''
        response = self.req('srinfo', srid)
        data = response.read()

        # Check for invalid ID
        if data == 'No SR number':
            return None

        # Parse XML
        parsed = xml.etree.cElementTree.fromstring(data)

        # Grab fields
        result = {}
        date_fields = (
            'lastupdate',
            'created',
        )
        for item in parsed:
            if item.text is None:
                continue
            if item.tag in date_fields:
                result[item.tag] = dateutil.parser.parse(item.text)
            else:
                result[item.tag] = item.text

        return result


class DjangoSRInfo(SRInfo):
    '''
    Django wrapper for SR info, setting user-agent.
    '''
    def __init__(self):
        super(DjangoSRInfo, self).__init__()
        from django.conf import settings
        self.opener.addheaders = [
            ('User-agent', settings.EMAIL_SUBJECT_PREFIX.strip('[] '))
        ]
