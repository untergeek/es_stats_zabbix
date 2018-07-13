"""
Trapper Discovery CLI
"""

from sys import exit
import click
from es_stats_zabbix import __version__
from es_stats_zabbix.defaults.settings import apis
from es_stats_zabbix.exceptions import FailedExecution, NotFound
from es_stats_zabbix.helpers.utils import do_request, log_to_listener, open_port


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--host', help='es_stats_zabbix backend listener IP',
              default='127.0.0.1', show_default=True)
@click.option('--port', help='es_stats_zabbix backend listener Port',
              default=7600, show_default=True)
@click.option('--debug', is_flag=True, help='Log all transactions in listener')
@click.option('--flag', help='Pass arbitrary value to differentiate calls')
@click.option('--node', help='Optional node name', default=None, show_default=True)
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, host, port, debug, flag, node):
    """
    Connect to the backend at --host and --port and return the discovery json
    object for all APIs as Zabbix trapper data from "node".

    --flag is an arbitrary value used to make it possible to have multiple Zabbix keys
    reference the same data.

    Perform --debug logging upstream to the backend if specified
    """
    # Do a simple socket check first
    if not open_port(host, port):
        exit(1)

    # Now try to get the value
    if debug:
        log_to_listener(host, port, 'debug', {'node': node})

    uri = '/api/trapperdiscovery/{0}'.format(node)
    if debug:
        log_to_listener(host, port, 'debug', {'host':host, 'port':port, 'uri':uri})

    fail = 'ZBX_NOTSUPPORTED'
    body = {}
    if node:
        body['node'] = node
    method = 'post'

    try:
        result = do_request(host, port, uri, method, body=body)
        msgs = {
            'result': str(result),
            'size_in_bytes': len(str(result).encode('utf-8'))
        }
        if debug:
            log_to_listener(host, port, 'debug', msgs)
        print(result.strip())
    except NotFound:
        log_to_listener(host, port, 'error', {'error':'A non-200 HTTP response code was received.'})
        print(fail)
    except FailedExecution:
        mdict = {'error':'The request was unable to successfully complete.'}
        log_to_listener(host, port, 'error', mdict)
        print(fail)
