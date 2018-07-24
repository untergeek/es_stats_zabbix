"""Integration tests for es_stats_zabbix/helpers/utils.py"""
import json
import threading
import time
from es_stats_zabbix.exceptions import FailedExecution
from es_stats_zabbix.helpers.utils import do_request, open_port
from . import BackendCase, get_client


class TestDoRequest(BackendCase):
    """DoRequest Test Class"""
    # This 'loopy' nonsense is only to compensate for Travis CI nonsense.
    # It tests just fine locally.  It only seems constrained with Travis CI VMs.
    def loopy(self, host, port, uri, method, body=None):
        """Method to help compensate for Travis CI issues"""
        for _ in range(4):
            try:
                return do_request(host, port, uri, method, body=body).strip()
            except:
                pass
        raise FailedExecution

    def test_get(self):
        """Test the GET method"""
        self.assertEqual('0',
                         self.loopy(self.args['flaskhost'],
                                    self.args['flaskport'], '/api/health/status', 'get')
                        )
    def test_post(self):
        """Test the POST method"""
        self.assertEqual(
            self.nodename,
            self.loopy(self.args['flaskhost'],
                       self.args['flaskport'],
                       '/api/nodeinfo/name',
                       'post',
                       body={'node':self.nodename}
                      ).strip().strip('"')
        )
    def test_raises_on_no_body(self):
        """Test that an exception is raised when there is no 'body'"""
        self.assertRaises(
            FailedExecution,
            do_request,
            self.args['flaskhost'], self.args['flaskport'], '/api/nodeinfo/name', 'post', body=None
        )
    def test_raises_on_non_200(self):
        """Test that an exception is raised when a non-200 HTTP response is received"""
        self.assertRaises(
            FailedExecution,
            do_request,
            self.args['flaskhost'],
            self.args['flaskport'],
            '/api/nodeinfo/notpresent',
            'post',
            body={'invalid':'empty'}
        )
