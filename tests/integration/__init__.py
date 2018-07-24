"""Set up the integration test module"""
import os
import shutil
import tempfile
import random
import string
import time
from multiprocessing import Process
from unittest import SkipTest, TestCase
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError
from flask import Flask, request
from flask_restful import Resource, Api

from es_stats.classes import ClusterHealth, ClusterState, ClusterStats, NodeInfo, NodeStats
from es_stats_zabbix.backend import RequestLogger, Discovery, Stat, run_backend
from es_stats_zabbix.helpers.config import get_config
from es_stats_zabbix.helpers.utils import open_port

HOST, PORT = os.environ.get('TEST_ES_SERVER', 'localhost:9200').split(':')
PORT = int(PORT) if PORT else 9200

FLASKHOST, FLASKPORT = os.environ.get('TEST_ESZ_BACKEND', 'localhost:5000').split(':')
FLASKPORT = int(FLASKPORT) if FLASKPORT else 5000

BASE_CONFIG = {
    'elasticsearch': {
        'skip_version_test': True,
        'client': {
            'hosts': HOST,
            'port': PORT,
        }
    },
    'logging': {
        'loglevel': 'DEBUG'
    },
    'backend': {
        'host': FLASKHOST,
        'port': FLASKPORT,
    },
    'zabbix': {},
    'endpoints': {
        'cluster': {
            '60s': {
                'clusterstats': ['_nodes.total']
            }
        },
        'coordinating': {
            '60s': {
                'nodeinfo': [
                    'jvm.using_compressed_ordinary_object_pointers',
                    'jvm.version',
                    'jvm.vm_name',
                    'jvm.vm_vendor',
                    'jvm.vm_version',
                    'name',
                ]
            }
        }
    },
    'do_not_discover': {
        'health': ['status']
    }
}

def get_client():
    """Return a valid Elasticsearch client object"""

    client = Elasticsearch(host=HOST, port=PORT, timeout=300)

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

def backend_up():
    """Respond with boolean of whether the Flask backend is up or down"""
    for _ in range(100):
        if open_port(FLASKHOST, FLASKPORT):
            return True
        else:
            time.sleep(0.1)
    return False

def random_directory():
    """Generate a randomly named directory in the OS temp path"""
    dirname = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    directory = tempfile.mkdtemp(suffix=dirname)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

class Args(dict):
    """Argument class"""
    def __getattr__(self, att_name):
        return self.get(att_name, None)

class FlaskUnitTest(TestCase):
    """
    Unit TestCase subclass for Flask backend
    Still in the integration tests as it requires a running Elasticsearch.
    """
    def setUp(self):
        super(FlaskUnitTest, self).setUp()
        self.client = get_client()
        self.args = {}
        self.args['configdir'] = random_directory()
        self.args['configfile'] = os.path.join(self.args['configdir'], 'test.yml')
        self.args['flaskhost'] = FLASKHOST
        self.args['flaskport'] = FLASKPORT
        self.args['endpoints'] = get_config(BASE_CONFIG, 'endpoints')
        c_t = 60
        self.statobjs = {
            'health': ClusterHealth(self.client, cache_timeout=c_t),
            'clusterstate': ClusterState(self.client, cache_timeout=c_t),
            'clusterstats': ClusterStats(self.client, cache_timeout=c_t),
            'nodeinfo': NodeInfo(self.client, cache_timeout=c_t),
            'nodestats': NodeStats(self.client, cache_timeout=c_t),
        }

        app = Flask('INTEGRATION_TESTS')
        app.config['TESTING'] = True
        api = Api(app)
        api.add_resource(Stat, '/api/health/<key>', endpoint='/health/',
                         resource_class_kwargs={'statobj': self.statobjs['health']})
        api.add_resource(Stat, '/api/clusterstate/<key>', endpoint='/clusterstate/',
                         resource_class_kwargs={'statobj': self.statobjs['clusterstate']})
        api.add_resource(Stat, '/api/clusterstats/<key>', endpoint='/clusterstats/',
                         resource_class_kwargs={'statobj': self.statobjs['clusterstats']})
        api.add_resource(Stat, '/api/nodeinfo/<key>', endpoint='/nodeinfo/',
                         resource_class_kwargs={'statobj': self.statobjs['nodeinfo']})
        api.add_resource(Stat, '/api/nodestats/<key>', endpoint='/nodestats/',
                         resource_class_kwargs={'statobj': self.statobjs['nodestats']})
        api.add_resource(Discovery, '/api/discovery/', endpoint='/discovery/',
                         resource_class_kwargs={
                             'statobjs': self.statobjs,
                             'endpoints': self.args['endpoints'],
                             'do_not_discover':{'health':['status']}
                         }
                        )
        api.add_resource(RequestLogger, '/api/logger/<loglevel>', endpoint='/logger/')
        self.app = app

    # executed after each test
    def tearDown(self):
        if os.path.exists(self.args['configdir']):
            shutil.rmtree(self.args['configdir'])

    def parse_args(self):
        """Parse the arguments passed to Flask"""
        return Args(self.args)

    def write_config(self, fname, data):
        """Write a config file to the provided filename"""
        with open(fname, 'w') as fhandle:
            fhandle.write(data)

class BackendCase(TestCase):
    """TestCase subclass for Flask backend"""
    def setUp(self):
        self.client = get_client()
        self.nodeid = list(self.client.nodes.info()['nodes'].keys())[0]
        self.nodename = self.client.nodes.info()['nodes'][self.nodeid]['name']
        self.args = {}
        self.args['flaskhost'] = FLASKHOST
        self.args['flaskport'] = FLASKPORT
        self.backend = Process(target=run_backend, args=(BASE_CONFIG,))
        self.backend.start()
        if not backend_up():
            raise SkipTest('Unable to start the backend')
    def tearDown(self):
        self.backend.terminate()
