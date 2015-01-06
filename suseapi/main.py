# -*- coding: utf-8 -*-
#
# Copyright © 2012 - 2015 Michal Čihař <mcihar@suse.cz>
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


COMMANDS = {}


def register_command(command):
    """
    Decorator to register command in command line interface.
    """
    COMMANDS[command.name] = command
    return command


class SuseAPIConfig(RawConfigParser):
    def __init__(self):
        RawConfigParser.__init__(self)
        # Set defaults
        self.add_section('ldap')
        self.set('ldap', 'server', 'ldap://pan.suse.de')
        self.set('ldap', 'base', 'o=Novell')

    def load(self):
        self.read(load_config_paths('suseapi'))


def main():
    """
    Execution entry point.
    """
    realmain(COMMANDS)


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

    def __init__(self, args, config):
        self.args = args
        self.config = config

        self.run()

    @classmethod
    def add_parser(cls, subparser):
        """
        Creates parser for command line.
        """
        return subparser.add_parser(
            cls.name, description=cls.description
        )

    def println(self, line):
        print(line, file=sys.stdout)

    def run(self):
        raise NotImplementedError


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
        parser.add_argument("--by", type=str, default='smart-uid')
        parser.add_argument("value", nargs=1, type=str)
        return parser

    def run(self):
        self.println(pformat(self.search()))

    def search(self):
        userinfo = UserInfo(
            self.config.get('ldap', 'server'),
            self.config.get('ldap', 'base'),
        )
        if self.args.by == "smart-uid":
            return userinfo.search_uid(self.args.value[0], [])

        return userinfo.search_by(self.args.by, self.args.value[0], [])


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
        parser.add_argument("value", nargs=1, type=str)
        return parser

    def run(self):
        for absence in Presence().get_presence_data(self.args.value[0]):
            self.println(
                '{0} - {1}'.format(absence[0], absence[1])
            )


def realmain(commands):
    """
    The core of the invoker.
    """
    parser = get_parser()
    args = parser.parse_args(sys.argv[1:])

    config = SuseAPIConfig()
    config.load()

    commands[args.cmd](args, config)
