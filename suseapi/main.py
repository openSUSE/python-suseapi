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
Command line interface for suseapi.
'''
from __future__ import print_function

import sys
from xdg.BaseDirectory import load_config_paths
from pprint import pformat
from argparse import ArgumentParser
from ConfigParser import RawConfigParser

from suseapi.userinfo import UserInfo
from suseapi.presence import Presence
import suseapi


COMMANDS = {}


def register_command(command):
    """
    Decorator to register command in command line interface.
    """
    COMMANDS[command.name] = command
    return command


class SuseAPIConfig(RawConfigParser):
    """
    Configuration parser wrapper with defaults.
    """
    def __init__(self):
        RawConfigParser.__init__(self)
        # Set defaults
        self.add_section('ldap')
        self.add_section('presence')
        self.set('ldap', 'server', 'ldap://pan.suse.de')
        self.set('ldap', 'base', 'o=Novell')
        self.set(
            'presence', 'servers', 'present.suse.de,bolzano.suse.de/nosend'
        )

    def load(self):
        """
        Loads configuration from XDG paths.
        """
        self.read(load_config_paths('suseapi'))


def get_parser():
    """
    Creates argument parser.
    """
    parser = ArgumentParser()
    subparser = parser.add_subparsers(dest="cmd")

    for command in COMMANDS:
        COMMANDS[command].add_parser(subparser)

    return parser


class Command(object):
    """
    Basic command object.
    """
    name = ''
    description = ''

    def __init__(self, args, config, stdout=None):
        self.args = args
        self.config = config
        if stdout is None:
            self.stdout = sys.stdout
        else:
            self.stdout = stdout

    @classmethod
    def add_parser(cls, subparser):
        """
        Creates parser for command line.
        """
        return subparser.add_parser(
            cls.name, description=cls.description
        )

    def println(self, line):
        """
        Prints single line to output.
        """
        print(line, file=self.stdout)

    def run(self):
        """
        Main execution of the command.
        """
        raise NotImplementedError


@register_command
class Version(Command):
    """
    Prints version.
    """
    name = 'version'
    description = "Prints program version"

    def run(self):
        self.println(suseapi.__version__)


@register_command
class LookupUser(Command):
    """
    User lookup command.
    """
    name = 'lookup-user'
    description = "Look up a user in LDAP"

    @classmethod
    def add_parser(cls, subparser):
        """
        Creates parser for command line.
        """
        parser = super(LookupUser, cls).add_parser(subparser)
        parser.add_argument(
            "--by",
            type=str,
            default='smart-uid',
            help='LDAP lookup attribute'
        )
        parser.add_argument(
            "--attribs",
            type=str,
            default='',
            help='Comma separated list of LDAP attributes to print'
        )
        parser.add_argument(
            "value",
            nargs=1,
            type=str,
            help='LDAP lookup string, usually username'
        )
        return parser

    def run(self):
        self.println(pformat(self.search()))

    def search(self):
        """
        Performs LDAP search.
        """
        userinfo = UserInfo(
            self.config.get('ldap', 'server'),
            self.config.get('ldap', 'base'),
        )
        if self.args.attribs:
            attribs = self.args.attribs.split(',')
        else:
            attribs = []
        if self.args.by == "smart-uid":
            return userinfo.search_uid(self.args.value[0], attribs)

        return userinfo.search_by(self.args.by, self.args.value[0], attribs)


@register_command
class Absence(Command):
    """
    Displays absences for user.
    """
    name = 'absence'
    description = "Look up a user in presence database"

    @classmethod
    def add_parser(cls, subparser):
        """
        Creates parser for command line.
        """
        parser = super(Absence, cls).add_parser(subparser)
        parser.add_argument(
            "value",
            nargs=1,
            type=str,
            help='Username to lookup'
        )
        return parser

    def run(self):
        servers = []
        for server in self.config.get('presence', 'servers').split(','):
            server = server.strip()
            if not server:
                continue
            nosend = False
            if server.endswith('/nosend'):
                server = server[:-7]
                nosend = True
            servers.append((server, nosend))

        for absence in Presence(servers).get_presence_data(self.args.value[0]):
            self.println(
                '{0} - {1}'.format(absence[0], absence[1])
            )


def main(settings=None, stdout=None, args=None):
    """
    Execution entry point.
    """
    parser = get_parser()
    if args is None:
        args = sys.argv[1:]
    args = parser.parse_args(args)

    config = SuseAPIConfig()
    if settings is None:
        config.load()
    else:
        for section, key, value in settings:
            config.set(section, key, value)

    command = COMMANDS[args.cmd](args, config, stdout)
    command.run()
