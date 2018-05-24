import click
from es_stats_zabbix import __version__
from es_stats_zabbix.exceptions import FailedExecution, NotFound
from es_stats_zabbix.helpers.utils import do_request, log_to_listener, open_port
from sys import exit
    
@click.command()
@click.option('--host', help='es_stats_zabbix backend listener IP',
    default='127.0.0.1', show_default=True)
@click.option('--port', help='es_stats_zabbix backend listener Port',
    default=7600, show_default=True)
@click.option('--debug', is_flag=True, help='Log all transactions in listener')
@click.option('--flag', help='Pass arbitrary value to differentiate calls')
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, host, port, debug, flag):
    """
    Connect to the backend at --host and --port.

    --flag is used to make an arbitrary number of zabbix keys available.

    Perform --debug logging upstream to the backend if specified
    """

    uri = '/api/nodediscovery/'
    method = 'get'
    fail = 'ZBX_NOTSUPPORTED'
    if debug:
        log_to_listener(host, port, 'debug', {'host':host, 'port':port, 'uri':uri})
    try:        
        result = do_request(host, port, uri, method)
        if debug:
            msgs = {
                'result': str(result),
                'size_in_bytes': len(str(result).encode('utf-8'))
            }
            log_to_listener(host, port, 'debug', msgs)
        print(result.strip())
    except NotFound:
        log_to_listener(host, port, 'error', {'error':'A non-200 HTTP response code was received.'})
        print(fail)
    except FailedExecution:
        log_to_listener(host, port, 'error', {'error':'The request was unable to successfully complete.'})
        print(fail)
  


