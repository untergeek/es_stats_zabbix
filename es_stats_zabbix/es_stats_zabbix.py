import os, sys
import click
import kaptan
import elasticsearch
from es_stats import *
from .utils import *
from ._version import __version__
import logging

try:
    from logging import NullHandler
except ImportError:
    from logging import Handler

    class NullHandler(Handler):
        def emit(self, record):
            pass


@click.group()
@click.option('--configuration', help='Path to configuration file', default=os.path.join(os.getcwd(), 'es_stats_zabbix.ini'))
@click.option('--debug', is_flag=True, help='Debug mode', default=False)
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, configuration, debug):
    """
    Get Elasticsearch stats from es_stats and send them to Zabbix
    """

    config = kaptan.Kaptan(handler='ini')
    try:
        config.import_config(configuration)
    except Exception as e:
        click.echo(click.style(
            'Error: Could not open configuration file at {0}'.format(configuration),
            fg='red', bold=True)
        )
        sys.exit(1)

    # Override debug setting in config file, if used.
    if debug:
        # debug = True
        pass
    else:
        if config.get('logging.debug') == 'True':
            debug = True
        else:
            debug = False

    # Setup logging
    if debug or config.get('logging.loglevel').upper() == 'DEBUG':
        numeric_log_level = logging.DEBUG
        format_string = '%(asctime)s %(levelname)-9s %(name)22s %(funcName)22s:%(lineno)-4d %(message)s'
    else:
        numeric_log_level = getattr(logging, config.get('logging.loglevel').upper(), None)
        format_string = '%(asctime)s %(levelname)-9s %(message)s'
        if not isinstance(numeric_log_level, int):
            raise ValueError('Invalid log level: {0}'.format(config.get('logging.loglevel')))

    handler = logging.StreamHandler(
        open(config.get('logging.logfile'), 'a') if not config.get('logging.logfile') == 'None' else sys.stdout)
    if config.get('logging.logformat') == 'logstash':
        handler.setFormatter(LogstashFormatter())
    else:
        handler.setFormatter(logging.Formatter(format_string))
    logging.root.addHandler(handler)
    logging.root.setLevel(numeric_log_level)
    logger = logging.getLogger('es_stats_zabbix')

    logger.info('Job starting.')
    logger.debug('Logging config args: {0}'.format(config.get('logging')))
    # Fix bool and integer values to be correct
    client_args = fix_types(config.get('elasticsearch'))
    logger.debug('Elasticsearch config args: {0}'.format(client_args))

    # Test whether certificate is a valid file path
    if client_args['use_ssl'] is True and client_args['certificate'] is not None:
        try:
            open(client_args['certificate'], 'r')
        except IOError:
            click.echo(
                click.style(
                    'Error: Could not open certificate at {0}'.format(client_args['certificate']),
                    fg='red', bold=True)
            )
            sys.exit(1)

    # Filter out logging from Elasticsearch and associated modules by default
    if not debug:
        for handler in logging.root.handlers:
            handler.addFilter(
                Whitelist('root', '__main__', 'es_stats_zabbix', 'zbxsender')
            )

    # Setting up NullHandler to handle nested elasticsearch.trace Logger
    # instance in elasticsearch python client
    logging.getLogger('elasticsearch.trace').addHandler(NullHandler())

    # Put elasticsearch client into ctx.obj['client']
    ctx.obj['client'] = get_client(**client_args)

    # Put batch configuration into ctx.obj['batches']
    batches = config.get()
    del batches["elasticsearch"]
    del batches["logging"]
    ctx.obj['batches'] = batches

@cli.command(short_help="Single item mode")
@click.argument('zabbixkey', nargs=1, required=True)
@click.pass_context
def single(ctx, zabbixkey):
    """Obtain and return value associated with zabbix key"""
    logger = logging.getLogger('es_stats_zabbix') # Since logging is set up in cli()
    logger.info('Single key: {0}'.format(zabbixkey))
    ztuple = parse_key(zabbixkey)
    apiobj = map_api(ztuple, ctx.obj['client'])
    result = apiobj.get(ztuple[2], name=ztuple[1])
    logger.debug('Result = {0}'.format(result))
    if result == DotMap():
        click.echo('ZBX_NOTSUPPORTED')
    else:
        click.echo(result)
    logger.info('Job completed.')

@cli.command(short_help="Batch mode")
@click.option('--name', help="Batch name from within configuration file.", default="batch")
@click.pass_context
def batch(ctx, name):
    """Send values in batch to zabbix_host (server defined in config file)"""
    logger = logging.getLogger('es_stats_zabbix') # Since logging is set up in cli()
    logger.debug('Batch mode with named batch: {0}'.format(name))
    if name not in ctx.obj['batches']:
        click.echo(click.style('Batch {0} not found in configuration file.'.format(name), fg='red', bold=True))
        sys.exit(1)
    from zbxsend import Metric, send_to_zabbix
    b = ctx.obj['batches'][name]
    logger.debug('Batch config args: {0}'.format(b))
    metrics = []
    zserver = b.pop('server')
    zport = int(b.pop('port'))
    zhost = b.pop('host')
    # Should only be Item keys at this point.
    logger.debug('Batch keys: {0}'.format(b))
    # Separate keys into similar APIs
    apis = { 'health': [], 'clusterstats': [], 'clusterstate': [],
        'nodestats': [], 'nodeinfo': [],}
    for k in b:
        ztuple = parse_key(b[k])
        apis[ztuple[0]].append(ztuple)
    logger.debug('API-separated keys: {0}'.format(apis))
    for api in apis:
	# ignore empty list
        if not apis[api]:
            continue
	# get the base api object
        apiobj = map_api(apis[api][0], ctx.obj['client'])
	# iterate over each tuple 
        for ztuple in apis[api]:
            result = apiobj.get(ztuple[2], name=ztuple[1])
            if result == DotMap():
                result = 'ZBX_NOTSUPPORTED'
            # We do not have the key here, so we need to rebuild it.
            metrics.append(Metric(zhost, ztuple[0] + '[' + ztuple[2] + ']', result))

    logger.debug('Metrics: {0}'.format(metrics))
    result = send_to_zabbix(metrics, zserver, zport)
    logger.debug('Result = {0}'.format(result))
    # Spit out exit code to stdout
    click.echo(0 if result else 1)
    logger.info('Job completed.')

def main():
    cli(obj={})
