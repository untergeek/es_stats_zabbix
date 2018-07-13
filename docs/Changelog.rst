.. _changelog:

Changelog
=========

0.9.12 (? ? ?)
--------------

**Alpha-release of pending 1.0 version**

  * Basically a complete rewrite.  This version is not yet ready for mass
    consumption.  Still pending are:
    - Zabbix 3.x template for 5.x and 6.x ES versions.
    - Installation scripts/config files
    - Init scripts for the backend (SysV, Upstart)
    - Documentation
    - Make different templates for different Zabbix versions, if necessary.
  * Testing this pre-release version requires a ``git clone`` and
    ``python setup.py install`` or ``pip install .`` from the source directory.

**New**

  * Flask-based backend listener that enables cached reads of the cluster
    stats. This prevents repeated calls from completely hammering the cluster
    with repeated stats calls. Currently intended to listen on localhost port
    7600, so that the Zabbix UserParameter script can simply read localhost.
    Cache timeout defaults to 60 seconds, and is configurable.
  * Use YAML based configuration.
    - Elasticsearch configuration block
    - Logging configuration block
    - Backend configuration block
    - `do_not_discover` block
  * Uses update `es_stats` and new `es_client` modules.
    - `es_client` allows monitoring of X-Pack secured Elasticsearch clusters
  * Discovery based on value (``bool`` for true/false, ``unsigned`` for
    Zabbix's `unsigned` integer values, ``float``, and ``character``).  This
    allows Zabbix to automatically discover items for the correct item type.
  * Block individual endpoints from LLD by enumerating them in the
    ``do_not_discover`` block in the configuration file.

**Interim Fix List**

  * Fixed issues with the config_override function not behaving as expected.
  * Pruned unnecessary code.
  * Added unit and integration tests.
  * Added endpoints
  * Switched to using ``setup.cfg`` instead of everything in ``setup.py``
  * Add some backward compatibility.
  * Compatibility testing with different versions of Elasticsearch (all 5.x and
    6.x minor releases) and Python client versions (2.7, 3.5, 3.6)
  * Add ``esz_nodes_discovery`` for node related macros for discovery.
  * Add systemd service file.
  * Full test of prototype template with discovery of cluster and nodes.
  * Added ``esz_cluster_discovery`` for cluster related macros for LLD.
  * Added ``run_display_endpoints.py`` to show all endpoints for a given node.
    This works better with ``--apidebug`` enabled in the backend, as it pretty
    prints the results.
  * Reworked the launch scripts to use similar code as much as possible.
  * Moved a lot of classes and modules around.

0.1.4 (22 June 2016)
--------------------

**Bug Fixes**

  * Fix ``es_stats`` dependency to be 0.2.1, which fixes some reported bugs.

**General**

  * Fix docs in their as yet incomplete state to at least not have incorrect
    information

0.1.1 (7 October 2015)
----------------------

**New**

  * Batch now reports count of items which failed on command-line.  This
    enables you to call batch as a Zabbix agent item, and report a result.

**Bug Fixes**

  * Prevent empty lists in batches from generating an error.

0.1.0 (7 October 2015)
----------------------

**New**

  * Refactor all Zabbix key parsing.  Much simpler now.
  * Improved logging.

0.0.2 (6 October 2015)
----------------------

**Bug fixes**

  * Put kaptan dependency in place

0.0.1 (6 October 2015)
----------------------

**Announcement**

  * Initial release
