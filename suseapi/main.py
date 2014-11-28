from __future__ import print_function

import sys
from xdg.BaseDirectory import load_first_config
from pprint import pformat
from argparse import ArgumentParser
from copy import deepcopy

from suseapi.userinfo import UserInfo

class ErrorMessage(Exception):
    pass

def main():
    try:
        rc = realmain(sys, load_first_config, {
            'lookup-user': LookupUser,
        })
    except ErrorMessage as e:
        print(e, file = sys.stderr)
        rc = 1

    sys.exit(rc)

def get_parser():
    p = ArgumentParser()
    sp = p.add_subparsers(dest = "cmd")

    lup = sp.add_parser(
        "lookup-user",
        description = "Look up a user in LDAP",
    )
    lup.add_argument("--by", type=str, default='smart-uid')
    lup.add_argument("value", nargs=1, type=str)

    return p

class Command(object):
    def __init__(self, args, sys, config):
        self.sys = sys
        self.args = args
        self.config = config

        self.run()

    def println(self, ln):
        print(ln, file = self.sys.stdout)

    def run(self):
        raise NotImplementedError

    def _kwargs(self, expected, got):
        got = deepcopy(got)

        for k, v in expected.items():
            try:
                v = got[k]
            except KeyError:
                pass
            else:
                del got[k]

            setattr(self, k, v)

        return got

class LookupUser(Command):
    def __init__(self, *a, **kw):
        kw = self._kwargs(dict(
            userinfo = UserInfo,
            pformat = pformat,
        ), kw)

        super(LookupUser, self).__init__(*a, **kw)

    def run(self):
        self.println(self.pformat(self.search()))

    def search(self):
        ui = self.userinfo(self.config['ldap.server'], self.config['ldap.base'])
        if self.args.by == "smart-uid":
            return ui.search_uid(self.args.value[0], [])

        return ui.search_by(self.args.by, self.args.value[0])

def realmain(sys, config_loader, commands):
    p = get_parser()
    args = p.parse_args(sys.argv[1:])

    f = config_loader("suseapi")
    if not f:
        raise ErrorMessage("Missing config file")

    # parse like Xdefaults file
    cg = dict(
        [ (key.strip(), val.strip()) for key, _, val
        in [ x.partition(":") for x in open(f).readlines() ]
    ])

    commands[args.cmd](args, sys, cg)
