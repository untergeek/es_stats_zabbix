"""Test the get_es_stat function"""
import json
import threading
import time
from click import testing as clicktest
from es_stats_zabbix.cli import get_es_stat
from es_stats_zabbix.exceptions import FailedExecution
from es_stats_zabbix.helpers.utils import do_request
from . import BackendCase

class TestGetStat(BackendCase):
    """Test class for es_stats_zabbix.cli.get_es_stat"""
    def test_valid_get(self):
        """It should be able to get the basic health status"""
        test = clicktest.CliRunner()
        result = test.invoke(
            get_es_stat.cli,
            [
                '--host', self.args['flaskhost'],
                '--port', self.args['flaskport'],
                '--debug',
                'health',
                'status'
            ],
        )
        self.assertEqual(0, int(result.output.rstrip()))
    def test_bad_port(self):
        """A bad port should result in an exit code of 1"""
        test = clicktest.CliRunner()
        result = test.invoke(
            get_es_stat.cli,
            [
                '--host', '127.0.0.1',
                '--port', '5001',
                '--debug',
                'health',
                'status'
            ],
        )
        self.assertEqual(1, result.exit_code)
    def test_bad_api(self):
        """A bad API should result in an exit code of 1"""
        test = clicktest.CliRunner()
        result = test.invoke(
            get_es_stat.cli,
            [
                '--host', self.args['flaskhost'],
                '--port', self.args['flaskport'],
                '--debug',
                'invalid',
                'status'
            ],
        )
        self.assertEqual(1, result.exit_code)
    def test_valid_post(self):
        """A valid post request should work"""
        test = clicktest.CliRunner()
        result = test.invoke(
            get_es_stat.cli,
            [
                '--host', self.args['flaskhost'],
                '--port', self.args['flaskport'],
                '--debug',
                '--node', self.nodename,
                'nodestats',
                'name'
            ],
        )
        self.assertEqual(self.nodename, result.output.rstrip().strip('"'))
    def test_raises_exception(self):
        """An exception should be raised if a non-existent node is polled"""
        test = clicktest.CliRunner()
        result = test.invoke(
            get_es_stat.cli,
            [
                '--host', self.args['flaskhost'],
                '--port', self.args['flaskport'],
                '--debug',
                '--node', 'notfound',
                'nodestats',
                'name'
            ],
        )
        self.assertEqual('ZBX_NOTSUPPORTED', result.output.rstrip().strip('"'))
