#!/usr/bin/env python

"""Wrapper for running es_stats_zabbix stat collector from source."""

from es_stats_zabbix.get_nodes import cli

if __name__ == '__main__':
    try:
        # pylint: disable=no-value-for-parameter
        cli()
    except Exception as e:
        if isinstance(e, RuntimeError):
            if 'ASCII' in str(e):
                print('{0}'.format(e))
                print(
'''

When used with Python 3, esz_nodes_discovery requires the locale to be unicode. 
Any of the above unicode definitions are acceptable.

To set the locale to be unicode, try:

$ export LC_ALL=en_US.utf8
$ esz_nodes_discovery [ARGS]

Alternately, you should be able to specify the locale on the command-line:

$ LC_ALL=en_US.utf8 esz_nodes_discovery [ARGS]

Be sure to substitute your unicode variant for en_US.utf8

'''
            )
        else:
            from sys import exit
            print('{0}'.format(e))
            exit(1)
