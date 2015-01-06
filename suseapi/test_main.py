from unittest import TestCase
from argparse import Namespace
from StringIO import StringIO

from suseapi.main import get_parser, main
from suseapi.test_presence import start_test_server, stop_test_server


class TestArgParser(TestCase):
    def test_lookup_user(self):
        parser = get_parser()
        args = parser.parse_args(["lookup-user", "foo"])
        self.assertEqual(args, Namespace(
            cmd='lookup-user',
            by='smart-uid',
            value=['foo']
        ))


class TestCommands(TestCase):
    def test_absence(self):
        output = StringIO()
        server = start_test_server()
        try:
            main(
                settings=(('presence', 'servers', '127.0.0.1/nosend'),),
                args=['absence', 'mcihar'],
                stdout=output
            )
        finally:
            stop_test_server(*server)

        self.assertTrue('2013-10-25 - 2013-10-28' in output.getvalue())
