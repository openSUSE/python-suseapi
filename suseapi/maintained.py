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
Parser for maintained data.
'''

import os

BASE_DIR = '/work/cd/data/maintained-CDs/'


class MaintainedData(object):
    '''
    Class holding maintained data information.
    '''
    def __init__(self, name, fileobj):
        '''
        Creates object from a file.
        '''
        self.name = name
        self.packages = []
        self.data = {}
        self.load_from_file(fileobj)

    def load_from_file(self, fileobj):
        '''
        Parses maintained data file.
        '''
        package_list = False
        for line in fileobj:
            line = line.strip()
            # Blank line
            if line == '':
                continue
            # Package list
            if package_list:
                self.packages.append(line)
            elif line == 'Packages on CD:':
                package_list = True
            else:
                if line.endswith(':'):
                    key = line[:-1]
                    value = ''
                else:
                    key, value = line.split(': ', 1)
                self.data[key] = value

    def is_maintained(self):
        '''
        Checks whether product is maintained.
        '''
        return (
            (self.data['ProductType'] == 'maintained') and
            (self.data['Distributionstring'] != 'res') and
            not self.data['Distributionstring'].startswith('RES') and
            ('-beta-' not in self.data['Distribution']) and
            ('-beta-' not in self.name) and
            ('sle11-hwrefresh10a' not in self.data['Distribution']) and
            ('sle11-pl11b' not in self.data['Distribution']) and
            ('openSUSE' not in self.data['Distributionstring'])
        )


def get_revision(base_dir=None):
    '''
    Loads SVN revision of maintained data.
    '''
    if base_dir is None:
        base_dir = BASE_DIR

    for svnpath in ('.svn/entries', '.svn-entries'):
        filepath = os.path.join(base_dir, svnpath)
        if os.path.exists(filepath):
            break

    with open(filepath, 'r') as handle:
        lines = handle.readlines()
        version = int(lines[0])
        if version != 10:
            raise ValueError('Not supported SVN format: {0}'.format(version))
        return int(lines[3])


def load_maintained_data(base_dir=None):
    '''
    Loads all maintained data and returs iterator over them.
    '''
    if base_dir is None:
        base_dir = BASE_DIR

    for name in os.listdir(base_dir):

        # Ignore some files
        if name.startswith('.'):
            continue

        fullname = os.path.join(base_dir, name)

        # Skip dirs
        if not os.path.isfile(fullname):
            continue

        # Parse item
        with open(fullname) as fileobj:
            product = MaintainedData(name, fileobj)

        yield product
