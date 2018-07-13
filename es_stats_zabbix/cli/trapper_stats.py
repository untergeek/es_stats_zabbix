"""
Click module to launch gathering of stats and sending via the Zabbix trapper protocol
"""

from sys import exit
import click
from es_stats_zabbix import __version__
from es_stats_zabbix.defaults.settings import apis
from es_stats_zabbix.exceptions import EmptyResult, FailedExecution, NotFound
from es_stats_zabbix.helpers.utils import do_request, log_to_listener, open_port

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--host', help='es_stats_zabbix backend listener IP',
              default='127.0.0.1', show_default=True)
@click.option('--port', help='es_stats_zabbix backend listener Port',
              default=7600, show_default=True)
@click.option('--debug', is_flag=True, help='Log all transactions in listener')
@click.option('--interval', show_default=True, default='60s',
              help='An interval defined in the YAML configuration file.')
@click.argument('node', nargs=1)
@click.argument('nodetype', nargs=1)
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, host, port, debug, interval, node, nodetype):
    """
    Connect to the backend at --host and --port using "node" as the target Zabbix host name.
    Collect stats, and ship them to Zabbix via the trapper protocol.

    "node" indicates both the node name and the Zabbix host trapper target
    "nodetype" is the type of node, as defined in the YAML config file. It is one of
        "cluster",
        "coordinating",
        "master",
        "data",
        "ingest",
        "ml",
    "cluster" is special, as it collects cluster-level stats from the clusterstats API endpoint
    "interval" is also defined in the YAML config file.  If not specified, it will be '60s'
    Return the number of stats which failed to be read by Zabbix. A zero indicates all succeeded.

    Perform --debug logging upstream to the backend if specified
    """
    # Do a simple socket check first
    if not open_port(host, port):
        exit(1)

    # Now try to get the value
    if debug:
        mdict = {
            'user_parms': 'node: {0}, nodetype: {1}, interval: {2}'.format(node, nodetype, interval)
        }
        log_to_listener(host, port, 'debug', mdict)

    uri = '/api/trapperstats/{0}'.format(node)
    if debug:
        log_to_listener(host, port, 'debug', {'host':host, 'port':port, 'uri':uri})
    fail = 'ZBX_NOTSUPPORTED'
    body = {'nodetype': nodetype, 'interval': interval}
    method = 'post'

    try:
        print(do_request(host, port, uri, method, body=body).strip())
    except FailedExecution:
        mdict = {'error':'The request was unable to successfully complete.'}
        log_to_listener(host, port, 'error', mdict)
        print(fail)
