from __future__ import print_function

import sys
from xdg.BaseDirectory import load_first_config
from pprint import pformat

from suseapi.userinfo import UserInfo

class ErrorMessage(Exception):
    pass

def main():
    try:
        rc = realmain(sys, load_first_config, UserInfo, pformat)
    except ErrorMessage as e:
        print(e, file = sys.stderr)
        rc = 1

    sys.exit(rc)

def realmain(sys, config_loader, userinfo, pformat):
    f = config_loader("suseapi")
    if not f:
        raise ErrorMessage("Missing config file")

    try:
        uid = sys.argv[1]
    except IndexError:
        raise ErrorMessage("Missing uid argument")

    # parse like Xdefaults file
    cg = dict(
        [ (key.strip(), val.strip()) for key, _, val
        in [ x.partition(":") for x in open(f).readlines() ]
    ])

    ui = userinfo(cg['ldap.server'], cg['ldap.base'])
    print(pformat(ui.search_uid(uid, [])), file = sys.stdout)
