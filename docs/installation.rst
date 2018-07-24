.. _installation:

Installation
============

The initial installation requires Python 2.7.9 or better, though Python 3.5+
are preferred.

Using ``setup.py``
------------------

Clone the GitHub repository or download the source.

Ensure you have ``pip`` and ``virtualenv`` installed before proceeding.

``virtualenv /my/chosen/path``

``source /my/chosen/path/bin/activate``

Go to the directory where you cloned the GitHub repository, or expanded the
source archive and run the following:

``pip install -r requirements.txt``

``pip install .``

This will install the necessary python entry points to ``/my/chosen/path/bin/``
