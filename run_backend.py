#!/usr/bin/env python

"""Wrapper for running es_stats_zabbix backend from source."""

from es_stats_zabbix.backend import cli

if __name__ == '__main__':
    try:
        # pylint: disable=no-value-for-parameter
        cli()
    except Exception as e:
        if type(e) == type(RuntimeError()):
            if 'ASCII' in str(e):
                print('{0}'.format(e))
                print(
'''

When used with Python 3, es_stats_zabbix requires the locale to be unicode. 
Any of the above unicode definitions are acceptable.

To set the locale to be unicode, try:

$ export LC_ALL=en_US.utf8
$ es_stats_zabbix [ARGS]

Alternately, you should be able to specify the locale on the command-line:

$ LC_ALL=en_US.utf8 es_stats_zabbix [ARGS]

Be sure to substitute your unicode variant for en_US.utf8

'''
            )
        else:
            from sys import exit
            print('{0}'.format(e))
            exit(1)