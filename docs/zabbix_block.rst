.. _zabbix_block:

``zabbix``
==========

This is an example configuration block::

    zabbix:
      ServerActive: zabbixserver.example.com
      ServerPort:
      LogType: 'file'
      LogFile: '/tmp/zabbix_agentd.log'
      DebugLevel: 3
      Timeout: 3
      Hostname:
      TLSConnect: 'unencrypted'
      TLSCAFile:
      TLSCertFile:
      TLSCRLFile:
      TLSKeyFile:
      TLSServerCertIssuer:
      TLSServerCertSubject:
      TLSPSKIdentity:
      TLSPSKFile:

Values and defaults are described at https://www.zabbix.com/documentation/3.4/manual/appendix/config/zabbix_agentd
except as follows:

``ServerPort``
----------------

``ServerPort`` refers to the listening port on the Zabbix Server.

The default value is 10051.
