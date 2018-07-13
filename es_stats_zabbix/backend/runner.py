"""
Actually run the flask backend, and spin up all Resource classes and necessary configuration data
"""

import json
import logging
from time import sleep
from flask import Flask
from flask_restful import Api
from es_stats.classes import ClusterHealth, ClusterState, ClusterStats, NodeInfo, NodeStats
from es_stats_zabbix.backend import (
    ClusterDiscovery, Discovery, DisplayEndpoints, NodeDiscovery, RequestLogger, Stat,
    TrapperDiscovery, TrapperStats
)
from es_stats_zabbix.exceptions import ConfigurationError
from es_stats_zabbix.helpers.config import configure_logging, get_client, get_config

def retry_es_connect(config):
    """
    On initial connection, to prevent a failure of the flask backend,
    continually retry connection to Elasticsearch until able to establish a connection.
    """
    logger = logging.getLogger('esz.backend.runner')
    connected = False
    while not connected:
        try:
            client = get_client(config)
            info = client.info()
            logger.info(
                'Connected to cluster: "{0}" through (initial) node: "{1}".  '
                'Elasticsearch version: "{2}"'.format(
                    info['cluster_name'], info['name'], info['version']['number']
                )
            )
            connected = True
        except ConfigurationError:
            msg = 'Unable to connect to Elasticsearch cluster. Retry in 5 seconds...'
            logger.error(msg)
            sleep(5)
    return client

def run_backend(config_dict):
    """
    Actually launch the backend.
    """
    # Enable logging first
    configure_logging(config_dict)
    logger = logging.getLogger('esz.backend.run_backend')
    dnd = get_config(config_dict, 'do_not_discover')
    zabbix = get_config(config_dict, 'zabbix')
    endpoints = get_config(config_dict, 'endpoints')
    backend = get_config(config_dict, 'backend')
    c_t = backend['cache_timeout']

    # Now that logging is enabled and we have the rest of the configuration,
    # let's attempt an Elasticsearch Client connection:
    client = retry_es_connect(config_dict)

    app = Flask(__name__)
    api = Api(app)
    statobjs = {
        'health': ClusterHealth(client, cache_timeout=c_t),
        'clusterstate': ClusterState(client, cache_timeout=c_t),
        'clusterstats': ClusterStats(client, cache_timeout=c_t),
        'nodeinfo': NodeInfo(client, cache_timeout=c_t),
        'nodestats': NodeStats(client, cache_timeout=c_t),
    }
    api.add_resource(Stat, '/api/health/<key>', endpoint='/health/',
                     resource_class_kwargs={'statobj': statobjs['health']})
    api.add_resource(Stat, '/api/clusterstate/<key>', endpoint='/clusterstate/',
                     resource_class_kwargs={'statobj': statobjs['clusterstate']})
    api.add_resource(Stat, '/api/clusterstats/<key>', endpoint='/clusterstats/',
                     resource_class_kwargs={'statobj': statobjs['clusterstats']})
    api.add_resource(Stat, '/api/nodeinfo/<key>', endpoint='/nodeinfo/',
                     resource_class_kwargs={'statobj': statobjs['nodeinfo']})
    api.add_resource(Stat, '/api/nodestats/<key>', endpoint='/nodestats/',
                     resource_class_kwargs={'statobj': statobjs['nodestats']})
    api.add_resource(DisplayEndpoints, '/api/display/', endpoint='/display/',
                     resource_class_kwargs={'statobjs': statobjs})
    api.add_resource(Discovery, '/api/discovery/', endpoint='/discovery/',
                     resource_class_kwargs={
                         'statobjs': statobjs,
                         'endpoints': endpoints,
                         'do_not_discover': dnd})
    api.add_resource(ClusterDiscovery, '/api/clusterdiscovery/<value>',
                     endpoint='/clusterdiscovery/',
                     resource_class_kwargs={'statobjs': statobjs})
    api.add_resource(NodeDiscovery, '/api/nodediscovery/<node>', endpoint='/nodediscovery/',
                     resource_class_kwargs={'statobjs': statobjs})
    api.add_resource(TrapperDiscovery, '/api/trapperdiscovery/<zbxhost>',
                     endpoint='/trapperdiscovery/',
                     resource_class_kwargs={
                         'statobjs': statobjs,
                         'zabbix': zabbix,
                         'endpoints': endpoints,
                         'do_not_discover': dnd})
    api.add_resource(TrapperStats, '/api/trapperstats/<zbxhost>', endpoint='/trapperstats/',
                     resource_class_kwargs={
                         'statobjs': statobjs,
                         'zabbix': zabbix,
                         'endpoints': endpoints})
    api.add_resource(RequestLogger, '/api/logger/<loglevel>', endpoint='/logger/')
    app.run(host=backend['host'], port=backend['port'], debug=backend['debug'], threaded=True)

    logger.info('Job completed.')
