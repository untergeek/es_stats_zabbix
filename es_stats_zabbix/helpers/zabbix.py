"""
Zabbix Sender Module
"""

import logging
import os
import random
import shutil
import string
import tempfile
import protobix
from dotmap import DotMap
from es_stats_zabbix.helpers.utils import status_map

class ZbxSendObject():
    """Zabbix Sender Class"""
    def __init__(self, zbx_conf):
        self.zabbix = zbx_conf
        self.debug = False
        self.logger = logging.getLogger('esz.ZbxSendObject')
        if logging.getLogger().getEffectiveLevel() == 10:
            self.debug = True

    def create_random_directory(self):
        """Create a random directory path"""
        dirname = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        directory = tempfile.mkdtemp(suffix=dirname)
        if not os.path.exists(directory):
            os.makedirs(directory)
        self.tmpdir = directory

    def create_tmpfile(self):
        """Create a random named tmpfile in a randomly created directory"""
        self.create_random_directory()
        self.zbxconfigfile = os.path.join(self.tmpdir, 'zabbix_agentd.conf')
        with open(self.zbxconfigfile, 'w') as configfile:
            for k in list(self.zabbix.keys()):
                data = '{0}={1}\n'.format(k, self.zabbix[k])
                configfile.write(data)

    def delete_tmpfile(self):
        """Delete the full tmpdir created in create_random_directory"""
        if os.path.exists(self.tmpdir):
            shutil.rmtree(self.tmpdir)

    def zbx_sender(self, host, data, data_type='items'):
        """Function to send trapper data to Zabbix"""
        # In order to use the Zabbix Agent Config portion of protobix, I cannot simply provide
        # a config dictionary.  I have to provide a config file.  These lines will create a
        # viable, temporary config file and then delete it once the config object has been created.
        self.create_tmpfile()
        pzalogger = None
        pdclogger = None
        if self.debug:
            pzalogger = logging.getLogger('protobix.ZabbixAgentConfig')
            pdclogger = logging.getLogger('protobix.DataContainer')
        zbx_config = protobix.ZabbixAgentConfig(config_file=self.zbxconfigfile, logger=pzalogger)
        self.delete_tmpfile()
        zbx_datacontainer = protobix.DataContainer(config=zbx_config, logger=pdclogger)
        zbx_datacontainer.data_type = data_type
        self.logger.debug('DATA = {0}'.format({host:data}))
        zbx_datacontainer.add({host:data})
        return zbx_datacontainer.send()
