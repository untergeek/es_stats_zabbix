import logging
import requests
import socket
from es_stats_zabbix.exceptions import FailedExecution, NotFound

logger = logging.getLogger(__name__)

def log_to_listener(host, port, level, msgs):
    url = 'http://{0}:{1}/api/logger/{2}'.format(host, port, level)
    if not isinstance(msgs, dict):
        requests.post(url, json={'message': '{0}'.format(msgs)})
    else:
        requests.post(url, json=msgs)

def open_port(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
        s.shutdown(2)
        return True
    except:
        return False

def do_request(host, port, url, method, body=None):
    try:
        if method == 'get':
            r = requests.get(url)
        elif body is not None:
            r = requests.post(url, json=body)
        else:
            raise ValueError('No value provided for "body"')
        if r.status_code != 200:
            # Something was invalid
            msgs = {
                'message': 'Response received: {0}'.format(r.status_code),
                'method': method.upper(),
                'url': url,
                'body': body,
            }
            log_to_listener(host, port, 'error', msgs)
            raise NotFound('A non-200 HTTP response code was received.')
        else:
            # We're good! Print the value minus newlines and trailing spaces
            return r.text
    except:
        # Something else is amiss with our api/endpoint/node
        log_to_listener(host, port, 'error', 'Failed to collect value. Try using --debug')
        raise FailedExecution('The request was unable to successfully complete.')

def status_map(state):
    """Return a numeric value in place of the string value for state"""
    if state == 'green':
        return 0
    elif state == 'yellow':
        return 1
    elif state == 'red':
        return 2
    else:
        return 3 # fail