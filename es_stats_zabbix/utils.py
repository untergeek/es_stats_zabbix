import elasticsearch
from es_stats import *
import click
import sys
import logging

logger = logging.getLogger(__name__)

# Elasticsearch versions supported
version_max = (3, 0, 0)
version_min = (1, 0, 0)

class LogstashFormatter(logging.Formatter):
    # The LogRecord attributes we want to carry over to the Logstash message,
    # mapped to the corresponding output key.
    WANTED_ATTRS = {'levelname': 'loglevel',
                    'funcName': 'function',
                    'lineno': 'linenum',
                    'message': 'message',
                    'name': 'name'}

    def converter(self, timevalue):
        return time.gmtime(timevalue)

    def format(self, record):
        timestamp = '%s.%03dZ' % (
            self.formatTime(record, datefmt='%Y-%m-%dT%H:%M:%S'), record.msecs)
        result = {'message': record.getMessage(),
                  '@timestamp': timestamp}
        for attribute in set(self.WANTED_ATTRS).intersection(record.__dict__):
            result[self.WANTED_ATTRS[attribute]] = getattr(record, attribute)
        return json.dumps(result, sort_keys=True)

class Whitelist(logging.Filter):
    def __init__(self, *whitelist):
        self.whitelist = [logging.Filter(name) for name in whitelist]

    def filter(self, record):
        return any(f.filter(record) for f in self.whitelist)

def fix_types(config):
    """Fix 'None' to None and 'False' or 'True' to not be strings"""
    for k in config:
        if config[k] == 'None':
            config[k] = None
        if config[k] == 'False':
            config[k] = False
        if config[k] == 'True':
            config[k] = True
        if k == 'timeout' or k == 'port':
            config[k] = int(config[k])
    return config

def get_version(client):
    """
    Return the ES version number as a tuple.
    Omits trailing tags like -dev, or Beta

    :arg client: The Elasticsearch client connection
    :rtype: tuple
    """
    version = client.info()['version']['number']
    version = version.split('-')[0]
    if len(version.split('.')) > 3:
        version = version.split('.')[:-1]
    else:
       version = version.split('.')
    return tuple(map(int, version))

def check_version(client):
    """
    Verify version is within acceptable range.  Exit with error if it is not.

    :arg client: The Elasticsearch client connection
    """
    version_number = get_version(client)
    logger.debug('Detected Elasticsearch version {0}'.format(".".join(map(str,version_number))))
    if version_number >= version_max or version_number < version_min:
        click.echo(click.style('Expected Elasticsearch version range > {0} < {1}'.format(".".join(map(str,version_min)),".".join(map(str,version_max))), fg='red'))
        click.echo(click.style('ERROR: Incompatible with version {0} of Elasticsearch.  Exiting.'.format(".".join(map(str,version_number))), fg='red', bold=True))
        sys.exit(1)

def check_master(client, master_only=False):
    """
    Check if master node.  If not, exit with error code
    """
    if master_only and not is_master_node(client):
        logger.info('Master-only flag detected. Connected to non-master node. Aborting.')
        sys.exit(1)

def get_client(**kwargs):
    """Return an Elasticsearch client using the provided parameters

    """
    kwargs['master_only'] = False if not 'master_only' in kwargs else kwargs['master_only']
    kwargs['use_ssl'] = False if not 'use_ssl' in kwargs else kwargs['use_ssl']
    kwargs['ssl_no_validate'] = False if not 'ssl_no_validate' in kwargs else kwargs['ssl_no_validate']
    kwargs['certificate'] = False if not 'certificate' in kwargs else kwargs['certificate']
    logger.debug("kwargs = {0}".format(kwargs))
    logger.info('Initializing Elasticsearch client.')
    master_only = kwargs.pop('master_only')
    if kwargs['use_ssl']:
        if kwargs['ssl_no_validate']:
            kwargs['verify_certs'] = False # Not needed, but explicitly defined
        else:
            logger.info('Attempting to verify SSL certificate.')
            # If user provides a certificate:
            if kwargs['certificate']:
                kwargs['verify_certs'] = True
                kwargs['ca_certs'] = kwargs['certificate']
            else: # Try to use certifi certificates:
                try:
                    import certifi
                    kwargs['verify_certs'] = True
                    kwargs['ca_certs'] = certifi.where()
                except ImportError:
                    logger.warn('Unable to verify SSL certificate.')
    try:
        client = elasticsearch.Elasticsearch(**kwargs)
        # Verify the version is acceptable.
        check_version(client)
        # Verify "master_only" status, if applicable
        check_master(client, master_only=master_only)
        return client
    except Exception as e:
        logger.error('Connection failure. Exception: {0}'.format(e))
        click.echo(click.style('ERROR: Connection failure. Exception: {0}'.format(e), fg='red', bold=True))
        sys.exit(1)

def parse_key(zabbixkey):
    """Parse zabbix key into Tuple(api_type, node, key)"""
    api_type = zabbixkey.split('[')[0]
    # Take what's inside the brackets, removing the last char (])
    bracketed = zabbixkey.split('[')[1][:-1]
    # Check if there's a comma (for nodestats and nodeinfo)
    if ',' in bracketed:
        node = bracketed.split(',')[0]
        key = bracketed.split(',')[1]
    else:
        node = None
        key = bracketed
    logger.debug('API: {0}  Node: {1}  Key: {2}'.format(api_type, node, key))
    return (api_type, node, key)

def map_api(ztuple, client):
    """Return API object associated with api_type.  Requires ES client."""
    if ztuple[0] == 'health':
        return ClusterHealth(client)
    if ztuple[0] == 'clusterstats':
        return ClusterStats(client)
    if ztuple[0] == 'clusterstate':
        return ClusterState(client)
    if ztuple[0] == 'nodestats':
        return NodeStats(client)
    if ztuple[0] == 'nodeinfo':
        return NodeInfo(client)
    # If we haven't returned yet, that's bad
    logger.error('API type {0} not found. Exiting'.format(ztuple[0]))
    click.echo(click.style('API type {0} not found. Exiting'.format(ztuple[0]), fg='red', bold=True))
    sys.exit(1)
