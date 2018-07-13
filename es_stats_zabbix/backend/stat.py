"""
Stat module for flask_restful
"""

import json
import logging
from dotmap import DotMap
from flask import request
from flask_restful import Resource
from es_stats_zabbix.exceptions import EmptyResult
from es_stats_zabbix.helpers.utils import status_map

class Stat(Resource):
    """Stat Resource class for flask_restful"""
    def __init__(self, statobj):
        self.statobj = statobj
        # Turn <class 'es_stats.classes.ClusterHealth'> into just "ClusterHealth"
        statclass = str(type(statobj)).split('.')[-1].split("'")[0]
        self.logger = logging.getLogger('es_stats_zabbix.Stat.{0}'.format(statclass))

    def get(self, key):
        """GET method"""
        return self.post(key)

    def post(self, key):
        """POST method"""
        self.logger.debug('request.data contents = {}'.format(request.data))
        node = None
        if request.data != b'':
            # Must decode to 'utf-8' for older versions of Python
            json_data = json.loads(request.data.decode('utf-8'))
            node = json_data['node'] if 'node' in json_data else None
        self.logger.debug('Node = {0} -- key = {1}'.format(node, key))
        result = self.statobj.get(key, name=node)
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
