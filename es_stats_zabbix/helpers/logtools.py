"""
Logging module
"""

import sys
import time
import logging
import json
from es_client.helpers.utils import ensure_list

class LogstashFormatter(logging.Formatter):
    """Set up log formatting for JSON or plain or debug"""
    # The LogRecord attributes we want to carry over to the Logstash message,
    # mapped to the corresponding output key.
    WANTED_ATTRS = {'levelname': 'loglevel',
                    'funcName': 'function',
                    'lineno': 'linenum',
                    'message': 'message',
                    'name': 'name'}

    # def converter(self, timevalue):
    #     return time.gmtime(timevalue)

    def format(self, record):
        self.converter = time.gmtime
        timestamp = '%s.%03dZ' % (
            self.formatTime(record, datefmt='%Y-%m-%dT%H:%M:%S'), record.msecs)
        result = {'message': record.getMessage(),
                  '@timestamp': timestamp}
        for attribute in set(self.WANTED_ATTRS).intersection(record.__dict__):
            result[self.WANTED_ATTRS[attribute]] = getattr(record, attribute)
        return json.dumps(result, sort_keys=True)

class Whitelist(logging.Filter):
    """Define a whitelist of acceptable log sources"""
    def __init__(self, *whitelist):
        self.whitelist = [logging.Filter(name) for name in whitelist]

    def filter(self, record):
        return any(f.filter(record) for f in self.whitelist)

class Blacklist(Whitelist):
    """Define a blacklist of blockable log sources"""
    def filter(self, record):
        return not Whitelist.filter(self, record)

class LogInfo(object):
    """LogInfo class to establish the root logger"""
    def __init__(self, cfg):
        cfg['loglevel'] = 'INFO' if not 'loglevel' in cfg else cfg['loglevel']
        cfg['logfile'] = None if not 'logfile' in cfg else cfg['logfile']
        cfg['logformat'] = 'default' if not 'logformat' in cfg else cfg['logformat']
        self.numeric_log_level = getattr(logging, cfg['loglevel'].upper(), None)
        self.format_string = '%(asctime)s %(levelname)-9s %(message)s'
        if not isinstance(self.numeric_log_level, int):
            raise ValueError('Invalid log level: {0}'.format(cfg['loglevel']))

        self.handler = logging.StreamHandler(
            open(cfg['logfile'], 'a') if cfg['logfile'] else sys.stdout
        )

        if self.numeric_log_level == 10: # DEBUG
            self.format_string = (
                '%(asctime)s %(levelname)-9s %(name)22s '
                '%(funcName)22s:%(lineno)-4d %(message)s'
            )

        if cfg['logformat'] == 'json' or cfg['logformat'] == 'logstash':
            self.handler.setFormatter(LogstashFormatter())
        else:
            self.handler.setFormatter(logging.Formatter(self.format_string))

def set_logging(log_opts):
    """Set up the root handler"""
    from logging import NullHandler
    # Set up logging
    loginfo = LogInfo(log_opts)
    logging.root.addHandler(loginfo.handler)
    logging.root.setLevel(loginfo.numeric_log_level)
    # Set up NullHandler() to handle nested elasticsearch.trace Logger
    # instance in elasticsearch python client
    logging.getLogger('elasticsearch.trace').addHandler(NullHandler())
    if log_opts['blacklist']:
        for bl_entry in ensure_list(log_opts['blacklist']):
            for handler in logging.root.handlers:
                handler.addFilter(Blacklist(bl_entry))
