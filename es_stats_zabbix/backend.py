import click
import logging
from es_stats_zabbix import __version__
from es_stats_zabbix.defaults.settings import apis
from es_stats_zabbix.helpers.config import config_override, host_callback, keys_callback
from es_stats_zabbix.defaults.settings import config_file
from es_stats_zabbix.helpers.execution import run

@click.command()
@click.option('--config', help='Path to configuration file.', default=config_file(), show_default=True)
@click.option('--host', multiple=True, help='Elasticsearch host.',
    default='127.0.0.1', callback=host_callback, show_default=True)
@click.option('--port', help='Elasticsearch port.', default=9200, show_default=True)
@click.option('--url_prefix', help='Elasticsearch http url prefix.', default='')
@click.option('--use_ssl', is_flag=True, help='Connect to Elasticsearch through SSL.')
@click.option('--ca_certs', help='Path to certificate to use for SSL validation.')
@click.option('--client_cert', help='Path to file containing SSL certificate for client auth.')
@click.option('--client_key', help='Path to file containing SSL key for client auth.')
@click.option('--verify_certs', is_flag=True, help='Whether to validate SSL certificates')
@click.option('--username', help='Username')
@click.option('--password', help='Password')
@click.option('--timeout', help='Connection timeout in seconds.', default=30, show_default=True)
@click.option('--master_only', is_flag=True, help='Only operate on elected master node.')
@click.option('--loglevel', help='Log level')
@click.option('--logfile', help='Log file (Default: STDOUT)')
@click.option('--logformat', help='Log output format [default|logstash|json].')
@click.option('--apihost', help='es_stats_zabbix backend listener IP',
    default='127.0.0.1', show_default=True)
@click.option('--apiport', help='es_stats_zabbix backend listener Port',
    default=7600, show_default=True)
@click.option('--apidebug', is_flag=True, help='es_stats_zabbix backend debug mode')
@click.option('--cache_timeout', help='How long to cache the results of API call to Elasticsearch (Default: 60)')
@click.version_option(version=__version__)
@click.pass_context
def cli(
    ctx, config, host, port, url_prefix, use_ssl, ca_certs, client_cert, client_key, verify_certs,
    username, password, timeout, master_only, loglevel, logfile, logformat, apihost, apiport, apidebug,
    cache_timeout
    ):
    """
    es_stats_zabbix: for collecting stats & metrics from Elasticsearch into Zabbix
    """
    config_dict = config_override(ctx)
    run(config_dict)