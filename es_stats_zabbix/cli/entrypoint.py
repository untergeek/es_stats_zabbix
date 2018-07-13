"""
Universal entrypoint for any scripts/modules that need to be called.
"""
from sys import argv as cli_args
from sys import exit
from os import path as os_path
from es_stats_zabbix.cli.backend import cli as backend
from es_stats_zabbix.cli.display_endpoints import cli as display_endpoints
from es_stats_zabbix.cli.get_discovery import cli as get_discovery
from es_stats_zabbix.cli.get_es_stat import cli as get_es_stat
from es_stats_zabbix.cli.get_cluster import cli as get_cluster
from es_stats_zabbix.cli.get_nodes import cli as get_nodes
from es_stats_zabbix.cli.trapper_discovery import cli as trapper_discovery
from es_stats_zabbix.cli.trapper_stats import cli as trapper_stats

EXECUTABLE = {
    'run_backend.py': backend,
    'esz_backend': backend,
    'run_display_endpoints.py': display_endpoints,
    'esz_display_endpoints': display_endpoints,
    'run_discovery.py': get_discovery,
    'esz_discovery': get_discovery,
    'run_cluster_discovery.py': get_cluster,
    'esz_cluster_discovery': get_cluster,
    'run_node_discovery.py': get_nodes,
    'esz_node_discovery': get_nodes,
    'run_get_es_stat.py': get_es_stat,
    'esz_get_stat': get_es_stat,
    'run_trapper_discovery.py': trapper_discovery,
    'esz_trapper_discovery': trapper_discovery,
    'run_trapper_stats.py': trapper_stats,
    'esz_trapper_stats': trapper_stats,
}

def command_liner(name, cli):
    '''
    Wrapper for running programs from the command-line.
    It is specifically for catching Unicode errors when running click with
    Python 3 when LANG and LC_ALL are not set appropriately, and giving an
    instructional warning message for how to fix it.
    '''

    msg = (
        '''
When used with Python 3, {0} requires the locale to be unicode.
Any of the above unicode definitions are acceptable.

To set the locale to be unicode, try:

$ export LC_ALL=en_US.utf8
$ {0} [ARGS]

Alternately, you should be able to specify the locale on the command-line:

$ LC_ALL=en_US.utf8 {0} [ARGS]

Be sure to substitute your unicode variant for en_US.utf8

'''.format(name))
    try:
        # pylint: disable=no-value-for-parameter
        cli()
    except Exception as err:
        if isinstance(err, RuntimeError):
            if 'ASCII' in str(err):
                print('{0}'.format(err))
                print(msg)
        else:
            from sys import exit
            print('{0}'.format(err))
            exit(1)

def run():
    """Run the called program"""
    _, program_name = os_path.split(cli_args[0])
    if program_name not in list(EXECUTABLE.keys()):
        print('{0} is not an recognized command'.format(program_name))
        exit(1)
    command_liner(program_name, EXECUTABLE[program_name])

if __name__ == '__main__':
    run()
    