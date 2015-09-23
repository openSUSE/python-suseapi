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
Helper class for various namings used at SUSE.
'''


def codestream_name(name):
    '''
    Converts codestream name into standard form (as used by SMASH).
    '''
    # Standard replacing magic
    dist = name.upper().replace(
        'SLE12', 'SLE-12'
    ).replace(
        'SLE11', 'SLE-11'
    ).replace(
        'SLE10', 'SLE-10'
    ).replace(
        'SLE9', 'SLE-9'
    ).replace(
        'SLED9', 'SLE-9'
    ).replace(
        'SLED10', 'SLE-10'
    ).replace(
        'SLED11', 'SLE-11'
    ).replace(
        'SLES9', 'SLE-9'
    ).replace(
        'SLES10', 'SLE-10'
    ).replace(
        'SLES11', 'SLE-11'
    ).replace(
        'OES11', 'OES-11'
    ).replace(
        'OES2', 'OES-2'
    ).replace(
        '-UPDATE', ''
    ).replace(
        '-STAGING', ''
    )
    if dist == 'SMT11-SP2':
        return 'SLE-11-SP2-PRODUCTS'

    if dist == 'SLEPOS10':
        return 'SLE-10-SP4'

    if '-' in dist:
        base, end = dist.rsplit('-', 1)
        if end.startswith('PL') or end.startswith('HWREFRESH'):
            dist = '%s-HWRefresh' % base

    return dist


def codestream_base(name):
    '''
    Returns base of a codestream, without servicepack info.
    '''
    if not (name.startswith('SLE-') or name.startswith('OES-')):
        return name
    separator = name.find('-', 4)
    if separator == -1:
        return name
    return name[:separator]
