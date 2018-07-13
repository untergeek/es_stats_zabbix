"""
Discovery-related Resource Classes for flask_restful
"""

import json
import logging
from flask import request
from flask_restful import Resource
from es_stats_zabbix.exceptions import NotFound
from es_stats_zabbix.defaults.settings import APIS
from es_stats_zabbix.helpers.batch import get_endpoints, lldoutput, macrogen
from es_stats_zabbix.helpers.config import extract_endpoints
from es_stats_zabbix.helpers.utils import get_nodeid, get_cluster_macros, get_node_macros

class Discovery(Resource):
    """
    Endpoint Discovery Resource Class for flask_restful
    """
    def __init__(self, statobjs, do_not_discover, endpoints):
        self.statobjs = statobjs
        self.dnd = do_not_discover
        self.raw_endpoints = endpoints
        self.logger = logging.getLogger('esz.Discovery')

    def get(self):
        """GET method"""
        return self.post()

    def post(self):
        """POST method"""
        endpoints = extract_endpoints(self.raw_endpoints)
        node = None
        show_all = False
        self.logger.debug('request.data contents = {}'.format(request.data))
        if request.data != b'':
            # Must decode to 'utf-8' for older versions of Python
            json_data = json.loads(request.data.decode('utf-8'))
            node = json_data['node'] if 'node' in json_data else None
            show_all = json_data['show_all'] if 'show_all' in json_data else False
        results = macrogen(self.statobjs, self.dnd, node=node,
                           included=None if show_all else endpoints)
        llddata = lldoutput(results)
        return {'data': llddata}

class ClusterDiscovery(Resource):
    """
    Cluster and Node Discovery Resource Class for flask_restful
    """
    def __init__(self, statobjs):
        self.logger = logging.getLogger('esz.ClusterDiscovery')
        self.statobjs = statobjs
        self.statobj = statobjs['nodeinfo']
        self.nodeinfo = self.statobj.cached_read('nodeinfo')['nodes']

    def get(self, value):
        """GET method"""
        return self.post(value)

    def post(self, value):
        """POST method"""
        self.logger.debug('request.data contents = {}'.format(request.data))
        flag = None
        if request.data != b'':
            # Must decode to 'utf-8' for older versions of Python
            json_data = json.loads(request.data.decode('utf-8'))
            flag = json_data['flag'] if 'flag' in json_data else None
        if flag:
            # Placeholder if needed.
            pass
        macros = []
        if value == 'cluster':
            nodeid = list(self.nodeinfo.keys())[0]
            self.logger.debug('Value is "cluster."  Returning LLD data for the cluster...')
            self.logger.debug('Using nodeid {0} for cluster data'.format(nodeid))
            macros.append(get_cluster_macros(self.statobj, nodeid))
        elif value == 'nodes':
            self.logger.debug('Value is "nodes."  Returning LLD data for all discovered nodes...')
            for nodeid in self.nodeinfo:
                macros.append(get_cluster_macros(self.statobj, nodeid))
        return {'data': macros}

class NodeDiscovery(Resource):
    """
    Node Discovery Resource Class for flask_restful
    """
    def __init__(self, statobjs):
        self.logger = logging.getLogger('esz.NodeDiscovery')
        self.statobjs = statobjs
        self.statobj = statobjs['nodeinfo']
        self.nodeinfo = self.statobj.cached_read('nodeinfo')['nodes']

    def get(self, node):
        """GET method"""
        return self.post(node)

    def post(self, node):
        """POST method"""
        self.logger.debug('request.data contents = {}'.format(request.data))
        flag = None
        if request.data != b'':
            # Must decode to 'utf-8' for older versions of Python
            json_data = json.loads(request.data.decode('utf-8'))
            flag = json_data['flag'] if 'flag' in json_data else None
        try:
            nodeid = get_nodeid(self.statobjs, node)
        except NotFound:
            return {'data': []}
        if flag:
            pass # Placeholder to quiet pylint
        macros = get_node_macros(self.statobj, nodeid)
        return {'data': macros}

class DisplayEndpoints(Resource):
    """
    Endpoint Display Resource Class for flask_restful
    """
    def __init__(self, statobjs):
        self.statobjs = statobjs
        self.logger = logging.getLogger('esz.DisplayEndpoints')

    def get(self):
        """GET method"""
        return self.post()

    def post(self):
        """POST method"""
        node = None
        self.logger.debug('request.data contents = {}'.format(request.data))
        if request.data != b'':
            # Must decode to 'utf-8' for older versions of Python
            json_data = json.loads(request.data.decode('utf-8'))
            node = json_data['node'] if 'node' in json_data else None
        results = {}
        node = node if node else self.statobjs['health'].local_name
        for api in APIS:
            results[api] = get_endpoints(self.statobjs, api, node=node)[api]
        self.logger.debug('RESULTS = {0}'.format(results))
        return results
