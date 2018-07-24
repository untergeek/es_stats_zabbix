"""Test the default settings"""
from es_stats_zabbix.defaults.settings import config_file
from . import FileTestCase

class TestConfigFile(FileTestCase):
    """TestConfigFile test class"""
    def test_no_default(self):
        """Test whether the default exists"""
        self.assertIsNone(config_file())
    def test_provided(self):
        """Test if a viable filename has been provided"""
        self.assertEqual(self.args['filename'], config_file(testpath=[self.args['filename']]))
    