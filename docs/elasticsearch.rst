.. _elasticsearch:

``elasticsearch``
=================

This is an example configuration block::

    elasticsearch:
      master_only: false
      skip_version_test: false
      client:
        hosts:
          - 127.0.0.1
        port: 9200
        url_prefix:
        timeout: 30
        username:
        password:
        verify_certs: false
        use_ssl: false
        ca_certs:
        client_cert:
        client_key:
        ssl_version:
        ssl_assert_hostname:
        http_compress: true
      aws:
        sign_requests: false
        aws_region: us_east

``master_only``
---------------

``master_only`` should be ``true`` or ``false``. This setting specifies that
Elasticsearch is permitted to establish a client connection *only* with the
elected master node in the cluster.

The default value is ``false``.

.. TIP::
    This option only works if there is one, and only one host provided for
    ``hosts``.

``skip_version_test``
---------------------

``skip_version_test`` may permit use with an unsupported version of
Elasticsearch.  The value should be ``true`` or ``false``.

The default value is ``false``.

``client``
----------

``client`` is a sub-section that contains further options for establishing a
client connection to Elasticsearch.  The options are as follows:

``hosts``
~~~~~~~~~

``hosts`` is an array of potential hosts to connect to.  If multiple are
specified, requests will be performed in a round robin approach across all
*available* hosts.  Any acceptable YAML syntax for lists/arrays will work.

The default value is ``127.0.0.1``

``url_prefix``
~~~~~~~~~~~~~~
Set this if you have Elasticsearch behind a proxy or some other end point, and
have configured an additional endpoint before the API portion of the URL.

For example, if you have to type ``https://www.example.com/myprefix/_cat`` to
reach the ``_cat`` API, then your ``url_prefix`` would be ``myprefix``.

There is no default value, or the default value is empty.

``timeout``
~~~~~~~~~~~
How long a client connection should wait (in seconds) for a response before
timing out.

The default value is `30`, meaning 30 seconds.

``username``
~~~~~~~~~~~~

If Elasticsearch requires a username and password to authenticate, specify the
username here.

There is no default value, or the default value is empty.

``password``
~~~~~~~~~~~~

If Elasticsearch requires a username and password to authenticate, specify the
password here.

There is no default value, or the default value is empty.

``verify_certs``
~~~~~~~~~~~~~~~~

The value of this should be ``true`` or ``false``, and determines whether SSL
certificates will be verified.

The default value is ``false``, though you should create your certificates in
a way that authenticity can be verified.

``use_ssl``
~~~~~~~~~~~

The value of this should be ``true`` or ``false``, and determines whether
SSL/TLS will be used to connect to Elasticsearch.

The default value is ``false``

``ca_certs``
~~~~~~~~~~~~

The value of this can be a single value, or an array of values.  Each value
must be a filesystem path to a certificate authority file.

There is no default value, but if not specified, and ``use_ssl`` is ``true``,
it will try to use the default certificates provided by ``certifi`` for
verification purposes.

``client_cert``
~~~~~~~~~~~~~~~

This setting should point to a filesystem path to a client public key (or
certificate) file to be used for two-way SSL authentication/verification.

There is no default value, or the default value is empty.

``client_key``
~~~~~~~~~~~~~~

This setting should point to a filesystem path to a client private key file to
be used for two-way SSL authentication/verification.

There is no default value, or the default value is empty.

``ssl_version``
~~~~~~~~~~~~~~~

You can specify what versions of SSL/TLS to permit here.

Acceptable choices are:

* ``SSLv23``
* ``SSLv2``
* ``SSLv3``
* ``TLSv1``

There may be other potential values for different environments.

The default value is ``SSLv23``

``ssl_assert_hostname``
~~~~~~~~~~~~~~~~~~~~~~~

If the value of this setting is ``true``, hostname verification will take
place, otherwise it will not.

The default value is ``false``.

``http_compress``
~~~~~~~~~~~~~~~~~

The value must be ``true`` or ``false`` and determines whether gzip compression
will be used for client traffic to Elasticsearch.

The default value is ``false``.

``aws``
-------

If you are trying to monitor an Elasticsearch cluster in AWS with Zabbix, you
can!

``sign_requests``
~~~~~~~~~~~~~~~~~

This value should be ``true`` if you want your requests to be signed with AWS
IAM credentials retrieved from your environment.

The order in which credentials will be searched for is:

1. Environment variables
2. Shared credential file (``=/.aws/credentials``)
3. AWS config file (``=/.aws/config``)
4. Boto2 config file (``/etc/boto.cfg`` and ``=/.boto``)
5. Instance metadata service on an Amazon EC2 instance that has an IAM role
   configured.

The default value is ``false``.

``aws_region``
~~~~~~~~~~~~~~

This should be an AWS region, such as ``us-east``, or left empty.

There is no default value, or the default value is empty.
