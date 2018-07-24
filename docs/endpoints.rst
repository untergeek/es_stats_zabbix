.. _endpoints:

``endpoints``
=============

This is an example configuration block::

    endpoints:
      cluster:
        60s:
          clusterstats:
            - ...
      coordinating:
        60s:
          nodestats:
            - ...
      data:
        60s:
          nodestats:
            - ...

``cluster``
-----------

This block contains endpoints exclusively used for cluster-level monitoring.
These include the cluster ``health``, ``clusterstate``, and ``clusterstats``
metrics.

The default values included are probably sufficient, but you can remove any
items that you do not want discovered and monitored.

``coordinating``
----------------

In Elasticsearch terminology, all nodes can act as *coordinating* nodes, so
these metrics will be monitored for every node in the cluster.  The stats are
broken down first by interval (``60s``, ``300s``, ``900s``), and by API
endpoint (``nodestats``, ``nodeinfo``).

**Everything included here will be discovered, and monitored.**

``data``
--------

Differing from ``coordinating`` node, these stats are specific to data nodes.
All endpoints specified here will be discovered and monitored.

Other Node Types
----------------

While no endpoints are provided out of the box, you can also monitor:

* ``ingest``
* ``master``
* ``ml`` - Machine Learning
