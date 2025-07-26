"""Test Module for globals.py"""
import os
import unittest
import logging
from unittest.mock import patch, Mock
from lib.globals import G

_LOGGER = logging.getLogger(__name__)


class TestGlobals(unittest.TestCase):
    """Class to test init of globals variables"""

    def setUp(self):
        """Set up test fixtures"""
        # Reset the global state
        G.addon_config.url = None
        G.addon_config.handle = None
        G.addon_config.addon_id = None
        G.addon_config.addon_data_path = None
        G.addon_config.token_path = None
        G.portal_config.mac_cookie = None
        G.portal_config.device_id = None
        G.portal_config.device_id_2 = None
        G.portal_config.signature = None
        G.portal_config.serial_number = None
        G.portal_config.server_address = None
        G.portal_config.portal_base_url = None
        G.portal_config.portal_url = None
        setattr(G, '_GlobalVariables__is_addd_on_first_run', None)

    @patch('sys.argv', ['plugin://plugin.video.stalkervod/', '1'])
    @patch('lib.globals.xbmcvfs')
    @patch('lib.globals.xbmcaddon')
    def test_1_init_globals(self, mock_xbmcaddon, mock_xbmcvfs):
        """Test init global settings"""
        # Mock addon
        mock_addon = Mock()
        mock_addon.getAddonInfo.side_effect = lambda x: {
            'id': 'plugin.video.stalkervod',
            'name': 'Stalker VOD',
            'path': os.getcwd(),
            'profile': os.path.join(os.getcwd(), 'tests/userdata/addon_data/plugin.video.stalkervod')
        }[x]
        mock_addon.getSetting.side_effect = lambda x: {
            'mac_address': '00:2D:73:68:91:11',
            'device_id': 'SUEHFIOHR23IYR2U39U298EUDOIWHJDOIWEJHDIOHJWE',
            'device_id_2': '9384UR9UJFHJSDIFH9348EYFIUWDHFIHWDIFHEDHFE',
            'signature': '9834UROIWEHDJEFKIJHDF983EUFISDHFDKHJFKSJDHFKS',
            'serial_number': '02983409283402',
            'server_address': 'http://xyz.com/stalker_portal/c/',
            'alternative_context_path': 'false'
        }[x]
        mock_xbmcaddon.Addon.return_value = mock_addon

        # Mock xbmcvfs
        mock_xbmcvfs.translatePath.return_value = os.path.join(os.getcwd(), 'tests/userdata/addon_data/plugin.video.stalkervod')
        mock_xbmcvfs.exists.return_value = False
        mock_xbmcvfs.mkdirs.return_value = True

        # Initialize globals
        G.init_globals()

        # Test assertions
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
        G.addon_config.handle = 1
        self.assertEqual(G.get_handle(), 1)

    def test_3_get_custom_thumb_path(self):
        """Test get_custom_thumb_path"""
        G.addon_config.addon_data_path = os.getcwd()
        self.assertEqual(G.get_custom_thumb_path('file.png'),
                         os.path.join(os.getcwd(), 'resources', 'media', 'file.png'))

    def test_4_get_plugin_url(self):
        """Test get_plugin_url"""
        G.addon_config.url = 'plugin://plugin.video.stalkervod/'
        self.assertEqual(G.get_plugin_url({'action': 'test'}), 'plugin://plugin.video.stalkervod/?action=test')

    def test_5_get_portal_url(self):
        """Test get_portal_url"""
        G.portal_config.server_address = 'http://xyz.com:8080/c'
        G.portal_config.alternative_context_path = False
        G.portal_config.portal_base_url = 'http://xyz.com:8080'
        portal_url = G.get_portal_url()
        self.assertEqual(portal_url, 'http://xyz.com:8080/server/load.php')
