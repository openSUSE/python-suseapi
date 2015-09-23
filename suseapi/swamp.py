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
Wrapper around suds to allow easier access to SWAMP.

Complete documentation is available in doc/source/api/swamp.rst, which can be
processed using sphinx to get full featured documentation.
'''
from suds.client import Client
from suds import WebFault
import re

from suseapi.browser import WebScraper, WebScraperError

SWAMP_URL = 'http://swamp.suse.de:8080/axis/services/swamp?wsdl'

SWAMP_NEW_RE = re.compile(
    r'New Maintenance Issue started, ID: MaintenanceTracker-([0-9]+)'
)

FIELD_ADDITIONAL_BUGZILLA = 'laufzettelset.bugzilla.additional_ids'
FIELD_PACKAGES = 'laufzettelset.packages'
FIELD_DATE = 'laufzettelset.duedate_release'
FIELD_MAINTAINER = 'laufzettelset.roles.maintainer'

# We follow naming convetion of SWAMP API here
# pylint: disable=C0103


class SWAMPError(WebFault):
    '''
    SWAMP SOAP error class.
    '''
    pass


class WebSWAMPError(WebScraperError):
    '''
    Web SWAMPerror class.
    '''
    pass


class SWAMP(object):
    '''
    SWAMP SOAP wrapper class.
    '''
    def __init__(self, user, password, url=SWAMP_URL):
        '''
        Creates new SWAMP accessor instance.
        '''
        self._user = user
        self._password = password
        self._url = url
        self._client = Client(url)

    def _dict2map(self, dictdata):
        '''
        Converts Python dict into Apache map object.
        '''
        result = self._client.factory.create('ns2:Map')
        for item in dictdata:
            mapitem = self._client.factory.create('ns2:mapItem')
            mapitem.key = item
            mapitem.value = dictdata[item]
            # pylint: disable=E1101,E1103
            result.item.append(mapitem)
        return result

    @staticmethod
    def _map2dict(apachemap):
        '''
        Converts Apache map object to standard Python dict.
        '''
        return dict([(item.key, item.value) for item in apachemap.item])

    def _convert_pu_list(self, pulist):
        '''
        Convert product update list from SWAMP hashes to python dict.
        '''
        ret = {}
        if pulist == '':
            return {}
        for i in pulist.item:
            ret[i.key] = self._map2dict(i.value)
        return ret

    def getMethodDoc(self, name):
        '''
        Gets online documentation for method.
        '''
        return self._client.service.getMethodDoc(name)

    def getAllDocs(self):
        '''
        Gets online documentation for all methods.
        '''
        return self._map2dict(self._client.service.getAllDocs())

    def login(self):
        '''
        Logins to SWAMP. (Emulated by doing any password protected access.)
        '''
        self.doGetProperty('SWAMP_VERSION')

    def doGetProperty(self, name):
        '''
        Gets SWAMP property.
        '''
        return self._client.service.doGetProperty(
            name, self._user, self._password
        )

    def getWorkflowInfo(self, wfid):
        '''
        Gets the workflows properties.
        '''
        return self._map2dict(
            self._client.service.getWorkflowInfo(
                wfid, self._user, self._password
            )
        )

    def doGetAllDataPaths(self, wfid):
        '''
        Gets all workflows data paths.
        '''
        return self._client.service.doGetAllDataPaths(
            wfid, self._user, self._password
        )[0]

    def doGetData(self, wfid, path):
        '''
        Gets workflow data bit.
        '''
        return self._client.service.doGetData(
            wfid, path, self._user, self._password
        )

    def doGetAllData(self, wfid):
        '''
        Gets all workflow data bits.
        '''
        data = self._client.service.doGetAllData(
            wfid, self._user, self._password
        )
        if data == '':
            return {}
        return self._map2dict(data)

    def getDataBit(self, wfid, path):
        '''
        Efficient wrapper around doGetAllData and doGetData to get a data bit.
        It first tries to use all data, because getting it takes same time as
        single bit, but the data is cached and reused for next time.
        '''
        alldata = self.doGetAllData(wfid)
        try:
            return alldata[path]
        except KeyError:
            return self.doGetData(wfid, path)

    def doSendData(self, wfid, path, value):
        '''
        Sets data bit in a workflow.

        '''
        self._client.service.doSendData(
            wfid, path, value, self._user, self._password
        )

    def doSendEvent(self, wfid, event):
        '''
        Send event to a workflow.

        '''
        self._client.service.doSendData(
            wfid, event, self._user, self._password
        )

    def doGetPlannedUpdateList(self):
        '''
        Returns a hash map with all active items from list of planned updates.
        '''
        ret = self._client.service.doGetPlannedUpdateList(
            self._user, self._password
        )
        return self._convert_pu_list(ret)

    def doGetPlannedUpdateItem(self, wfid):
        '''
        Returns a sigle item from list of planned updates with given id.
        '''
        ret = self._client.service.doGetPlannedUpdateItem(
            wfid, self._user, self._password
        )
        return self._map2dict(ret)

    def doSearchPlannedUpdateList(self, **kwargs):
        '''
        Returns a hash map with all active items from list of planned updates
        that match the given criterias.
        '''
        args = self._dict2map(kwargs)
        ret = self._client.service.doSearchPlannedUpdateList(
            args, self._user, self._password
        )
        return self._convert_pu_list(ret)

    def doAddPUListItem(self, data):
        '''
        Adds a new item to the list of planned updates.
        '''
        args = self._dict2map(data)
        return self._client.service.doAddPUListItem(
            args, self._user, self._password
        )

    def doRemovePUListItem(self, wfid):
        '''
        Removes a sigle item from list of planned updates with given id.
        (Sets it to inactive)
        '''
        self._client.service.doRemovePUListItem(
            wfid, self._user, self._password
        )

    def doModifyPUListItem(self, wfid, data):
        '''
        Modify a sigle item from list of planned updates with given id.
        You may change packages, bugids and l3ids.
        '''
        data['id'] = wfid
        args = self._dict2map(data)
        return self._client.service.doModifyPUListItem(
            args, self._user, self._password
        )

    def getWorkflowIdList(self, filterstrings):
        '''
        Returns list of matching incidents.
        '''
        args = self._dict2map(filterstrings)
        return self._client.service.getWorkflowIdList(
            args, self._user, self._password
        )


class WebSWAMP(WebScraper):
    '''
    Web based access to SWAMP.
    '''
    def __init__(self, user, password,
                 base='https://swamp.suse.de/webswamp/swamp'):
        super(WebSWAMP, self).__init__(user, password, base)

    def login(self):
        '''
        Performs login to SWAMP.
        '''
        self.request('')
        # pylint: disable=E1102
        self.browser.select_form(name='loginform')
        self.browser['username'] = self.user
        self.browser['password'] = self.password
        response = self.submit()
        data = response.read()
        if 'Logout' not in data:
            raise WebSWAMPError('Failed to login!')

    def create(self, main_bug, extra_bugs, packages, maintainer=None):
        '''
        Creates new maintenance workflow.
        '''
        # It would be better to access form here, but the HTML is
        # so broken, that mechanize can not handle that.
        response = self.request(
            'eventSubmit_doStartBugzillaIssue/true/'
            'action/workflows.MaintenanceTracker.MaintenanceActions',
            bugid=main_bug,
        )
        data = response.read()
        if 'Success' not in data:
            raise WebSWAMPError('Failed to create workflow!')

        # Extract workflow ID
        ids = SWAMP_NEW_RE.findall(data)
        if len(ids) != 1:
            raise WebSWAMPError('Failed to parse workflow ID!')

        # Set some additional attributes
        # pylint: disable=E1102
        self.browser.select_form('dataedit')
        self.browser['field_%s' % FIELD_ADDITIONAL_BUGZILLA] = \
            ','.join([str(bug) for bug in extra_bugs])
        self.browser['field_%s' % FIELD_PACKAGES] = ','.join(packages)
        if maintainer is not None:
            self.browser['field_%s' % FIELD_MAINTAINER] = maintainer
        self.submit()

        return ids[0]

    def edit(self, wfid, release_date=None):
        '''
        Changes workflow attributes.
        '''
        self.request(
            'template/DisplayWorkflow.vm/workflowid/{0}/dataedit/true'.format(
                wfid
            )
        )

        # pylint: disable=E1102
        self.browser.select_form('dataedit')
        if release_date is not None:
            date_str = release_date.strftime('%Y-%m-%d')
            self.browser['field_%s' % FIELD_DATE] = date_str
        self.submit()


def get_django_webswamp(request):
    '''
    Returns SWAMP connection bound to Django request object.
    '''
    swamp = WebSWAMP(
        request.user.username,
        request.session['user_password']
    )
    return swamp
