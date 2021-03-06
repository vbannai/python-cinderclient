import cStringIO
import os
import httplib2
import sys

from cinderclient import exceptions
import cinderclient.shell
from tests import utils


class ShellTest(utils.TestCase):

    # Patch os.environ to avoid required auth info.
    def setUp(self):
        global _old_env
        fake_env = {
            'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_TENANT_NAME': 'tenant_name',
            'OS_AUTH_URL': 'http://no.where',
        }
        _old_env, os.environ = os.environ, fake_env.copy()

    def shell(self, argstr):
        orig = sys.stdout
        try:
            sys.stdout = cStringIO.StringIO()
            _shell = cinderclient.shell.OpenStackCinderShell()
            _shell.main(argstr.split())
        except SystemExit:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.assertEqual(exc_value.code, 0)
        finally:
            out = sys.stdout.getvalue()
            sys.stdout.close()
            sys.stdout = orig

        return out

    def tearDown(self):
        global _old_env
        os.environ = _old_env

    def test_help_unknown_command(self):
        self.assertRaises(exceptions.CommandError, self.shell, 'help foofoo')

    def test_debug(self):
        httplib2.debuglevel = 0
        self.shell('--debug help')
        assert httplib2.debuglevel == 1

    def test_help(self):
        required = [
            '^usage: ',
            '(?m)^\s+create\s+Add a new volume.',
            '(?m)^See "cinder help COMMAND" for help on a specific command',
        ]
        for argstr in ['--help', 'help']:
            help_text = self.shell(argstr)
            for r in required:
                self.assertRegexpMatches(help_text, r)

    def test_help_on_subcommand(self):
        required = [
            '^usage: cinder list',
            '(?m)^List all the volumes.',
        ]
        argstrings = [
            'list --help',
            'help list',
        ]
        for argstr in argstrings:
            help_text = self.shell(argstr)
            for r in required:
                self.assertRegexpMatches(help_text, r)
