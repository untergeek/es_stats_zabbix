.. _configuration:

Configuration
=============

In order to prevent a high number of individual calls to the Elasticsearch API,
``es_stats_zabbix`` uses a caching client backend.  The TTL on the cache can be
tuned, with a default of 60 seconds.


Configuring ``es_stats_zabbix``
-------------------------------

.. toctree::
   :maxdepth: 2

   configfile
   zabbix


Launching the Backend
---------------------

The backend must be running for the ``esz_*`` scripts to work.

Install the configuration file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The backend configuration file should be installed at
``/etc/es_stats_zabbix/config.yml``.

This will be overridden by ``$HOME/.es_stats_zabbix/config.yml``, if it exists.

``systemd``
~~~~~~~~~~~

Install unit file
^^^^^^^^^^^^^^^^^

A sample systemd unit file is provided at https://github.com/untergeek/es_stats_zabbix/blob/master/configuration/systemd/esz_backend.service

This file can be placed at ``/etc/systemd/system/esz_backend.service``.  After
installing the file there, run ``systemctl daemon-reload`` to have the system
recognize the new unit file.


Launching via ``systemd``
^^^^^^^^^^^^^^^^^^^^^^^^^

::

    systemctl start esz_backend.service

Manually launching the backend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The path to the entry points must be known.  If the scripts were installed to
a virtualenv, you might be able to launch via:

::

    /my/chosen/path/bin/esz_backend

