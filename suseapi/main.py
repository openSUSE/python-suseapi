# -*- coding: utf-8 -*-
#
# Copyright © 2012 - 2014 Michal Čihař <mcihar@suse.cz>
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
from xdg.BaseDirectory import load_first_config
from pprint import pformat
from argparse import ArgumentParser

from suseapi.userinfo import UserInfo
from suseapi.presence import Presence


class ErrorMessage(Exception):
    """
    Error raised by commands.
    """
    pass


def main():
    """
    Execution entry point.
    """
    try:
        realmain(load_first_config, {
            'lookup-user': LookupUser,
            'absence': Absence,
        })
    except ErrorMessage as error:
        print(error, file=sys.stderr)
        sys.exit(1)


def get_parser():
    """
    Creates argument parser.
    """
    parser = ArgumentParser()
    subparser = parser.add_subparsers(dest="cmd")

    lup = subparser.add_parser(
        "lookup-user",
        description="Look up a user in LDAP",
    )
    lup.add_argument("--by", type=str, default='smart-uid')
    lup.add_argument("value", nargs=1, type=str)

    absence = subparser.add_parser(
        "absence",
        description="Look up a user in presence database",
    )
    absence.add_argument("value", nargs=1, type=str)

    return parser


class Command(object):
    """
    Basic command object.
    """
    def __init__(self, args, config):
        self.args = args
        self.config = config

        self.run()

    def println(self, line):
        print(line, file=sys.stdout)

    def run(self):
        raise NotImplementedError


class LookupUser(Command):
    """
    User lookup command.
    """
    def run(self):
        self.println(pformat(self.search()))

    def search(self):
        userinfo = UserInfo(
            self.config['ldap.server'],
            self.config['ldap.base']
        )
        if self.args.by == "smart-uid":
            return userinfo.search_uid(self.args.value[0], [])

        return userinfo.search_by(self.args.by, self.args.value[0], [])


class Absence(Command):
    """
    Displays absences for user.
    """
    def run(self):
        for absence in Presence().get_presence_data(self.args.value[0]):
            self.println(
                '{0} - {1}'.format(absence[0], absence[1])
            )


def realmain(config_loader, commands):
    """
    The core of the invoker.
    """
    parser = get_parser()
    args = parser.parse_args(sys.argv[1:])

    filename = config_loader("suseapi")
    if not filename:
        raise ErrorMessage("Missing config file")

    # parse like Xdefaults file
    config = dict([
        (key.strip(), val.strip()) for key, dummy, val
        in [x.partition(":") for x in open(filename).readlines()]
    ])

    commands[args.cmd](args, config)
