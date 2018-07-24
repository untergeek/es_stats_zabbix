"""
Batch processing functions
"""

import json
import logging
from re import sub
from dotmap import DotMap
from es_stats.utils import fix_key
from es_stats_zabbix.defaults.settings import (
    APIS, valuetype_map, skip_these_endpoints)
from es_stats_zabbix.exceptions import NotFound
from es_stats_zabbix.helpers.utils import get_nodeid, status_map

LOGGER = logging.getLogger(__name__)

BASETYPES = ['bool', 'bytes', 'millis', 'percent', 'unsigned', 'character', 'float']

def dotty(dotmapobj, notation='', retval=[]):
    """Extract a DotMap of endpoints into dotted notation strings"""
    for i in list(dotmapobj.keys()):
        if i in skip_these_endpoints():
            continue
        if isinstance(dotmapobj[i], DotMap):
            nestlevel = notation[:]
            if notation == '':
                notation += i
            else:
                notation += '.' + i
            try:
                val = eval('dotmapobj' + '.' + i)
            except (NameError, SyntaxError):
                val = dotmapobj[i]
            dotty(val, notation, retval=retval)
            notation = nestlevel
        elif isinstance(dotmapobj[i], list):
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
        pass # Uncomment if debugging is needed.
        # LOGGER.debug('{0} is not a float'.format(value))
    try:
        _ = int(value)
        return int
    except (TypeError, ValueError):
        pass # Uncomment if debugging is needed.
        # LOGGER.debug('{0} is not an int'.format(value))
    return str


def get_endpoints(statobjs, api, node=None, valuetype=None):
    """
    Get the endpoints matching only the provided valuetype
    """
    LOGGER.debug('ITERATION: API={0}, node={1}, valuetype={2}'.format(api, node, valuetype))
    try:
        nodeid = get_nodeid(statobjs, node)
    except NotFound:
        nodeid = statobjs['health'].local_id
        LOGGER.debug('No specific node name provided. Using "{0}"'.format(nodeid))
    if api in ['health', 'clusterstate', 'clusterstats']:
        full = statobjs[api].stats()
    else:
        full = statobjs[api].stats(nodeid=nodeid)

    # Must set dotty's retval to an empty list on initialization
    # Neglecting this leads to data duplication on subsequent runs
    # since there's recursion in dotty.
    dotted = dotty(full, retval=[])

    all_lines = []

    for line in dotted:
        value = eval('full' + fix_key(line))
        # Only add lines which have the same valuetype as what we received.
        if valuetype is not None and value != '':
            if typecaster(value) is not valuetype_map(valuetype):
                continue
        if value == DotMap():
            # This is essential to not returning invalid endpoints
            continue
        if valuetype is not None:
            vtl = len(valuetype)
            if valuetype in ['bytes', 'millis', 'percent']:
                if line[-vtl:] == valuetype:
                    all_lines.append(line)
            elif valuetype == 'unsigned':
                # Only append these if they're not those valuetype endings
                if line[-5:] != 'bytes' and \
                line[-6:] != 'millis' and \
                line[-7:] != 'percent':
                    all_lines.append(line)
            else:
                all_lines.append(line)
        else:
            all_lines.append(line)
    if all_lines:
        retval = {api: all_lines}
    else:
        retval = {}
    return retval

def get_macros(statobjs, api, dnd, node=None, valuetype=None, included=None):
    """
    Get the appropriate LLD macros for the provided valuetype.
    If a list of approved endpoints is "included", only return
    endpoints from that list.
    """
    endpoints = get_endpoints(statobjs, api, node=node, valuetype=valuetype)
    macros = []
    if api in endpoints:
        for e_p in endpoints[api]:
            # Don't send health or cluster info to any zabbix host but the cluster_name one
            if node != statobjs['health'].get('cluster_name'):
                if api in ['health', 'clusterstate', 'clusterstats']:
                    continue
            if api in dnd and e_p in dnd[api]:
                continue
            else:
                def macgen(e_p, api):
                    """Add the uppercase value of valuetype to the LLD Macros"""
                    return {
                        '{#TYPE' + valuetype.upper() + '}':e_p,
                        '{#API}':api
                    }
                if isinstance(included, list):
                    if e_p in included:
                        macros.append(macgen(e_p, api))
                else:
                    macros.append(macgen(e_p, api))
    return macros

def macrogen(statobjs, dnd, node=None, included=None):
    """
    Get the macros via get_macros for each BASETYPE and api.
    Prepare them for lldoutput
    """
    results = {}
    for zbxtype in BASETYPES:
        if not zbxtype in results:
            results[zbxtype] = {}
        for api in APIS:
            if not api in results[zbxtype]:
                results[zbxtype][api] = []
            macros = get_macros(statobjs, api, dnd, node=node, valuetype=zbxtype,
                                included=included)
            for macro in macros:
                results[zbxtype][api].append(macro)
    return results

def lldoutput(results):
    """
    Generate the appropriate LLD DATA dictionary for protobix to send
    """
    llddata = {}
    def lldify(orig):
        """Append _lld to the original string, and return"""
        return orig + '_lld'
    for zbxtype in results:
        if not zbxtype in llddata:
            llddata[lldify(zbxtype)] = []
        for api in results[zbxtype]:
            if results[zbxtype][api] != []:
                llddata[lldify(zbxtype)] += results[zbxtype][api]
    for k in list(llddata.keys()):
        if llddata[k] == []:
            del llddata[k]
    return llddata
