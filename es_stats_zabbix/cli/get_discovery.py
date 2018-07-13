"""
Click module to call the discovery functions
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
@click.option('--node', help='Optional node name', default=None, show_default=True)
@click.option('--show_all', default='false', show_default=True,
              help='Show all macros, not just those in config file (yes, y, true, show_all)')
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, host, port, debug, node, show_all):
    """
    Connect to the backend at --host and --port and return the Zabbix Low-Level Discovery
    json object.

    This object will contain macros for all endpoints from the config file found
    on --node, unless --show_all is set, in which case it will collect ALL macros
    found, excepting those set as do_not_discover.

    Perform --debug logging upstream to the backend if specified
    """
    # Do a simple socket check first
    if not open_port(host, port):
        exit(1)

    # Now try to get the value
    if debug:
        log_to_listener(host, port, 'debug', {'node': node, 'show_all': show_all})
    uri = '/api/discovery/'
    if debug:
        log_to_listener(host, port, 'debug', {'host':host, 'port':port, 'uri':uri})

    show_bool = True if show_all.lower() in ['true', 'yes', 'y', 'show_all'] else False

    fail = 'ZBX_NOTSUPPORTED'
    body = {'show_all': show_bool}
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
        mdict = {'error':'A non-200 HTTP response code was received.'}
        log_to_listener(host, port, 'error', mdict)
        print(fail)
    except FailedExecution:
        mdict = {'error':'The request was unable to successfully complete.'}
        log_to_listener(host, port, 'error', mdict)
        print(fail)
