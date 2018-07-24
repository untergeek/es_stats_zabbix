"""
Utility methods
"""

import socket
import logging
import requests
from es_stats_zabbix.defaults.settings import NODETYPES
from es_stats_zabbix.exceptions import FailedExecution, NotFound

LOGGER = logging.getLogger(__name__)

def log_to_listener(host, port, level, msgs):
    """Log to the REST API"""
    url = 'http://{0}:{1}/api/logger/{2}'.format(host, port, level)
    if not isinstance(msgs, dict):
        requests.post(url, json={'message': '{0}'.format(msgs)})
    else:
        requests.post(url, json=msgs)

def open_port(host, port):
    """Test whether a port is open at host.  Return boolean"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        sock.shutdown(2)
        return True
    except:
        return False

def do_request(host, port, uri, method, body=None):
    """Wrapper for handling REST requests"""
    # Since we're manually separating with a /, prune if it exists.
    uri = uri[1:] if uri[0] == '/' else uri
    url = 'http://{0}:{1}/{2}'.format(host, port, uri)
    try:
        if method == 'get':
            req = requests.get(url)
        elif body is not None:
            LOGGER.debug('POST: url={0}, body={1}'.format(url, body))
            req = requests.post(url, json=body)
        else:
            raise ValueError('No value provided for "body"')
        if req.status_code != 200:
            # Something was invalid
            msgs = {
                'message': 'Response received: {0}'.format(req.status_code),
                'method': method.upper(),
                'url': url,
                'body': body,
            }
            log_to_listener(host, port, 'error', msgs)
            raise NotFound('A non-200 HTTP response code was received.')
        else:
            # We're good!
            return req.text
    except:
        # Something else is amiss with our api/endpoint/node
        log_to_listener(host, port, 'error', 'Failed to collect value. Try using --debug')
        raise FailedExecution('The request was unable to successfully complete.')

def status_map(state):
    """Return a numeric value in place of the string value for state"""
    if state == 'green':
        retval = 0
    elif state == 'yellow':
        retval = 1
    elif state == 'red':
        retval = 2
    else:
        retval = 3 # fail
    return retval

def true_nodetypes(statobj, nodeid):
    """
    Return a list of nodetypes which have a `True` status"""
    nodeinfo = statobj.cached_read('nodeinfo')['nodes']
    settings = nodeinfo[nodeid]['settings']['node']
    retval = []
    for nodetype in NODETYPES:
        if nodetype in settings:
            if settings[nodetype].lower() == 'true':
                retval.append(nodetype)
        elif nodetype == 'ml':
            if settings['attr'][nodetype]['enabled']:
                retval.append(nodetype)
        elif nodetype == 'cluster':
            # We don't need this here.
            pass
        else:
            #  The default is true for each node type, so if it's not false, it's true.
            retval.append(nodetype)
    LOGGER.debug('RETVAL={0}'.format(retval))
    return retval

def get_cluster_macros(statobj, nodeid):
    """Get the cluster and node LLD macros"""
    cluster_name = statobj.client.cluster.health()['cluster_name']
    nodeinfo = statobj.cached_read('nodeinfo')['nodes']
    nodename = nodeinfo[nodeid]['name']
    entries = {
        '{#CLUSTERNAME}': cluster_name,
        '{#NODEID}':nodeid,
        '{#NODENAME}':nodename
    }
    return entries

def get_node_macros(statobj, nodeid):
    """Get the nodetype LLD macros"""
    macros = []
    def macgen(nodetype, boolish):
        """Add the uppercase value of valuetype to the LLD Macros"""
        return {
            '{#NODETYPE}':nodetype,
            '{#PRESENT}':boolish
        }
    present_nodetypes = true_nodetypes(statobj, nodeid)
    for nodetype in NODETYPES:
        if nodetype in present_nodetypes:
            macros.append(macgen(nodetype, 1))
        else:
            macros.append(macgen(nodetype, 0))
    return macros

def get_nodeid(statobjs, node):
    """Get the nodeid from the node name"""
    nodeinfo = statobjs['nodeinfo'].cached_read('nodeinfo')['nodes']
    found = False
    if not node:
        msg = 'No node name provided.'
        raise NotFound(msg)
    for n_i in nodeinfo:
        if nodeinfo[n_i]['name'] == node:
            LOGGER.debug('Found node name "{0}"'.format(node))
            LOGGER.debug('Setting nodeid to "{0}"'.format(n_i))
            return n_i
    if not found:
        msg = 'Node with name {0} not found.'.format(node)
        LOGGER.critical(msg)
        raise NotFound(msg)
