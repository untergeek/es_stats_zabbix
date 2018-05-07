from es_stats_zabbix.defaults.settings import config_file
from . import FileTestCase

class TestConfigFile(FileTestCase):
    def test_no_default(self):
        self.assertIsNone(config_file())
    def test_provided(self):
        self.assertEqual(self.args['filename'], config_file(testpath=[self.args['filename']]))
    