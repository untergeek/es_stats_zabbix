"""
Class that permits log messages to be sent back to the REST API by other Resources
"""

import json
import logging
from flask import request
from flask_restful import Resource

class RequestLogger(Resource):
    """
    RequestLogger Resource class for flask_restful
    """
    def __init__(self):
        self.logger = logging.getLogger('esz.RequestLogger')
        self.keymap = {
            'DEBUG': self.logger.debug,
            'INFO': self.logger.info,
            'WARNING': self.logger.warning,
            'ERROR': self.logger.error,
            'CRITICAL': self.logger.critical,
        }

    def post(self, loglevel):
        """POST method"""
        if request.data != b'':
            # Must decode to 'utf-8' for older versions of Python
            json_data = json.loads(request.data.decode('utf-8'))
            # If multiple keys were posted, log them all as specified
            for k in json_data:
                self.keymap[loglevel.upper()]('{0}: {1}'.format(k, json_data[k]))
        else:
            self.keymap[loglevel.upper()]('Received no POST data')
