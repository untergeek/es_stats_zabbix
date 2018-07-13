"""
Click module to launch es_stat gathering
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
@click.option('--node', help='Optional node name', default=None, show_default=True)
@click.argument('api', nargs=1)
@click.argument('endpoint', nargs=1)
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, host, port, debug, node, api, endpoint):
    """
    Connect to the backend at --host and --port and return the value
    associated with the provided API and ENDPOINT.

    Specify a particular node name with --node
    Perform --debug logging upstream to the backend if specified
    """
    # Do a simple socket check first
    if not open_port(host, port):
        exit(1)

    # Now try to get the value
    node = None if node == '' else node
    if debug:
        mdict = {'user_parms': 'api: {0}, endpoint: {1}, node: {2}'.format(api, endpoint, node)}
        log_to_listener(host, port, 'debug', mdict)

    if not api in apis():
        msg = "'{0}' is not a valid API: {1}".format(api, apis())
        log_to_listener(host, port, 'critical', msg)
        exit(1)

    uri = '/api/{0}/{1}'.format(api, endpoint)
    if debug:
        log_to_listener(host, port, 'debug', {'host':host, 'port':port, 'uri':uri})
    fail = 'ZBX_NOTSUPPORTED'
    if node is not None:
        body = {'node': node}
        method = 'post'
    else:
        method = 'get'
        body = None

    try:
        print(do_request(host, port, uri, method, body=body).strip())
    except FailedExecution:
        mdict = {'error':'The request was unable to successfully complete.'}
        log_to_listener(host, port, 'error', mdict)
        print(fail)
