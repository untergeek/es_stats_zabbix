"""
Trapper module for flask_restful
"""

import json
import logging
from copy import deepcopy
from dotmap import DotMap
from flask import request
from flask_restful import Resource
from es_stats_zabbix.defaults.settings import APIS
from es_stats_zabbix.helpers.batch import lldoutput, macrogen
from es_stats_zabbix.helpers.config import extract_endpoints
from es_stats_zabbix.helpers.utils import get_nodeid, status_map, true_nodetypes
from es_stats_zabbix.helpers.zabbix import ZbxSendObject


def shipit(zbxconf, zbxhost, data, data_type='items'):
    """
    Do the zabbix_trapper shipping via ZbxSendObject, which uses protobix
    """
    try:
        zso = ZbxSendObject(zbxconf)
        _, server_failure, _, failed, _, _ = zso.zbx_sender(
            zbxhost, data, data_type=data_type)
    except ConnectionRefusedError:
        return (
            'Unable to connect to Zabbix server at '
            '{0}'.format(zbxconf['ServerActive'])), 500

    # If server_failure is 1, we were unable to communicate with the Zabbix server
    if server_failure > 0:
        return 1, 500
    # Return the number of items that failed to be picked up by Zabbix (hopefully zero!)
    return failed, 200

def get_node_endpoints(zbxhost, raw_endpoints, statobjs):
    """Return a tuple of a node name and the endpoints to extract"""
    node = zbxhost
    if zbxhost == statobjs['health'].get('cluster_name'):
        node = statobjs['health'].local_name
        endpoints = {'cluster': raw_endpoints['cluster']}
    else:
        node_endpoints = deepcopy(raw_endpoints)
        del node_endpoints['cluster']
        # Determine which nodetypes are "True" for the given node
        valid_nodetypes = true_nodetypes(statobjs['nodeinfo'], get_nodeid(statobjs, node))
        for nodetype in list(node_endpoints.keys()):
            if nodetype not in valid_nodetypes:
                del node_endpoints[nodetype]
        endpoints = node_endpoints
    return node, endpoints

class TrapperDiscovery(Resource):
    """TrapperDiscovery Resource class for flask_restful"""
    def __init__(self, statobjs, zabbix, endpoints, do_not_discover):
        self.logger = logging.getLogger('esz.TrapperDiscovery')
        self.statobjs = statobjs
        self.zabbix = zabbix
        self.raw_endpoints = endpoints
        self.dnd = do_not_discover

    def get(self, zbxhost):
        """GET method"""
        return self.post(zbxhost)

    def post(self, zbxhost):
        """POST method"""
        node, endpoints = get_node_endpoints(zbxhost, self.raw_endpoints, self.statobjs)
        endpoints = extract_endpoints(endpoints)
        results = macrogen(
            self.statobjs, self.dnd, node=node, included=endpoints)
        llddata = lldoutput(results)
        exit_code, http_code = shipit(
            self.zabbix, zbxhost, llddata, data_type='lld')
        return exit_code, http_code

class TrapperStats(Resource):
    """TrapperStats Resource class for flask_restful"""
    def __init__(self, statobjs, zabbix, endpoints):
        self.statobjs = statobjs
        self.raw_endpoints = endpoints
        self.zabbix = zabbix
        self.client = statobjs['health'].client
        self.logger = logging.getLogger('esz.TrapperStats')
        self.nodeinfo = self.client.nodes.info()['nodes']
        self.debug = False
        if logging.getLogger().getEffectiveLevel() == 10:
            self.debug = True

    def _get_kv(self, api, entry, node):
        value = self.statobjs[api].get(entry, name=node)
        self.logger.debug('Value: {0}'.format(value))
        # Map cluster health status to Zabbix expected values
        if entry == 'status':
            value = status_map(value)
        # Do nothing for nested or DotMap values
        if value == DotMap():
            self.logger.debug('Nested or value for {0}:{1}'.format(api, entry))
            return None, None
        # Set boolean and bool-ish values to firm 0/1
        if str(value).strip().lower() == 'false':
            value = 0
        if str(value).strip().lower() == 'true':
            value = 1
        # Do nothing for empty values
        if value == '':
            self.logger.debug('Empty value for {0}:{1}'.format(api, entry))
            return None, None
        # Truncate floating point values at 3 places
        if isinstance(value, float):
            value = float("{0:.3f}".format(value))
        key = 'es_stats[{0},{1},]'.format(api, entry)
        return key, value

    def get(self, zbxhost):
        """GET method"""
        self.logger.debug('We are doing a GET, but shouldn\'t be')
        return self.post(zbxhost)

    def post(self, zbxhost):
        """POST method"""
        self.logger.debug('request.data contents = {}'.format(request.data))
        node, endpoints = get_node_endpoints(zbxhost, self.raw_endpoints, self.statobjs)
        if request.data != b'':
            # Must decode to 'utf-8' for older versions of Python
            json_data = json.loads(request.data.decode('utf-8'))
            nodetype = json_data['nodetype'] if 'nodetype' in json_data else None
            interval = json_data['interval'] if 'interval' in json_data else '60s'
        # Get the result here.
        # We need all the results specified in the YAML file.
        # endpoints:
        #   nodetype:
        #     interval:
        #       api:
        #         - array of keys
        stats = {}
        if nodetype in endpoints:
            if interval in endpoints[nodetype]:
                for api in APIS:
                    if api in endpoints[nodetype][interval]:
                        for entry in endpoints[nodetype][interval][api]:
                            key, value = self._get_kv(api, entry, node)
                            if key:
                                stats[key] = value
        exit_code, http_code = shipit(self.zabbix, zbxhost, stats)
        return exit_code, http_code
