import click
from es_stats_zabbix import __version__
from es_stats_zabbix.defaults.settings import apis
from es_stats_zabbix.exceptions import FailedExecution, NotFound
from es_stats_zabbix.helpers.utils import do_request, log_to_listener, open_port
from sys import exit
    
@click.command()
@click.option('--host', help='es_stats_zabbix backend listener IP',
    default='127.0.0.1', show_default=True)
@click.option('--port', help='es_stats_zabbix backend listener Port',
    default=7600, show_default=True)
@click.option('--debug', is_flag=True, help='Log all transactions in listener')
@click.argument('api', nargs=1)
@click.argument('valuetype', nargs=1)
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, host, port, debug, api, valuetype):
    """
    Connect to the backend at --host and --port and return the discovery json
    object from the provided API.

    Perform --debug logging upstream to the backend if specified
    """
    # Do a simple socket check first
    if not open_port(host, port):
        exit(1)

    # Now try to get the value
    if debug:
        log_to_listener(host, port, 'debug', {'api': api})
    if not api in apis():
        m = "'{0}' is not a valid API: {1}".format(api, apis())
        log_to_listener(host, port, 'critical', m)
        exit(1)
    url = 'http://{0}:{1}/api/discovery/{2}'.format(host, port, api)
    if debug:
        log_to_listener(host, port, 'debug', {'url':url})

    fail = 'ZBX_NOTSUPPORTED'
    if valuetype != 'all':
        body = {'valuetype': valuetype} 
        method = 'post'
    else:
        method = 'get'
        body = None

    try:        
        result = do_request(host, port, url, method, body=body)
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
        log_to_listener(host, port, 'error', {'error':'The request was unable to successfully complete.'})
        print(fail)
  


