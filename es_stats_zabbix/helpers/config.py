"""
Configuration specific modules and functions
"""

import logging
from es_client import Builder
from es_client.helpers.schemacheck import SchemaCheck
from es_client.helpers.utils import get_yaml, prune_nones
from es_stats_zabbix.defaults.config import schema
from es_stats_zabbix.defaults.settings import apis
from es_stats_zabbix.exceptions import ConfigurationError
from es_stats_zabbix.helpers.logtools import set_logging

LOGGER = logging.getLogger(__name__)

TOP_LEVEL = ['elasticsearch', 'logging', 'backend', 'zabbix', 'endpoints']
CLIENT_KEYS = [
    'host', 'port', 'url_prefix', 'use_ssl', 'ca_certs', 'client_cert', 'client_key',
    'verify_certs', 'username', 'password', 'timeout',
]
ELASTICSEARCH_KEYS = ['client', 'master_only']
LOGGING_KEYS = ['loglevel', 'logfile', 'logformat', 'blacklist']
BACKEND_KEYS = ['apihost', 'apiport', 'apidebug', 'cache_timeout']
ZBXKEYMAP = {
    'zbx_serveractive': 'ServerActive',
    'zbx_serverport': 'ServerPort',
    'zbx_logtype': 'LogType',
    'zbx_logfile': 'LogFile',
    'zbx_debuglevel': 'DebugLevel',
    'zbx_timeout': 'Timeout',
    'zbx_hostname': 'Hostname',
    'zbx_tlsconnect': 'TLSConnect',
    'zbx_tlscafile': 'TLSCAFile',
    'zbx_tlscertfile': 'TLSCertFile',
    'zbx_tlscrlfile': 'TLSCRLFile',
    'zbx_tlskeyfile': 'TLSKeyFile',
    'zbx_tlsservercertissuer': 'TLSServerCertIssuer',
    'zbx_tlsservercertsubject': 'TLSServerCertSubject',
    'zbx_tlspskidentity': 'TLSPSKIdentity',
    'zbx_tlspskfile': 'TLSPSKFile',
}

def default_config():
    """Provide a default configuration"""
    value = {'do_not_discover': {'health': ['status']}}
    for k in TOP_LEVEL:
        value[k] = {}
    return value

def get_client(cfg):
    """
    Return an Elasticsearch client object from a configuration dictionary
    """
    try:
        return Builder(cfg).client
    except Exception as err:
        msg = 'Failed to connect to Elasticsearch: Exception: {0}'.format(err)
        LOGGER.error(msg)
        raise ConfigurationError(msg)

def check_schema(cfg, key):
    """
    Ensure that the schema passes muster
    """
    try:
        return SchemaCheck(
            {key: prune_nones(cfg[key])},
            schema(key),
            '{0} Configuration'.format(key.title()),
            key
        ).result()
    except Exception as err:
        msg = 'Failed to configure {0}: Exception: {1}'.format(key, err)
        LOGGER.error(msg)
        raise ConfigurationError(msg)

def configure_logging(cfg):
    """
    Read logging configuration and initiate logging.
    """
    set_logging(check_schema(cfg, 'logging')['logging'])

def get_config(cfg, key):
    """
    Wrapper to get schema-validated values from :func:~`es_stats_zabbix.helpers.config.check_schema`
    """
    return check_schema(cfg, key)[key]

def config_override(ctx):
    """
    Override the settings in the config file with the options provided at the command-line
    """
    params = prune_nones(ctx.params)
    if 'config' in params:
        config_dict = get_yaml(params['config'])
    else:
        config_dict = default_config()
    for toplevel in TOP_LEVEL:
        if toplevel == 'elasticsearch':
            for k in ELASTICSEARCH_KEYS:
                if k == 'master_only':
                    if k in params:
                        config_dict[toplevel][k] = params[k]
                else:
                    if not k in config_dict[toplevel]:
                        config_dict[toplevel][k] = {}
                    for subk in CLIENT_KEYS:
                        if subk in params:
                        # If we supply multiple hosts on the command line, they come as a tuple
                            if subk == 'host':
                                if params[subk]:
                                    # This "None" doesn't get pruned, it's an empty tuple
                                    config_dict[toplevel][k]['hosts'] = list(params[subk])
                            else:
                                config_dict[toplevel][k][subk] = params[subk]
        if toplevel == 'logging':
            for k in LOGGING_KEYS:
                if k in params:
                    config_dict[toplevel][k] = params[k]
        if toplevel == 'zabbix':
            # In order to prevent the elasticsearch and zabbix key names from
            # colliding, all zabbix keys were prefaced with 'zbx_'.
            # We have to strip the 'zbx_' away again, and remap back to the
            # CamelCase versions here.
            for k in list(ZBXKEYMAP.keys()):
                if k in params:
                    config_dict[toplevel][ZBXKEYMAP[k]] = params[k]
        if toplevel == 'backend':
            for k in BACKEND_KEYS:
                if k in params:
                    if k[:3] == 'api':
                        renamed = k[3:] # Remove 'api' from 'apihost', 'apiport', and 'apidebug'
                        config_dict[toplevel][renamed] = params[k]
                    else: # Cover cache_timeout this way
                        config_dict[toplevel][k] = params[k]
    return config_dict

def extract_endpoints(data):
    """
    Turn the dictionary of endpoints from the config file into a list of all endpoints.
    """
    endpoints = []
    for nodetype in data:
        for interval in data[nodetype]:
            for api in data[nodetype][interval]:
                endpoints += (
                    data[nodetype][interval][api]
                )
    return endpoints
