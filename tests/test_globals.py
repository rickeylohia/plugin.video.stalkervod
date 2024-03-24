"""Test Module for globals.py"""
import os
import unittest
import logging
from unittest.mock import patch
from lib.globals import G

_LOGGER = logging.getLogger(__name__)


@patch('sys.argv', ['plugin://plugin.video.stalkervod/', '1'])
class TestGlobals(unittest.TestCase):
    """Class to test init of globals variables"""

    @patch('sys.argv', ['plugin://plugin.video.stalkervod/', '1'])
    def __init__(self, method_name='runTest'):
        """Init test"""
        super().__init__(method_name)
        G.init_globals()

    def test_1_init_globals(self):
        """Test init global settings"""
        self.assertEqual(G.addon_config.handle, 1)
        self.assertEqual(G.addon_config.url, 'plugin://plugin.video.stalkervod/')
        self.assertEqual(G.addon_config.addon_id, 'plugin.video.stalkervod')
        self.assertEqual(G.addon_config.addon_data_path, os.getcwd())
        self.assertEqual(G.addon_config.token_path, os.path.join(os.getcwd(), 'tests/userdata/addon_data/plugin.video.stalkervod'))
        self.assertEqual(G.portal_config.mac_cookie, 'mac=00:2D:73:68:91:11')
        self.assertEqual(G.portal_config.device_id, 'SUEHFIOHR23IYR2U39U298EUDOIWHJDOIWEJHDIOHJWE')
        self.assertEqual(G.portal_config.device_id_2, '9384UR9UJFHJSDIFH9348EYFIUWDHFIHWDIFHEDHFE')
        self.assertEqual(G.portal_config.signature, '9834UROIWEHDJEFKIJHDF983EUFISDHFDKHJFKSJDHFKS')
        self.assertEqual(G.portal_config.serial_number, '02983409283402')
        self.assertEqual(G.portal_config.portal_base_url, 'http://xyz.com')
        self.assertEqual(G.portal_config.server_address, 'http://xyz.com/stalker_portal/c/')
        self.assertEqual(G.portal_config.portal_url, 'http://xyz.com/stalker_portal/server/load.php')

    def test_2_get_handle(self):
        """Test get_handle"""
        self.assertEqual(G.get_handle(), 1)

    def test_3_get_custom_thumb_path(self):
        """Test get_handle"""
        self.assertEqual(G.get_custom_thumb_path('file.png'),
                         os.path.join(os.getcwd(), 'resources', 'media', 'file.png'))

    def test_4_get_plugin_url(self):
        """Test get_handle"""
        self.assertEqual(G.get_plugin_url({'action': 'test'}), 'plugin://plugin.video.stalkervod/?action=test')

    def test_5_get_portal_url(self):
        """Test get_portal_url"""
        G.portal_config.server_address = 'http://xyz.com:8080/c'
        portal_url = G.get_portal_url()
        self.assertEqual(portal_url, 'http://xyz.com:8080/server/load.php')
