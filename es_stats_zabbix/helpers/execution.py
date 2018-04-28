import json
import logging
from dotmap import DotMap
from es_stats.classes import ClusterHealth, ClusterState, ClusterStats, NodeInfo, NodeStats
from es_stats.exceptions import NotFound
from es_stats_zabbix.exceptions import EmptyResult, ConfigurationError
from es_stats_zabbix.helpers.config import configure_logging, get_backend, get_client, get_dnd
from es_stats_zabbix.helpers.batch import get_endpoints
from es_stats_zabbix.helpers.utils import status_map
from flask import Flask, request
from flask_restful import Resource, Api

logger = logging.getLogger(__name__)

class RequestLogger(Resource):
    def __init__(self):
        self.logger = logging.getLogger('es_stats_zabbix.RequestLogger')
        self.keymap = {
            'DEBUG': self.logger.debug,
            'INFO': self.logger.info,
            'WARNING': self.logger.warning,
            'ERROR': self.logger.error,
            'CRITICAL': self.logger.critical,
        }

    def post(self, loglevel):
        # self.logger.debug('request.data contents = {}'.format(request.data))
        if request.data != b'':
            try:
                json_data = json.loads(request.data)
            except json.decoder.JSONDecodeError:
                self.logger.error('Unable to parse JSON: {0}'.format(request.data))
            try:
                # If multiple keys were posted, log them all as specified
                for k in json_data:
                    self.keymap[loglevel.upper()]('{0}: {1}'.format(k, json_data[k]))
            except:
                self.logger.error('Unable to share message')
        else:
            self.keymap[loglevel.upper()]('Received no POST data')

class Discovery(Resource):
    def __init__(self, client, do_not_discover):
        self.client = client
        self.dnd = do_not_discover
        self.logger = logging.getLogger('es_stats_zabbix.Discovery')

    def get(self, api):
        return self.post(api)

    def post(self, api):
        self.logger.debug('request.data contents = {}'.format(request.data))
        valuetype = None
        if request.data != b'':
            try:
                json_data = json.loads(request.data)
            except json.decoder.JSONDecodeError:
                return 'unable to decode JSON', 400    
            valuetype = json_data['valuetype'] if 'valuetype' in json_data else None
        self.logger.debug('valuetype = {0} -- api = {1}'.format(valuetype, api))
        endpoints = get_endpoints(self.client, api, valuetype=valuetype)
        macros = []
        macroname = '{#' + valuetype.upper() + '}' if valuetype else '{#ENDPOINT}'
        for ep in endpoints[api]:
            if api in self.dnd and ep in self.dnd[api]:
                continue
            macros.append({macroname: ep})
        return { 'data': macros }


class Stat(Resource):
    def __init__(self, statobj):
        self.statobj = statobj
        # Turn <class 'es_stats.classes.ClusterHealth'> into just "ClusterHealth"
        statclass = str(type(statobj)).split('.')[-1].split("'")[0]
        self.logger = logging.getLogger('es_stats_zabbix.Stat.{0}'.format(statclass))

    def get(self, key):
        return self.post(key)

    def post(self, key):
        self.logger.debug('request.data contents = {}'.format(request.data))
        node = None
        if request.data != b'':
            try:
                json_data = json.loads(request.data)
            except json.decoder.JSONDecodeError:
                return 'unable to decode JSON', 400
            node = json_data['node'] if 'node' in json_data else None
        self.logger.debug('Node = {0} -- key = {1}'.format(node, key))
        try:
            result = self.statobj.get(key, name=node)
        except NotFound as e:
            r = {'message':'{0}'.format(e)}
            return r, 404
        # Remap for `status`
        if key == 'status': 
            result = status_map(result)
        if result == DotMap():
            return {'message':'ZBX_NOTFOUND'}, 404
        if str(result).strip().lower() == 'false':
            return 0, 200
        if str(result).strip().lower() == 'true':
            return 1, 200
        if result == '':
            self.logger.error('Empty value')
            raise EmptyResult('No result received.')
        return result, 200

def run(config_dict):
    """
    Actually run.
    """
    configure_logging(config_dict)
    backend = get_backend(config_dict)
    dnd = get_dnd(config_dict)
    ct = backend['cache_timeout']
    # Now that logging is enabled, let's attempt an Elasticsearch Client connection:
    client = get_client(config_dict)
    info = client.info()
    logger.info(
        'Connected to cluster: "{0}" through (initial) node: "{1}".  Elasticsearch version: "{2}"'.format(info['cluster_name'], info['name'], info['version']['number'])
    )
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(Stat, '/api/health/<key>', endpoint='/health/',
        resource_class_kwargs={'statobj': ClusterHealth(client, cache_timeout=ct)})
    api.add_resource(Stat, '/api/clusterstate/<key>', endpoint='/clusterstate/',
        resource_class_kwargs={'statobj': ClusterState(client, cache_timeout=ct)})
    api.add_resource(Stat, '/api/clusterstats/<key>', endpoint='/clusterstats/',
        resource_class_kwargs={'statobj': ClusterStats(client, cache_timeout=ct)})
    api.add_resource(Stat, '/api/nodeinfo/<key>', endpoint='/nodeinfo/',
        resource_class_kwargs={'statobj': NodeInfo(client, cache_timeout=ct)})
    api.add_resource(Stat, '/api/nodestats/<key>', endpoint='/nodestats/',
        resource_class_kwargs={'statobj': NodeStats(client, cache_timeout=ct)})
    api.add_resource(Discovery, '/api/discovery/<api>', endpoint='/discovery/',
        resource_class_kwargs={'client': client, 'do_not_discover': dnd})
    api.add_resource(RequestLogger, '/api/logger/<loglevel>', endpoint='/logger/')
    app.run(host=backend['host'], port=backend['port'], debug=backend['debug'], threaded=True)
    
    logger.info('Job completed.')