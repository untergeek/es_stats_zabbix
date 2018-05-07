import os
import shutil
import tempfile
import random
import string
import time
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError
from es_stats.classes import ClusterHealth, ClusterState, ClusterStats, NodeInfo, NodeStats
from es_stats_zabbix.helpers.execution import RequestLogger, Discovery, Stat, run
from es_stats_zabbix.helpers.utils import open_port
from flask import Flask, request
from flask_restful import Resource, Api
from multiprocessing import Process
from unittest import SkipTest, TestCase

client = None

host, port = os.environ.get('TEST_ES_SERVER', 'localhost:9200').split(':')
port = int(port) if port else 9200

flaskhost, flaskport = os.environ.get('TEST_ESZ_BACKEND', 'localhost:5000').split(':')
flaskport = int(flaskport) if flaskport else 5000

BASE_CONFIG = {
    'elasticsearch': {
        'skip_version_test': True,
        'client': {
            'hosts': host,
            'port': port,
        }
    },
    'logging': {
        'loglevel': 'DEBUG'
    },
    'backend': {
        'host': flaskhost,
        'port': flaskport,
    },
    'do_not_discover': {
        'health': ['status']
    }
}

def get_client():
    global client
    if client is not None:
        return client

    client = Elasticsearch([os.environ.get('TEST_ES_SERVER', {})], timeout=300)

    # wait for yellow status
    for _ in range(100):
        time.sleep(.1)
        try:
            # This errors because of decorators.  Silence it.
            # pylint: disable=E1123
            client.cluster.health(wait_for_status='yellow')
            return client
        except ConnectionError:
            continue
    else:
        # timeout
        raise SkipTest("Elasticsearch failed to start.")

def backendUp():
    for _ in range(100):
        if open_port(flaskhost, flaskport):
            return True
        else:
            time.sleep(0.1)
    return False

def random_directory():
    dirname = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    directory = tempfile.mkdtemp(suffix=dirname)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

class Args(dict):
    def __getattr__(self, att_name):
        return self.get(att_name, None)

class FlaskUnitTest(TestCase):
    def setUp(self):
        super(FlaskUnitTest, self).setUp()
        self.client = get_client()
        self.args = {}
        self.args['configdir'] = random_directory()
        self.args['configfile'] = os.path.join(self.args['configdir'], 'test.yml')
        self.args['flaskhost'] = flaskhost
        self.args['flaskport'] = flaskport

        app = Flask('INTEGRATION_TESTS')
        app.config['TESTING'] = True
        api = Api(app)
        api.add_resource(Stat, '/api/health/<key>', endpoint='/health/',
            resource_class_kwargs={'statobj': ClusterHealth(self.client)})
        api.add_resource(Stat, '/api/clusterstate/<key>', endpoint='/clusterstate/',
            resource_class_kwargs={'statobj': ClusterState(self.client)})
        api.add_resource(Stat, '/api/clusterstats/<key>', endpoint='/clusterstats/',
            resource_class_kwargs={'statobj': ClusterStats(self.client)})
        api.add_resource(Stat, '/api/nodeinfo/<key>', endpoint='/nodeinfo/',
            resource_class_kwargs={'statobj': NodeInfo(self.client)})
        api.add_resource(Stat, '/api/nodestats/<key>', endpoint='/nodestats/',
            resource_class_kwargs={'statobj': NodeStats(self.client)})
        api.add_resource(Discovery, '/api/discovery/<api>', endpoint='/discovery/',
            resource_class_kwargs={'client': self.client, 'do_not_discover': {'health': ['status']}})
        api.add_resource(RequestLogger, '/api/logger/<loglevel>', endpoint='/logger/')
        self.app = app

    # executed after each test
    def tearDown(self):
        if os.path.exists(self.args['configdir']):
            shutil.rmtree(self.args['configdir'])

    def parse_args(self):
        return Args(self.args)

    def write_config(self, fname, data):
        with open(fname, 'w') as f:
            f.write(data)

class BackendCase(TestCase):
    def setUp(self):
        self.client = get_client()
        self.nodeid = list(self.client.nodes.info()['nodes'].keys())[0]
        self.nodename = self.client.nodes.info()['nodes'][self.nodeid]['name']
        self.args = {}
        self.args['flaskhost'] = flaskhost
        self.args['flaskport'] = flaskport
        self.backend = Process(target=run, args=(BASE_CONFIG,))
        self.backend.start()
        if not backendUp():
            raise SkipTest('Unable to start the backend')
    def tearDown(self):
        self.backend.terminate()
