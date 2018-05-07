import json
import threading
import time
from click import testing as clicktest
from es_stats_zabbix import get_es_stat
from es_stats_zabbix.exceptions import FailedExecution
from es_stats_zabbix.helpers.utils import do_request
from . import BackendCase

class TestGetStat(BackendCase):
    def test_valid_get(self):
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

