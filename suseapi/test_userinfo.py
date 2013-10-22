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

import os
from unittest import TestCase, skipIf

from suseapi.userinfo import DjangoUserInfo

SKIP_NET = 'SKIP_NET_TEST' in os.environ


class UserInfoTest(TestCase):
    @skipIf(SKIP_NET, 'No network access')
    def test_django_department(self):
        userinfo = DjangoUserInfo()
        self.assertEqual(
            'L3/Maintenance',
            userinfo.get_department('mcihar')
        )
        self.assertEqual(
            'L3/Maintenance',
            userinfo.get_department('mcihar@suse.com')
        )
        self.assertEqual(
            'Security team',
            userinfo.get_department('security-team@suse.de')
        )
