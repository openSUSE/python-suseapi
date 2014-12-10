from unittest import TestCase
from argparse import Namespace

from suseapi.main import get_parser


class TestArgParser(TestCase):
    def test_lookup_user(self):
        parser = get_parser()
        args = parser.parse_args(["lookup-user", "foo"])
        self.assertEqual(args, Namespace(
            cmd='lookup-user',
            by='smart-uid',
            value=['foo']
        ))
