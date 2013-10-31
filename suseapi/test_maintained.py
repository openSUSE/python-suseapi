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
Testing of maintained data parser.
'''

from unittest import TestCase
from cStringIO import StringIO

from suseapi.maintained import MaintainedData


DATA_1 = '''
Distribution: 12.1-i586
Distributionstring: openSUSE-i386
Distributionversion: 12.1-0
CD-Produkt-Name: openSUSE
CD-Produkt-Version: 12.1
Marketing-Name: openSUSE 12.1
NPP-Id: 35843
ProductType: box
FTPServerName: ftp.opensuse.org
Master-Date: 1269000000
YOUPathIncludesArch: yes
PackTrack: BOX/openSUSE-12.1-POOL
PatchfileNaming: sat
PatchRpms: deltaonly
PublicTest: yes
MarkFinished: upload-buildservice
ChecksummedFilenames: yes
BuildServiceMaintained: yes

Packages on CD:
844-ksc-pcf
CID-keyed-fonts-MOE
CID-keyed-fonts-Munhwa
CID-keyed-fonts-Wada
CID-keyed-fonts-WadaH
'''

DATA_2 = '''
Distribution: sle11-sp2-x86_64
Distributionstring: SLES-11-SP2-x86_64
Distributionversion: 11-0
CD-Produkt-Name: SLE SERVER
CD-Produkt-Version: 11-SP2
Marketing-Name: SUSE Linux Enterprise Server 11 SP2
NPP-Id: 36426
ProductType: maintained
FTPServerName: zypp-patches.suse.de
Master-Date: 1273000000
YOUPathIncludesArch: yes
PackTrack: SLES11/SLES-11-SP2-x86_64
PatchfilePrefix: slessp2
PatchfileNaming: sat
PatchRpms: deltaonly
KWDFile: /work/cd/data/supportstatus/SUSE_SLES-11.2
PB-Entitlement: server-x86-updates--NR,NovellEmployeeFlag--NR,PartnerNetOnlineUpdates--NR,TSFiles-Suse-Patches--NR
PB-Family: SUSE Linux Enterprise Server
PB-Product: SUSE Linux Enterprise Server 11 SP2
PB-System: SUSE LINUX Enterprise Server 11
PB-Arch: x86-64
MarkFinishedTest: upload-kmpbuild
MarkFinished: upload-build

Packages on CD:
Mesa
ModemManager
NetworkManager
NetworkManager-glib
NetworkManager-gnome
'''

class PresenceTest(TestCase):
    def test_1(self):
        fileobj = StringIO(DATA_1)
        maintained = MaintainedData('opensuse', fileobj)
        self.assertFalse(maintained.is_maintained())

    def test_2(self):
        fileobj = StringIO(DATA_2)
        maintained = MaintainedData('sles', fileobj)
        self.assertTrue(maintained.is_maintained())
