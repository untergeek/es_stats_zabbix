from os import access, path, R_OK

APIS = ['health', 'clusterstate', 'clusterstats', 'nodeinfo', 'nodestats']

FILEPATHS = [
    path.join(path.expanduser('~'), '.es_stats_zabbix', 'config.yml'),
    path.join('etc', 'es_stats_zabbix', 'config.yml'),
]

SKIP_THESE = [
    'get', 
    'os', 
    'update', 
    'keys', 
    'items', 
    'mappings', 
    'snapshots', 
    'metadata', 
    'type.default',
    'adaptive_selection',
    'max_unsafe_auto_id_timestamp'
]

DATATYPES = {
    'bool': bool,
    'text': str,
    'unsigned': int,
    'float': float,
    'character': str,
}

def apis():
    """
    Return constant APIS
    """
    return APIS

def config_file():
    """
    Default Config file location
    
    Return the first file that matches from constant FILEPATHS, otherwise None
    """
    for file in FILEPATHS:
        if path.isfile(file) and access(file, R_OK):
            return file
    return None # If no files in filepaths are present, then return None

def valuetype_map(value):
    """
    Return DATATYPES[value]
    """
    return DATATYPES[value]


def skip_these_endpoints():
    """
    'get', 'update', 'keys', and 'items' are a protected methods in DotMap
    'os' level stats are easier to get in other ways
    'mappings' & 'metadata' should not be tracked in this way
    'type.default' is a dotted notation, but single key. Very weird.
    """
    return SKIP_THESE