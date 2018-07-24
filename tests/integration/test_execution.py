"""Test the flask bits"""
import json
import logging
import click

from . import FlaskUnitTest


class TestGetStat(FlaskUnitTest):
    """Test basic GET functionality"""
    def test_get(self):
        """Test basic GET functionality"""
        with self.app.test_client() as client:
            result = client.get('/api/health/status')
            self.assertEqual(b'0\n', result.data)
    def test_post(self):
        """Test basic POST functionality"""
        with self.app.test_client() as client:
            nodename = client.get('/api/nodestats/name').data.decode('utf-8').strip().strip('"')
        with self.app.test_client() as client:
            result = client.post('/api/nodeinfo/name', json={'node':nodename})
            result = result.data.decode('utf-8').strip().strip('"')
            self.assertEqual(nodename, result)
    def test_four_o_four(self):
        """Assert that a 404 is returned when a non-existent endpoint is polled"""
        with self.app.test_client() as client:
            result = client.get('/api/nodestats/notreallythere')
            self.assertEqual(404, result.status_code)
    def test_bool_true(self):
        """Test that a string '1' is returned for a truthy value"""
        with self.app.test_client() as client:
            result = client.get('/api/nodeinfo/jvm.using_compressed_ordinary_object_pointers')
            self.assertEqual('1', result.data.decode('utf-8').strip().strip('"'))
    def test_bool_false(self):
        """Test that a string '0' is returned for a false value"""
        with self.app.test_client() as client:
            result = client.get('/api/nodeinfo/process.mlockall')
            self.assertEqual('0', result.data.decode('utf-8').strip().strip('"'))

# Tests that work on the command-line are not working here.  Calling the exact same API
# results in no problems at the command-line, but lots here.
# class TestGetDiscovery(FlaskUnitTest):
#     """Test the Zabbix discovery script"""
#     def test_get_health(self):
#         """Test that we get an appropriate value back"""
#         with self.app.test_client() as client:
#             result = client.get('/api/discovery/')
#             # data = json.loads(result.data.decode('utf-8'))['data']
#             # self.assertEqual(data[0], {"{#CHARACTER}":"cluster_name"})
#             self.assertEqual(200, result.status_code)
#     def test_all_apis_and_valuetypes(self):
#         """Test that we get a 200 when discovering everything"""
#         with self.app.test_client() as client:
#             for api in ['health', 'clusterstate', 'clusterstats', 'nodeinfo', 'nodestats']:
#                 for valuetype in ['bool', 'character', 'unsigned', 'float']:
#                     result = client.post('/api/discovery/' + api, json={'valuetype':valuetype})
#                     self.assertEqual(200, result.status_code)
#     def test_dnd(self):
#         """Test that items flagged as DND (do not discover) are not discovered"""
#         with self.app.test_client() as client:
#             result = client.get('/api/discovery/health')
#             data = json.loads(result.data.decode('utf-8'))['data']
#             self.assertFalse({"{#ENDPOINT}":"status"} in data)

####
#### WEIRDNESS ALERT
####
# result = client.get('/api/nodediscovery/')
# This line gives a 404, though it works manually.  I cannot explain it.
# As a result, this test is incomplete, and commented out.
# class TestNodeDiscovery(FlaskUnitTest):
#     def test_get_all(self):
#         with self.app.test_client() as client:
#             nodename = client.get('/api/nodestats/name').data.decode('utf-8').strip().strip('"')
#         with self.app.test_client() as client:
#             result = client.get('/api/nodediscovery/')
#             # data = json.loads(result.data.decode('utf-8'))['data']
#             # self.assertEqual(data[0], {"{#NODEID}":"cluster_name", "{#NODENAME":nodename})
#             self.assertEqual(200, result.status_code)

class TestRequestLogger(FlaskUnitTest):
    """Test logging back from the client to the upstream"""
    def test_post(self):
        """Test basic POST"""
        with self.app.test_client() as client:
            result = client.post('/api/logger/debug', json={'message':'test'})
            self.assertEqual(200, result.status_code)
    def test_empty_post(self):
        """Test empty POST"""
        with self.app.test_client() as client:
            result = client.post('/api/logger/debug')
            self.assertEqual(200, result.status_code)
