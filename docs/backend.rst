.. _backend:

``backend``
===========

This is an example configuration block::

    backend:
      host: 127.0.0.1
      port: 7600
      cache_timeout: 60
      debug: false

``host``
--------

``host`` should *always* be ``localhost`` or ``127.0.0.1``.

The backend should not be available to outside queries by itself, so the value
of this should never permit outside access.

The default value is ``127.0.0.1``

``port``
--------

The port to listen on.

The default value is ``7600``

``cache_timeout``
-----------------

How long to cache the values from an API call.

The default value is ``60``, meaning 60 seconds.

``debug``
---------

If ``true``, turn on debug logging for the Flask backend.  This results in
pretty-printing the command-line output for easier reading.

The default value is ``false``
