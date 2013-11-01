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
Generic access to Novell Bugzilla.

It uses XML to load the data (when applicable) and HTML forms to update it.
'''

import urlparse
from xml.etree import cElementTree as ElementTree
import dateutil.parser
import traceback
import re
import logging
from mechanize import (
    LinkNotFoundError, FormNotFoundError, ControlNotFoundError
)
from BeautifulSoup import BeautifulSoup

from suseapi.browser import WebScraper, WebScraperError

logger = logging.getLogger('suse.bugzilla')

SR_MATCH = re.compile(r'\[(\d+)\]')


class BugzillaError(WebScraperError):
    '''Generic error'''
    def __init__(self, error, bug_id=None):
        super(BugzillaError, self).__init__()
        self.bug_id = bug_id
        self.error = error

    def __str__(self):
        if self.bug_id is not None:
            return "%s: %s: %s" % (self.__doc__, self.error, self.bug_id)
        else:
            return "%s: %s" % (self.__doc__, self.error)


class BugzillaNotPermitted(BugzillaError):
    '''Access not permitted'''
    pass


class BugzillaNotFound(BugzillaError):
    '''Bug was not found'''
    pass


class BugzillaInvalidBugId(BugzillaError):
    '''Bug Id is invalid'''
    pass


class BugzillaConnectionError(BugzillaError):
    '''Connection related error'''
    pass


class BugzillaLoginFailed(BugzillaConnectionError):
    '''Login has failed'''
    pass


class BuglistTooLarge(BugzillaError):
    '''Search returned too many entries'''
    pass


class BugzillaUpdateError(BugzillaConnectionError):
    '''Error while updating bug'''
    pass


def escape_xml_text(data):
    '''
    Fix some XML errors in bugzilla xml, which confuse proper XML parser.
    '''
    data = data.replace('', '^H')
    data = data.replace('', '^S')
    data = data.replace('', '^A')
    data = data.replace('', '^G')
    return data


class Bug(object):
    '''
    Class holding bug information.
    '''
    def __init__(self, bug_et, anonymous=False):
        error = bug_et.get('error')
        if error is not None:
            bug_id = bug_et.find("bug_id")
            if bug_id is not None:
                bug_id = bug_id.text
            if error == 'NotPermitted':
                raise BugzillaNotPermitted(error, bug_id)
            if error == 'NotFound':
                raise BugzillaNotFound(error, bug_id)
            if error == 'InvalidBugId':
                raise BugzillaInvalidBugId(error, bug_id)
            raise BugzillaError(error)
        self.cc_list = []
        self.groups = []
        self.comments = []
        self.attachments = []
        self.aliases = []
        self.delta_ts = None
        self.creation_ts = None
        self.anonymous = anonymous
        for element in bug_et.getchildren():
            self.process_element(element)

    def has_nonempty(self, name):
        '''
        Checks whether object has nonempty attribute.
        '''
        value = getattr(self, name, None)
        return value is not None and value != ''

    def process_element(self, element):
        '''
        Parses data from element tree instance and stores them within
        this object.
        '''
        if element.tag == 'cc':
            self.cc_list.append(element.text)
        elif element.tag == 'alias':
            self.aliases.append(element.text)
        elif element.tag == 'group':
            self.groups.append(element.text)
        elif element.tag == 'creation_ts':
            self.creation_ts = dateutil.parser.parse(element.text)
        elif element.tag == 'delta_ts':
            self.delta_ts = dateutil.parser.parse(element.text)
        elif len(element.getchildren()) == 0:
            setattr(self, element.tag, element.text)
        elif element.tag == 'long_desc':
            self.process_comment(element)
        elif element.tag == 'attachment':
            self.process_attachment(element)

    def process_attachment(self, element):
        '''
        Stores attachment data within this object.
        '''
        self.attachments.append({
            'attachid': element.find('attachid').text,
            'desc': element.find('desc').text,
            'date': dateutil.parser.parse(element.find('date').text),
            'filename': element.find('filename').text,
            'type': element.find('type').text,
            'size': element.find('size').text,
            'attacher': element.find('attacher').text,
            'ispatch': element.get('ispatch', '0') == '1',
            'isobsolete': element.get('isobsolete', '0') == '1',
        })

    def process_comment(self, element):
        '''
        Stores commend data within this object.
        '''
        try:
            bug_id = self.bug_id
        except:
            bug_id = None

        who_elm = element.find('who')
        if who_elm is None:
            if not self.anonymous:
                raise BugzillaNotPermitted(
                    'Could not load author from bugzilla', bug_id
                )
            else:
                who = ''
        else:
            who = who_elm.text

        when_elm = element.find('bug_when')
        if when_elm is None:
            if not self.anonymous:
                raise BugzillaNotPermitted(
                    'Could not load time of change from bugzilla', bug_id
                )
            else:
                when = None
        else:
            when = dateutil.parser.parse(when_elm.text)

        self.comments.append({
            'who': who,
            'bug_when': when,
            'thetext': element.find('thetext').text,
        })


class Bugzilla(WebScraper):
    '''
    Class for access to Novell bugzilla.
    '''
    def __init__(self, user, password, base='https://bugzilla.novell.com',
                 useragent=None, timeout=10):
        super(Bugzilla, self).__init__(
            user, password, base, useragent, timeout
        )

    def check_login(self):
        '''
        Check whether we're logged in.
        '''
        logger.info('Getting login page')
        self.request('index', GoAheadAndLogIn=1)

        if not self.browser.viewing_html():
            raise BugzillaLoginFailed('Failed to load bugzilla login form')

        try:
            self.browser.find_link(text='Log\xc2\xa0out')
            logger.info('Already logged in')
            return True
        except LinkNotFoundError:
            return False

    def login(self):
        '''
        Login to Bugzilla using Access Manager.
        '''
        if self.check_login():
            return

        # Submit fake javascript form
        try:
            self.browser.select_form(nr=0)
        except FormNotFoundError:
            raise BugzillaUpdateError('Failed to parse HTML for login!')
        response = self._submit()

        # Find the login form
        try:
            self.browser.select_form(nr=0)
        except FormNotFoundError:
            raise BugzillaUpdateError('Failed to parse HTML for login!')

        try:
            self.browser['Ecom_User_ID'] = self.user
            self.browser['Ecom_Password'] = self.password
        except ControlNotFoundError:
            raise BugzillaUpdateError('Failed to parse HTML for login!')

        logger.info('Doing login')
        response = self._submit()

        text = response.read()

        # Check for error messages
        soup = BeautifulSoup(text)
        for para in soup.findAll('p'):
            if para.get('class') == 'error':
                raise BugzillaLoginFailed(para.text)

        # Emulate javascript redirect
        for script in soup.findAll('script'):
            for line in script.text.splitlines():
                line = line.strip()
                if line.startswith('top.location.href='):
                    path = line.split("'")[1]
                    newpath = urlparse.urljoin(
                        response.geturl(),
                        path
                    )
                    response = self.request(newpath)

        if not self.check_login():
            raise BugzillaLoginFailed(
                'Failed to verify login after successful login'
            )

    def _get_req_url(self, action):
        '''
        Formats request URL based on action.
        '''
        if action.startswith('http'):
            return action
        else:
            return self.base + '/' + action + '.cgi'

    def _handle_parse_error(self, bugid, data):
        '''
        Handles invalid output received from bugzilla.
        '''

        if data.find('Buglist Too Large') != -1:
            raise BuglistTooLarge('Buglist too large')

        if data.find('Bugzilla has suffered an internal error.'):
            raise BugzillaError('Bugzilla has suffered an internal error.')

        if data == '':
            raise BugzillaError('Received empty response from Bugzilla.')

        self.log_parse_error(bugid, data)

    def log_parse_error(self, bugid, data):
        '''
        Logs information about parse error.
        '''
        if data.startswith('<!DOCTYPE html'):
            logger.error('Got HTML instead of from bugzilla for bug %s', bugid)
        else:
            logger.error(
                'Failed to parse XML response from bugzilla for bug %s: %s',
                bugid,
                traceback.format_exc()
            )

    def get_bug(self, bugid, retry=True):
        '''
        Returns Bug object based on data received from bugzilla.

        Returns None in case of failure.
        '''
        result = self.get_bugs([bugid], retry)
        if len(result) == 0:
            return None
        return result[0]

    def get_bugs(self, ids, retry=True, permissive=False):
        '''
        Returns Bug objects based on data received from bugzilla for each bug
        ID.

        Returns empty list in case of some problems.
        '''
        # Generate request query
        req = [('id', bugid) for bugid in ids if bugid is not None]
        req += [('ctype', 'xml'), ('excludefield', 'attachmentdata')]

        # Download data
        data = self.request('show_bug', paramlist=req).read()

        # Fixup XML errors bugzilla produces
        data = escape_xml_text(data)

        # Parse XML
        try:
            response_et = ElementTree.fromstring(data)
        except:
            self._handle_parse_error(
                ','.join([str(bugid) for bugid in ids]),
                data
            )
            return []
        try:
            bugs = []
            for bug in response_et.findall('bug'):
                try:
                    bugs.append(Bug(bug, self.anonymous))
                except BugzillaError as exc:
                    if permissive:
                        logger.error(exc)
                    else:
                        raise exc
            return bugs
        except BugzillaNotPermitted as exc:
            if retry and not self.anonymous:
                logger.error("%s - login and retry", exc)
                self.login()
                return self.get_bugs(ids, False, permissive)
            raise exc

    def do_search(self, params):
        '''
        Performs search and returns list of IDs.
        '''
        req = [('ctype', 'atom')] + params
        logger.info('Doing bugzilla search: %s', req)
        data = self.request('buglist', paramlist=req).read()
        data = escape_xml_text(data)
        try:
            response_et = ElementTree.fromstring(data)
        except:
            self._handle_parse_error('recent', data)
            return []

        id_query = '{http://www.w3.org/2005/Atom}id'
        entry_query = '{http://www.w3.org/2005/Atom}entry'

        bugs = [
            bug.find(id_query).text for bug in response_et.findall(entry_query)
        ]

        # Strip http://bugzilla.novell.com/show_bug.cgi?id=
        return [int(bugid[bugid.find("?id=") + 4:]) for bugid in bugs]

    def get_recent_bugs(self, startdate):
        '''
        Returns lis of bugs changed since start date.
        '''
        return self.do_search([
            ('chfieldto', 'Now'),
            ('chfieldfrom', startdate.strftime('%Y-%m-%d %H:%M:%S +0000'))
        ])

    def get_openl3_bugs(self):
        '''
        Searches for bugs with openL3 in whiteboard.
        '''
        return self.do_search([
            ('status_whiteboard_type', 'allwordssubstr'),
            ('query_format', 'advanced'),
            ('status_whiteboard', 'openL3')
        ])

    def get_l3_summary_bugs(self):
        '''
        Searches for open bugs with L3: in summary.
        '''
        return self.do_search([
            ('short_desc', 'L3:'),
            ('query_format', 'advanced'),
            ('bug_status', 'NEW'),
            ('bug_status', 'ASSIGNED'),
            ('bug_status', 'NEEDINFO'),
            ('bug_status', 'REOPENED'),
            ('short_desc_type', 'allwordssubstr')
        ])

    def get_sr(self, bugid):
        '''
        Black magic to obtain SR ids from bugzilla.
        '''
        # Load the form
        logger.info('Loading bug page for %d', bugid)
        self.request('show_bug', id=bugid)
        if not self.browser.viewing_html():
            raise BugzillaUpdateError('Failed to load bugzilla form')

        # Find link containing SR ids
        try:
            link = self.browser.find_link(text='Report View')
        except LinkNotFoundError:
            return []

        # Split parts (URL encoded)
        urlpart = [x for x in link.url.split('%26') if x[:7] == 'lsMSRID']

        if len(urlpart) == 0:
            return []

        # Find SR ids
        match = SR_MATCH.findall(urlpart[0])

        # Convert to integers
        return [int(x) for x in match]

    def update_bug(self, bugid, callback=None, callback_param=None,
                   whiteboard_add=None, whiteboard_remove=None, **kwargs):
        '''
        Updates bugzilla.
        '''
        if self.anonymous:
            raise BugzillaUpdateError('No updates in anonymous mode!')

        # Load the form
        logger.info('Loading bug form for %d', bugid)
        data = self.request('show_bug', id=bugid)
        if 'You are not authorized to access bug' in data.read():
            raise BugzillaNotPermitted(
                'You are not authorized to access bug #%d.' % bugid
            )
        if not self.browser.viewing_html():
            raise BugzillaUpdateError('Failed to load bugzilla form')

        changes = False

        # Find the form
        try:
            self.browser.select_form(name="changeform")
        except FormNotFoundError:
            raise BugzillaUpdateError('Failed to parse HTML to update bug!')

        # Set parameters
        for k in kwargs:
            val = kwargs[k]
            if type(val) == unicode:
                val = val.encode('utf-8')
            self.browser[k] = val
            changes = True

        # Callback can adjust data on fly
        if callback is not None:
            changes |= callback(self.browser, callback_param)

        # Whiteboard manipulations
        if whiteboard_add is not None or whiteboard_remove is not None:
            changes |= self._update_bug_whiteboard(
                self.browser,
                whiteboard_remove,
                whiteboard_add
            )

        # Retrun on no changes
        if not changes:
            return

        # Submit
        resp = self._submit()
        data = resp.read()
        if data.find('Mid-air collision!') != -1:
            raise BugzillaUpdateError('Mid-air collision!')
        if data.find('Changes submitted for') == -1:
            raise BugzillaUpdateError('Unknown error while submitting form')

    def _update_bug_whiteboard(self, browser, remove, add):
        '''
        Callback for changing bug whiteboard.
        '''
        whiteboard = browser['status_whiteboard']

        if remove is not None and remove in whiteboard:
            whiteboard = whiteboard.replace(remove, '')

        if add is not None and add not in whiteboard:
            whiteboard = '%s %s' % (whiteboard, add)

        changes = (browser['status_whiteboard'] != whiteboard)

        browser['status_whiteboard'] = whiteboard

        # Do not add ourselves to cc
        try:
            browser['addselfcc'] = []
        except ValueError:
            pass

        return changes


class APIBugzilla(Bugzilla):
    '''
    Wrapper class to use apibugzilla.novell.com.
    '''
    def __init__(self, user, password, base='https://apibugzilla.novell.com',
                 useragent=None, timeout=10):
        super(APIBugzilla, self).__init__(
            user, password, base, useragent, timeout
        )
        # Use normal Bugzilla for anonymous access
        if self.anonymous and 'novell.com' in base:
            self.base = 'https://bugzilla.novell.com'
        else:
            self.browser.add_password(base + '/', user, password)

    def login(self):
        '''
        Checks login to Bugzilla using HTTP authentication.
        '''
        logger.info('Getting login page')
        self.request('index', GoAheadAndLogIn=1)

        if not self.browser.viewing_html():
            raise BugzillaLoginFailed('Failed to load bugzilla login form')

        try:
            self.browser.find_link(text='Log\xc2\xa0out')
            logger.info('Already logged in')
            return
        except LinkNotFoundError:
            raise BugzillaLoginFailed('Failed to login to bugzilla')


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


def get_django_bugzilla():
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
