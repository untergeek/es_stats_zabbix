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
    if debug:
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

    # Fix bool and integer values to be correct
    client_args = fix_types(config.get('elasticsearch'))

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

    logging.info('Job starting.')
    # Put elasticsearch client into ctx.obj['client']
    ctx.obj['client'] = get_client(**client_args)

    # Put batch configuration into ctx.obj['batches']
    batches = config.get()
    del batches["elasticsearch"]
    del batches["logging"]
    ctx.obj['batches'] = batches

@cli.command(short_help="Cluster Health")
@click.option('--key', help="Dot-notation path to Cluster Health key", required=True)
@click.pass_context
def health(ctx, key):
    """Send back value for single cluster health key"""
    ch = ClusterHealth(ctx.obj['client'])
    click.echo(ch.get(key))

@cli.command(short_help="Cluster Stats")
@click.option('--key', help="Dot-notation path to Cluster Stats key", required=True)
@click.pass_context
def cluster_stats(ctx, key):
    """Send back value for single cluster stats key"""
    stats = ClusterStats(ctx.obj['client'])
    click.echo(stats.get(key))

@cli.command(short_help="Cluster State")
@click.option('--key', help="Dot-notation path to Cluster State key", required=True)
@click.pass_context
def cluster_state(ctx, key):
    """Send back value for single cluster state key"""
    state = ClusterState(ctx.obj['client'])
    click.echo(state.get(key))

@cli.command(short_help="Node Stats")
@click.option('--key', help="Dot-notation path to Node Stats key", required=True)
@click.option('--node', help="Node name (not nodeid)", required=True)
@click.pass_context
def node_stats(ctx, key, node):
    """Send back value for single node stats key"""
    stats = NodeStats(ctx.obj['client'], node)
    click.echo(stats.get(key))

@cli.command(short_help="Node Info")
@click.option('--key', help="Dot-notation path to Node Info key", required=True)
@click.option('--node', help="Node name (not nodeid)", required=True)
@click.pass_context
def node_info(ctx, key, node):
    """Send back value for single node info key"""
    info = NodeInfo(ctx.obj['client'], node)
    click.echo(info.get(key))

@cli.command(short_help="Batch mode")
@click.option('--name', help="Batch name from within configuration file.")
@click.pass_context
def batch(ctx, name):
    """Send values in batch to zabbix_host (server defined in config file)"""
    if name not in ctx.obj['batches']:
        click.echo(click.style('Batch {0} not found in configuration file.'.format(batch), fg='red', bold=True))
        sys.exit(1)
    from zbxsend import Metric, send_to_zabbix
    b = ctx.obj['batches'][name]
    metrics = []
    if b['clusterhealth']:
        ch = ClusterHealth(ctx.obj['client'])
        for k in b['clusterhealth'].split(','):
            metrics.append(Metric(b['host'], 'health[' + k + ']', ch.get(k)))
    if b['clusterstats']:
        cs = ClusterStats(ctx.obj['client'])
        for k in b['clusterstats'].split(','):
            metrics.append(Metric(b['host'], 'clusterstats[' + k + ']', cs.get(k)))
    if b['clusterstate']:
        cte = ClusterState(ctx.obj['client'])
        for k in b['clusterstate'].split(','):
            metrics.append(Metric(b['host'], 'clusterstate[' + k + ']', cte.get(k)))
    if b['nodestats']:
        if not b['node']:
            click.echo(click.style('Batch {0} is missing required parameter "node"'.format(name), fg='red', bold=True))
            sys.exit(1)
        ns = NodeStats(ctx.obj['client'], b['node'])
        for k in b['nodestats'].split(','):
            metrics.append(Metric(b['host'], 'nodestats[' + k + ']', ns.get(k)))
    if b['nodeinfo']:
        if not b['node']:
            click.echo(click.style('Batch {0} is missing required parameter "node"'.format(name), fg='red', bold=True))
            sys.exit(1)
        ni = NodeInfo(ctx.obj['client'], b['node'])
        for k in b['nodeinfo'].split(','):
            metrics.append(Metric(b['host'], 'nodeinfo[' + k + ']', ni.get(k)))

    # click.echo('Metrics: {0}'.format(metrics))
    send_to_zabbix(metrics, b['server'], int(b['port']))

def main():
    cli(obj={})
