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
Testing of presence module connector
'''

from unittest import TestCase

import datetime
import threading

from suseapi.presence import trim_weekends, Presence

RESPONSE = b'''
------------------------------------------------------------
Name       : Michal Cihar
Login      : mcihar
Phone      : +420-284-0
Department : [SUSE-CZ] SUSE LINUX s.r.o.
Position   : Employee
Location   : Tschechien, Room 1.105
Tasks      : Tool Developer MaintenanceSecurity
Absence    : Fri 2013-10-25 - Mon 2013-10-28
             Fri 2013-11-11
             Tue 2013-12-24 - Tue 2013-12-31
------------------------------------------------------------
'''

# One of those imports has to fail
# pylint: disable=F0401
try:
    import SocketServer
except ImportError:
    import socketserver as SocketServer


class MyTCPHandler(SocketServer.BaseRequestHandler):
    '''
    Simple handler to report presence.
    '''

    def handle(self):
        '''
        Send out mock response.
        '''
        self.request.sendall(RESPONSE)


def start_test_server():
    """
    Starts test server.
    """
    SocketServer.TCPServer.allow_reuse_address = True
    server = SocketServer.TCPServer(('127.0.0.1', 9874), MyTCPHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = False
    server_thread.start()
    return server, server_thread


def stop_test_server(server, server_thread):
    """
    Shutdowns the testing server.
    """
    server.shutdown()
    server_thread.join()


class PresenceTest(TestCase):
    '''
    Presence testing.
    '''

    def test_trim_weekends(self):
        '''
        Test for weekend trimming.
        '''
        self.assertEqual(
            datetime.date(2013, 7, 15),
            trim_weekends(datetime.date(2013, 7, 13)),
        )
        self.assertEqual(
            datetime.date(2013, 7, 12),
            trim_weekends(datetime.date(2013, 7, 13), -1),
        )
        self.assertEqual(
            datetime.date(2013, 7, 15),
            trim_weekends(datetime.date(2013, 7, 15)),
        )

    def test_presence(self):
        '''
        Test for presence retrieving.
        '''
        presence = Presence([('127.0.0.1', True)])
        server = start_test_server()
        try:

            self.assertTrue(
                presence.is_absent('mcihar', datetime.date(2013, 7, 15))
                is None
            )
            self.assertFalse(
                presence.is_absent('mcihar', datetime.date(2013, 10, 28))
                is None
            )
        finally:
            stop_test_server(*server)
