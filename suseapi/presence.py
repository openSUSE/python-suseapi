'''
Absence collection module
'''

from datetime import date, timedelta
import logging
import socket
import re
from suseapi.cacher import CacherMixin, DjangoCacherMixin

logger = logging.getLogger('suse.presence')

DATE_REGEXP = r'\w{3} (\d{4})-(\d{2})-(\d{2})'
DATE_RANGE_MATCH = re.compile(
    r'\s' + DATE_REGEXP + ' - ' + DATE_REGEXP + r'\s*$'
)
DATE_MATCH = re.compile(r'\s' + DATE_REGEXP + r'\s*$')
ABSENCE_MATCH = re.compile(r'(Absent|Vacation|Absence)\s*:\s')


class PresenceError(Exception):
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
            handle = sock.makefile('r', 0)
            absences = []
            gather_data = 0
            for line in handle:
                line = line.rstrip()
                match = re.match(r"Login\s*:\s*(%s)\s*$" % who, line)
                if match:
                    gather_data = 1
                if re.match(r"-+\s*$", line):
                    gather_data = 0
                if (gather_data == 1 and ABSENCE_MATCH.match(line)):
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
                            logger.error(
                                'unparsable absence data for %s: %s',
                                who, line
                            )
                            continue
                    from_date = trim_weekends(date(*tuple(from_date)), 1)
                    till_date = trim_weekends(date(*tuple(till_date)), -1)
                    absences.append((from_date, till_date))

            sock.close()
        except socket.error as e:
            raise PresenceError(e, host)

        return absences

    def get_presence_data(self, person):
        '''
        Gets complete presence data.
        '''
        absence_list = self._cache_get(person)

        if absence_list is None:
            absence_list = []
            failure = False

            try:
                absence_list.extend(
                    self._get_presence_data('present.suse.de', person)
                )
            except PresenceError as e:
                logger.warn('could not get presence data: %s', str(e))
                failure = True

            try:
                absence_list.extend(
                    self._get_presence_data('bolzano.suse.de', person, True)
                )
            except PresenceError as e:
                logger.warn('could not get presence data: %s', str(e))
                failure = True

            if failure:
                cached_absence = self._cache_get(person, True)
                if cached_absence is not None:
                    absence_list = cached_absence
            else:
                self._cache_set(person, absence_list)
        return absence_list

    def is_absent(self, person, when, threshold=0):
        '''
        Checks whether person is absent with caching of presence data.

        threshold - how long the absense should be to be notified
        '''
        absence_list = self.get_presence_data(person)

        for absence in absence_list:
            if (when >= absence[0] and when <= absence[1]):
                if (absence[1] - absence[0]) < timedelta(days=threshold):
                    continue
                return absence

        return None


class DjangoPresence(Presence, DjangoCacherMixin):
    '''
    Presence class using Django caching framework.
    '''
    cache_key = 'presence-%s'

    def is_absent(self, person, when, threshold=0):
        if self.is_ignored(person, when):
            return None

        return super(DjangoPresence, self).is_absent(person, when, threshold)

    def is_ignored(self, person, when):
        from users.models import AbsenceIgnore
        from django.contrib.auth.models import User

        user = User.objects.get(username=person)

        return AbsenceIgnore.objects.filter(date=when, agent=user).exists()


if __name__ == '__main__':
    import sys

    presence = Presence()

    print presence.is_absent(sys.argv[1], date.today(), 1)