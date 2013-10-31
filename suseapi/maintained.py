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
Parser for maintained data.
'''

class MaintainedData(object):
    '''
    Class holding maintained data information.
    '''
    def __init__(self, fileobj):
        '''
        Creates object from a file.
        '''
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
            (self.data['ProductType'] == 'maintained')
            and (self.data['Distributionstring'] != 'res')
            and not self.data['Distributionstring'].startswith('RES')
            and ('-beta-' not in self.data['Distribution'])
            and ('sle11-hwrefresh10a' not in self.data['Distribution'])
            and ('sle11-pl11b' not in self.data['Distribution'])
            and ('openSUSE' not in self.data['Distributionstring'])
        )
