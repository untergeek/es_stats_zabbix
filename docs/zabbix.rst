.. _zabbix:

Zabbix Configuration
====================

Configuring Zabbix comes in multiple parts.

``zabbix_agentd.conf``
----------------------

It is important to note where ``es_stats_zabbix`` installs the entry points for
this part.  If you installed to a virtualenv, then the path will be
``/my/chosen/path/bin/``.  If you installed to the system Python by being root
or using ``sudo``, then the path can be determined with ``which esz_get_stat``.
The response will be something like ``/usr/bin/esz_get_stat``, so the path
would be ``/usr/bin``.  If you installed via ``pip`` to your username, e.g.
``pip install --user .``, then the path will be ``$HOME/.local/bin``.

Creating ``es_stats_zbx.conf``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A sample of the necessary Zabbix config file entries is included in the source
repository at
https://github.com/untergeek/es_stats_zabbix/tree/master/configuration/zabbix

::

    # $1 is api, $2 is endpoint, $3 is node
    UserParameter=es_stat[*],/usr/bin/esz_get_stat --node="$3" $1 $2

    # $1 is node, $2 is show_all
    UserParameter=es_stats_discovery[*],/usr/bin/esz_discovery --node="$1" --show_all="$2"

    # $1 is either 'cluster' or 'nodes'
    # $2 is any arbitrary value (allows for multiple keys to use this script)
    UserParameter=es_cluster_discovery[*],/usr/bin/esz_cluster_discovery --flag="$2" --value="$1"

    # $1 is node, $2 is any arbitrary value (allows for multiple keys to use this script)
    UserParameter=es_node_discovery[*],/usr/bin/esz_node_discovery --flag="$2" "$1"

    # $1 is node, $2 is any arbitrary value (allows for multiple keys to use this script)
    UserParameter=es_trapper_discovery[*],/usr/bin/esz_trapper_discovery --flag="$2" --node="$1"

    # $1 is node, $2 is nodetype, $3 is interval
    UserParameter=es_trapper_stats[*],/usr/bin/esz_trapper_stats --interval="$3" $1 $2

In this file, the ``PATH`` is ``/usr/bin``.  Replace ``/usr/bin`` with your
path, e.g. ``/my/chosen/path/bin/esz_discovery``, for each line.


Installing ``es_stats_zbx.conf``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``es_stats_zbx.conf`` file can then be placed in
``/etc/zabbix/zabbix_agentd.d`` as ``es_stats_zbx.conf``.  A corresponding
``Include`` line should be present in the ``zabbix_agentd.conf`` file:

::

    Include=/etc/zabbix/zabbix_agentd.d/*.conf

This will ensure that anything ending with ``.conf`` will be read from
``/etc/zabbix/zabbix_agentd.d``.  If your Zabbix agent has been installed to a
different path, you may need to adapt to suit the target location.


Adding the discovery template to your Zabbix host
-------------------------------------------------

The Zabbix templates can be found at
https://github.com/untergeek/es_stats_zabbix/tree/master/configuration/ES_VERSION
where ``ES_VERSION`` will be the major.minor release of Elasticsearch you plan
to monitor.  Your version may or may not exist in the repository yet.

Instructions for importing templates into Zabbix can be found at
https://www.zabbix.com/documentation/3.4/manual/xml_export_import/templates

.. TIP::

    The Zabbix host that is running the ``es_stats_zabbix`` backend should be
    the one that has the template assigned.
