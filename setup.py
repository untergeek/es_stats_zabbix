import os
import re
import sys
from setuptools import setup

# Utility function to read from file.
def fread(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def get_version():
    VERSIONFILE="es_stats_zabbix/_version.py"
    verstrline = fread(VERSIONFILE).strip()
    vsre = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(vsre, verstrline, re.M)
    if mo:
        VERSION = mo.group(1)
    else:
        raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))
    build_number = os.environ.get('ESSTATSZABBIX_BUILD_NUMBER', None)
    if build_number:
        return VERSION + "b{}".format(build_number)
    return VERSION

def get_install_requires():
    res = ['elasticsearch>=1.6.0' ]
    res.append('es_stats>=0.2.1')
    res.append('click>=3.3')
    res.append('zbxsend>=0.1.6')
    res.append('kaptan>=0.5.8')
    return res

setup(
    name = "es_stats_zabbix",
    version = get_version(),
    author = "Aaron Mildenstein",
    author_email = "aaron@mildensteins.com",
    description = "Collect stats from es_stats for ingest by Zabbix ",
    long_description=fread('README.rst'),
    url = "http://github.com/untergeek/es_stats_zabbix",
    download_url = "https://github.com/untergeek/es_stats_zabbix/tarball/v" + get_version(),
    license = "Apache License, Version 2.0",
    install_requires = get_install_requires(),
    keywords = "elasticsearch stats",
    packages = ["es_stats_zabbix"],
    include_package_data=True,
        entry_points = {
        "console_scripts" : ["es_stats_zabbix = es_stats_zabbix.es_stats_zabbix:main"]
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
    ],
)
