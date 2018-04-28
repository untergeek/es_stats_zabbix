from six import string_types
# from socket import getfqdn
from voluptuous import All, Any, Boolean, Coerce, Optional, Range, Schema

# pylint: disable=no-value-for-parameter
DEFAULTS = {
    # Configuration file: logging
    'logging': {
        Optional(
            'loglevel', default='INFO'): Any(None,
            'NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL',
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
    # Configuration file: do_not_discover
    'do_not_discover': {
        Optional('health'): Any(list),
        Optional('clusterstate'): Any(list),
        Optional('clusterstats'): Any(list),
        Optional('nodeinfo'): Any(list),
        Optional('nodestats'): Any(list),
    }
}

def schema(key):
    return Schema({ Optional(key, default={}): DEFAULTS[key] })

