.. _changelog:

Changelog
=========

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

  * Batch now reports count of items which failed on command-line.  This enables
    you to call batch as a Zabbix agent item, and report a result.

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
