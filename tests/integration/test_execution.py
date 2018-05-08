import click
import json
from . import FlaskUnitTest

class TestGetStat(FlaskUnitTest):
    def test_get(self):
        with self.app.test_client() as c:
            result = c.get('/api/health/status')
            self.assertEqual(b'0\n', result.data)
    def test_post(self):
        with self.app.test_client() as c:
            nodename = c.get('/api/nodestats/name').data.decode('utf-8').strip().strip('"')
        with self.app.test_client() as c:
            result = c.post('/api/nodeinfo/name', json={'node':nodename})
            result = result.data.decode('utf-8').strip().strip('"')
            self.assertEqual(nodename, result)
    def test_four_o_four(self):
        with self.app.test_client() as c:
            result = c.get('/api/nodestats/notreallythere')
            self.assertEqual(404, result.status_code)
    def test_bool_true(self):
        with self.app.test_client() as c:
            result = c.get('/api/nodeinfo/jvm.using_compressed_ordinary_object_pointers')
            self.assertEqual('1', result.data.decode('utf-8').strip().strip('"'))
    def test_bool_false(self):
        with self.app.test_client() as c:
            result = c.get('/api/nodeinfo/process.mlockall')
            self.assertEqual('0', result.data.decode('utf-8').strip().strip('"'))

class TestGetDiscovery(FlaskUnitTest):
    def test_get_health(self):
        with self.app.test_client() as c:
            result = c.post('/api/discovery/health', json={'valuetype':'character'})
            data = json.loads(result.data.decode('utf-8'))['data']
            self.assertEqual(data[0], {"{#CHARACTER}":"cluster_name"})
            self.assertEqual(200, result.status_code)
    def test_all_apis_and_valuetypes(self):
        with self.app.test_client() as c:
            for api in ['health','clusterstate','clusterstats','nodeinfo','nodestats']:
                for vt in ['bool','character','unsigned','float']:
                    result = c.post('/api/discovery/' + api, json={'valuetype':vt})
                    self.assertEqual(200, result.status_code)
    def test_dnd(self):
        with self.app.test_client() as c:
            result = c.get('/api/discovery/health')
            data = json.loads(result.data.decode('utf-8'))['data']
            self.assertFalse({"{#ENDPOINT}":"status"} in data)

class TestRequestLogger(FlaskUnitTest):
    def test_post(self):
        with self.app.test_client() as c:
            result = c.post('/api/logger/debug', json={'message':'test'})
            self.assertEqual(200, result.status_code)
    def test_empty_post(self):
        with self.app.test_client() as c:
            result = c.post('/api/logger/debug')
            self.assertEqual(200, result.status_code)

