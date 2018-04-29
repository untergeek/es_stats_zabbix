import logging
from es_client import Builder
from es_client.helpers.schemacheck import SchemaCheck
from es_client.helpers.utils import get_yaml, prune_nones
from es_stats_zabbix.defaults.config import schema
from es_stats_zabbix.defaults.settings import apis
from es_stats_zabbix.exceptions import ConfigurationError
from es_stats_zabbix.helpers.logtools import set_logging

logger = logging.getLogger(__name__)

TOP_LEVEL = ['elasticsearch', 'logging', 'backend']
CLIENT_KEYS = [
    'host', 'port', 'url_prefix', 'use_ssl', 'ca_certs', 'client_cert', 'client_key', 'verify_certs',
    'username', 'password', 'timeout', 
]
ELASTICSEARCH_KEYS = ['client', 'master_only']
LOGGING_KEYS = ['loglevel', 'logfile', 'logformat', 'blacklist']
BACKEND_KEYS = ['apihost', 'apiport', 'apidebug', 'cache_timeout']

def get_client(cfg):
    """
    Return an Elasticsearch client object from a configuration dictionary
    """
    try:
        return Builder(cfg).client
    except Exception as e:
        msg = 'Failed to connect to Elasticsearch: Exception: {0}'.format(e)
        logger.error(msg)
        raise ConfigurationError(msg)

def check_schema(cfg, key):
    try:
        return SchemaCheck(
            {key: prune_nones(cfg[key])}, 
            schema(key),
            '{0} Configuration'.format(key.title()), 
            key
        ).result()
    except Exception as e:
        msg = 'Failed to configure {0}: Exception: {1}'.format(key, e)
        logger.error(msg)
        raise ConfigurationError(msg)

def configure_logging(cfg):
    """
    Read logging configuration and initiate logging.
    """
    set_logging(check_schema(cfg, 'logging')['logging'])

def get_backend(cfg):
    """
    Wrapper to get schema-validated backend configuration from :func:~`es_stats_zabbix.helpers.config.check_schema`
    """
    return check_schema(cfg, 'backend')['backend']

def get_dnd(cfg):
    """
    Wrapper to get schema-validated do_not_discover configuration from :func:~`es_stats_zabbix.helpers.config.check_schema`
    """
    return check_schema(cfg, 'do_not_discover')['do_not_discover']

def config_override(ctx):
    params = prune_nones(ctx.params)
    if 'config' in params:
        config_dict = get_yaml(params['config'])
    else:
        config_dict = {'elasticsearch':{}, 'logging':{}, 'backend':{}, 'do_not_discover': {'health': ['status']}}
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
                            # We can supply multiple hosts on the command line, but they come as a tuple
                            if subk == 'host':
                                if params[subk]: # This "None" doesn't get pruned, it's an empty tuple
                                    config_dict[toplevel][k]['hosts'] = list(params[subk])
                            else:
                                config_dict[toplevel][k][subk] = params[subk]
        if toplevel == 'logging':
            for k in LOGGING_KEYS:
                if k in params:
                        config_dict[toplevel][k] = params[k]
        if toplevel == 'backend':
            for k in BACKEND_KEYS:
                if k in params:
                    if k[:3] == 'api':
                        renamed = k[3:] # Remove 'api' from 'apihost', 'apiport', and 'apidebug'
                        config_dict[toplevel][renamed] = params[k]
                    else: # Cover cache_timeout this way
                        config_dict[toplevel][k] = params[k]
    return config_dict
