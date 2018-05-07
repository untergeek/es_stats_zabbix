import socket
from unittest import TestCase
from es_stats_zabbix.helpers.utils import open_port, status_map

class TestStatusMap(TestCase):
    def test_expected(self):
        MAP = {
            'green': 0,
            'yellow': 1,
            'red': 2,
        }
        for k in list(MAP.keys()):
            self.assertEqual(MAP[k], status_map(k))
    def test_unexpected(self):
        self.assertEqual(3, status_map('anything_else'))

class TestOpenPort(TestCase):
    def test_open_port(self):
        host = 'localhost'
        port = 7600
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen(1)
        self.assertTrue(open_port(host, port))
        s.close()
    def test_closed_port(self):
        host = 'localhost'
        port = 7600
        self.assertFalse(open_port(host, port))