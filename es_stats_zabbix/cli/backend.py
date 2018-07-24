"""
Backend Click CLI module
"""

import logging
import click
from es_stats_zabbix import __version__
from es_stats_zabbix.defaults.settings import apis
from es_stats_zabbix.helpers.config import config_override
from es_stats_zabbix.defaults.settings import config_file
from es_stats_zabbix.backend import run_backend

def false_to_none(ctx, param, value):
    """Convert a false value to a None"""
    if value:
        retval = True
    else:
        retval = None
    return retval

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--config', help='Path to configuration file.', default=config_file(),
              show_default=True)
@click.option('--host', multiple=True, help='Elasticsearch host.')
@click.option('--port', help='Elasticsearch port.')
@click.option('--url_prefix', help='Elasticsearch http url prefix.', default='')
@click.option('--use_ssl', is_flag=True, help='Connect to Elasticsearch through SSL.',
              callback=false_to_none)
@click.option('--ca_certs', help='Path to certificate to use for SSL validation.')
@click.option('--client_cert', help='Path to file containing SSL certificate for client auth.')
@click.option('--client_key', help='Path to file containing SSL key for client auth.')
@click.option('--verify_certs', is_flag=True, help='Whether to validate SSL certificates',
              callback=false_to_none)
@click.option('--username', help='Username')
@click.option('--password', help='Password')
@click.option('--timeout', help='Connection timeout in seconds.', default=30, show_default=True)
@click.option('--master_only', is_flag=True, help='Only operate on elected master node.',
              callback=false_to_none)
@click.option('--loglevel', help='Log level')
@click.option('--logfile', help='Log file (Default: STDOUT)')
@click.option('--logformat', help='Log output format [default|logstash|json].')
@click.option('--apihost', help='es_stats_zabbix backend listener IP')
@click.option('--apiport', help='es_stats_zabbix backend listener Port')
@click.option('--apidebug', is_flag=True, help='es_stats_zabbix backend debug mode',
              callback=false_to_none)
@click.option('--cache_timeout',
              help='How long to cache the results of API call to Elasticsearch (Default: 60)')
@click.option('--zbx_ServerActive', help='Zabbix ServerActive IP or hostname')
@click.option('--zbx_ServerPort', help='Zabbix ServerPort')
@click.option('--zbx_LogType', help='Zabbix log type: "file", "system", or "console"')
@click.option('--zbx_LogFile', help='Path to Zabbix agent log file')
@click.option('--zbx_DebugLevel', help='Zabbix DebugLevel')
@click.option('--zbx_Timeout', help='Zabbix Timeout')
@click.option('--zbx_Hostname', help='Zabbix Hostname')
@click.option('--zbx_TLSConnect', help='Zabbix TLSConnect: "unencrypted", "psk", or "cert"')
@click.option('--zbx_TLSCAFile', help='Path to Zabbix TLSCAFile')
@click.option('--zbx_TLSCertFile', help='Path to Zabbix TLSCertFile')
@click.option('--zbx_TLSCRLFile', help='Path to Zabbix TLSCRLFile')
@click.option('--zbx_TLSKeyFile', help='Path to Zabbix TLSKeyFile')
@click.option('--zbx_TLSServerCertIssuer', help='Zabbix TLSServerCertIssuer')
@click.option('--zbx_TLSServerCertSubject', help='Zabbix TLSServerCertSubject')
@click.option('--zbx_TLSPSKIdentity', help='Zabbix TLSPSKIdentity')
@click.option('--zbx_TLSPSKFile', help='Path to Zabbix TLSPSKFile')
@click.version_option(version=__version__)
@click.pass_context
def cli(
        ctx, config, host, port, url_prefix, use_ssl, ca_certs, client_cert, client_key,
        verify_certs, username, password, timeout, master_only, loglevel, logfile, logformat,
        apihost, apiport, apidebug, cache_timeout, zbx_serveractive, zbx_serverport, zbx_logtype,
        zbx_logfile, zbx_debuglevel, zbx_timeout, zbx_hostname, zbx_tlsconnect, zbx_tlscafile,
        zbx_tlscertfile, zbx_tlscrlfile, zbx_tlskeyfile, zbx_tlsservercertissuer,
        zbx_tlsservercertsubject, zbx_tlspskidentity, zbx_tlspskfile
    ):
    """
    es_stats_zabbix: for collecting stats & metrics from Elasticsearch into Zabbix
    """
    config_dict = config_override(ctx)
    run_backend(config_dict)
