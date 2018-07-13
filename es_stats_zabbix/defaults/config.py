"""
Configuration data and functions
"""

from socket import getfqdn
from six import string_types
from voluptuous import All, Any, Boolean, Coerce, Optional, Range, Schema

# pylint: disable=no-value-for-parameter
DEFAULTS = {
    # Configuration file: logging
    'logging': {
        Optional('loglevel', default='INFO'):
            Any(None, 'NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL',
                All(Coerce(int), Any(0, 10, 20, 30, 40, 50))
               ),
        Optional('logfile', default=None): Any(None, *string_types),
        Optional('logformat', default='default'): Any('default', 'json', 'logstash'),
        Optional('blacklist', default=['elasticsearch', 'urllib3']): Any(None, list),
    },
    # Configuration file: backend
    'backend': {
        Optional('host', default='127.0.0.1'): Any(None, *string_types),
        Optional('port', default=7600): All(Coerce(int), Range(min=1025, max=65534)),
        Optional('debug', default=False): Boolean(),
        Optional('cache_timeout', default=60): All(Coerce(int), Range(min=1, max=600))
    },
    # Configuration file: zabbix
    'zabbix': {
        Optional('ServerActive', default='127.0.0.1'): Any(None, *string_types),
        Optional('ServerPort', default=10051): All(Coerce(int), Range(min=1025, max=65534)),
        Optional('LogType', default='file'): Any('file', 'system', 'console'),
        Optional('LogFile', default='/tmp/zabbix_agentd.log'): Any(None, *string_types),
        Optional('DebugLevel', default=3): All(Coerce(int), Range(min=1, max=5)),
        Optional('Timeout', default=3): All(Coerce(int), Range(min=1, max=30)),
        Optional('Hostname', default=getfqdn()): Any(None, *string_types),
        Optional('TLSConnect', default='unencrypted'): Any('unencrypted', 'psk', 'cert'),
        Optional('TLSCAFile'): Any(None, *string_types),
        Optional('TLSCertFile'): Any(None, *string_types),
        Optional('TLSCRLFile'): Any(None, *string_types),
        Optional('TLSKeyFile'): Any(None, *string_types),
        Optional('TLSServerCertIssuer'): Any(None, *string_types),
        Optional('TLSServerCertSubject'): Any(None, *string_types),
        Optional('TLSPSKIdentity'): Any(None, *string_types),
        Optional('TLSPSKFile'): Any(None, *string_types),
    },
    # Configuration file: do_not_discover
    'do_not_discover': {
        Optional('health'): Any(list),
        Optional('clusterstate'): Any(list),
        Optional('clusterstats'): Any(list),
        Optional('nodeinfo'): Any(list),
        Optional('nodestats'): Any(list),
    },
    # Configuration file: endpoints
    'endpoints': {
        Optional('cluster'): Any(dict),
        Optional('coordinating'): Any(dict),
        Optional('master'): Any(dict),
        Optional('data'): Any(dict),
        Optional('ml'): Any(dict),
        Optional('ingest'): Any(dict),
    }
}

def schema(key):
    """Define voluptuous schemas by provided key"""
    return Schema({Optional(key, default={}): DEFAULTS[key]})
