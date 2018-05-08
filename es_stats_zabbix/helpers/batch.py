import logging
from dotmap import DotMap
from es_stats.classes import ClusterHealth
from es_stats.utils import fix_key
from es_stats_zabbix.defaults.settings import valuetype_map, skip_these_endpoints
from es_stats_zabbix.helpers.utils import status_map
from re import sub

logger = logging.getLogger(__name__)

def dotty(dm, notation='', retval=[]):
    for i in list(dm.keys()):
        if i in skip_these_endpoints():
            continue
        if isinstance(dm[i], DotMap):
            nestlevel = notation[:]
            if notation == '':
                notation += i
            else:
                notation += '.' + i
            try:
                val = eval('dm' + '.' + i)
            except (NameError, SyntaxError):
                val = dm[i]
            dotty(val, notation, retval=retval)
            notation = nestlevel
        elif isinstance(dm[i], list):
            pass
        else:
            if notation == '':
                retval.append('{0}'.format(i))
            else:
                retval.append('{0}.{1}'.format(notation, i))
    return retval

def typecaster(value):
    """
    Attempt to cast value as float, or int.  If it can't, it's a str
    """
    # Check bool first, because int(False) == 0, and would be cast wrong
    if str(value).lower() == 'true' or str(value).lower() == 'false':
        return bool
    try:
        # A Zabbix float is a signed int, or a floating point value
        if str(value)[0] == '-' or len(str(value).split('.')) == 2:
            _ = float(value)
            return float
    except (TypeError, ValueError):
        logger.debug('{0} is not a float'.format(value))
    try:
        _ = int(value)
        return int
    except (TypeError, ValueError):
        logger.debug('{0} is not an int'.format(value))
    return str

    
def get_endpoints(client, api, valuetype=None):
    ch = ClusterHealth(client)
    nodeid = ch.local_id

    if api == 'health':
        data = client.cluster.health()
    elif api == 'clusterstate':
        data = client.cluster.state()
    elif api == 'clusterstats':
        data = client.cluster.stats()
    elif api == 'nodeinfo':
        data = client.nodes.info()['nodes'][nodeid]
    elif api == 'nodestats':
        data = client.nodes.stats()['nodes'][nodeid]

    # Must set dotty's retval to an empty list on initialization
    # Neglecting this leads to data duplication on subsequent runs
    # since there's recursion in dotty.
    dotted = dotty(DotMap(data), retval=[])
    # pylint: disable=unused-variable
    full = DotMap(data)
    all_lines = []
    
    for line in dotted:
        value = eval('full' + fix_key(line))
        # Only add lines which have the same valuetype as what we received.
        if valuetype is not None and value is not '':
            if typecaster(value) is not valuetype_map(valuetype):
                continue
        if value == DotMap():
            # This is essential to not returning invalid endpoints
            continue
        vtl = len(valuetype)
        if valuetype in ['bytes', 'millis', 'percent']:
            if line[-vtl:] == valuetype:
                all_lines.append(line)
        elif valuetype == 'unsigned': # Only append these if they're not those valuetype endings
            if line[-5:] != 'bytes' and \
               line[-6:] != 'millis' and \
               line[-7:] != 'percent':
                all_lines.append(line)
        else:
            all_lines.append(line)
    if all_lines:
        return { api: all_lines }
    else:
        return {}


