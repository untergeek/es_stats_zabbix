"""
Click module to launch node LLD gathering
"""

from sys import exit
import click
from es_stats_zabbix import __version__
from es_stats_zabbix.exceptions import FailedExecution, NotFound
from es_stats_zabbix.helpers.utils import do_request, log_to_listener, open_port

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--host', help='es_stats_zabbix backend listener IP',
              default='127.0.0.1', show_default=True)
@click.option('--port', help='es_stats_zabbix backend listener Port',
              default=7600, show_default=True)
@click.option('--debug', is_flag=True, help='Log all transactions in listener')
@click.argument('node')
@click.option('--flag', help='Pass arbitrary value to differentiate calls')
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, host, port, debug, node, flag):
    """
    Connect to the backend at --host and --port.

    Specify a particular node name.

    --flag is pseudo-arbitrary value used to make it possible to have multiple Zabbix keys
    reference the same data.

    Perform --debug logging upstream to the backend if specified
    """

    uri = '/api/nodediscovery/{0}'.format(node)
    fail = 'ZBX_NOTSUPPORTED'
    method = 'post'
    body = {}
    if flag is not None:
        body['flag'] = flag
    if debug:
        log_to_listener(host, port, 'debug',
                        {'host':host, 'port':port, 'uri':uri, 'node':node, 'flag':flag})
    try:
        result = do_request(host, port, uri, method, body=body)
        if debug:
            msgs = {
                'result': str(result),
                'size_in_bytes': len(str(result).encode('utf-8'))
            }
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
