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
Absence collection module
'''

from datetime import date, timedelta
import logging
import socket
import re
from suseapi.cacher import CacherMixin, DjangoCacherMixin

DATE_REGEXP = r'\w{3} (\d{4})-(\d{2})-(\d{2})'
DATE_RANGE_MATCH = re.compile(
    r'\s' + DATE_REGEXP + ' - ' + DATE_REGEXP + r'\s*$'
)
DATE_MATCH = re.compile(r'\s' + DATE_REGEXP + r'\s*$')
ABSENCE_MATCH = re.compile(r'(Absent|Vacation|Absence)\s*:\s')


class PresenceError(Exception):
    '''
    Exception raised withing presence checker.
    '''
    def __init__(self, socket_err, host):
        self.socket_err = socket_err
        self.host = host
        super(PresenceError, self).__init__(self, self.__str__())

    def __str__(self):
        return 'Presence error on %s: %s' % (self.host, str(self.socket_err))


def trim_weekends(when, diff=1):
    '''
    Move the day not to be on the weekend in given direction.
    '''
    while when.weekday() in [5, 6]:
        when = when + timedelta(days=diff)
    return when


class Presence(CacherMixin):
    '''
    Class for caching presence data.
    '''
    cache_key_template = 'presence-%s'

    def __init__(self, hosts=None):
        '''
        Creates presence class.
        '''
        if hosts is None:
            self.hosts = [
                ('present.suse.de', False),
                ('bolzano.suse.de', True),
            ]
        else:
            self.hosts = hosts
        super(Presence, self).__init__()
        self.logger = logging.getLogger('suse.presence')

    def _process_data(self, handle, who):
        '''
        Parses response from the server.
        '''
        absences = []
        gather_data = 0
        data = handle.read().decode('utf-8')

        for line in data.splitlines():
            line = line.rstrip()
            match = re.match(r"Login\s*:\s*(%s)\s*$" % who, line)
            if match:
                gather_data = 1
            if re.match(r"-+\s*$", line):
                gather_data = 0
            if gather_data == 1 and ABSENCE_MATCH.match(line):
                gather_data = 2
            if gather_data == 2:
                match = DATE_RANGE_MATCH.search(line)
                if match:
                    from_date = [int(x) for x in match.group(1, 2, 3)]
                    till_date = [int(x) for x in match.group(4, 5, 6)]
                else:
                    match = DATE_MATCH.search(line)
                    if match:
                        from_date = [int(x) for x in match.group(1, 2, 3)]
                        till_date = from_date
                    else:
                        self.logger.error(
                            'unparsable absence data for %s: %s',
                            who, line
                        )
                        continue
                from_date = trim_weekends(date(*tuple(from_date)), 1)
                till_date = trim_weekends(date(*tuple(till_date)), -1)
                absences.append((from_date, till_date))
        return absences

    def _get_presence_data(self, host, who, no_send=False):
        '''
        Gets and parses presence data from single host.
        '''
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Set timeout for 1 second
            sock.settimeout(1)
            sock.connect((host, 9874))
            if not no_send:
                sock.send(who + "\n")
            handle = sock.makefile('rb', 0)
            absences = self._process_data(handle, who)

        except socket.error as error:
            raise PresenceError(error, host)
        finally:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()

        return absences

    def get_presence_data(self, person):
        '''
        Gets complete presence data.
        '''
        absence_list = self.cache_get(person)

        if absence_list is None:
            absence_list = []

            try:
                for hostname, no_send in self.hosts:
                    absence_list.extend(
                        self._get_presence_data(hostname, person, no_send)
                    )

                self.cache_set(person, absence_list)
            except PresenceError as error:
                self.logger.warn('could not get presence data: %s', str(error))

                cached_absence = self.cache_get(person, True)
                if cached_absence is not None:
                    absence_list = cached_absence

        return absence_list

    def is_absent(self, person, when, threshold=0):
        '''
        Checks whether person is absent with caching of presence data.

        threshold - how long the absense should be to be notified
        '''
        absence_list = self.get_presence_data(person)

        for absence in absence_list:
            if when >= absence[0] and when <= absence[1]:
                if (absence[1] - absence[0]) < timedelta(days=threshold):
                    continue
                return absence

        return None


class DjangoPresence(Presence, DjangoCacherMixin):
    '''
    Presence class using Django caching framework.
    '''
