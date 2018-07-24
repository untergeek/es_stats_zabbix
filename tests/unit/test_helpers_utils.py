"""Unit tests for es_stats_zabbix/helpers/utils.py"""
import socket
from unittest import TestCase
from es_stats_zabbix.helpers.utils import open_port, status_map

class TestStatusMap(TestCase):
    """StatusMap test class"""
    def test_expected(self):
        """Test the Zabbix mapping of Elasticsearch health status"""
        status_dict = {
            'green': 0,
            'yellow': 1,
            'red': 2,
        }
        for k in list(status_dict.keys()):
            self.assertEqual(status_dict[k], status_map(k))
    def test_unexpected(self):
        """Test that a 3 is reported for anything not 'green', 'yellow', or 'red'"""
        self.assertEqual(3, status_map('anything_else'))

class TestOpenPort(TestCase):
    """Class to test port response"""
    def test_open_port(self):
        """Test that an open port is correctly recognized"""
        host = 'localhost'
        port = 7606
        sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sck.bind((host, port))
        sck.listen(1)
        self.assertTrue(open_port(host, port))
        sck.close()
    def test_closed_port(self):
        """Test that a closed port is correctly recognized"""
        host = 'localhost'
        port = 7606
        self.assertFalse(open_port(host, port))
