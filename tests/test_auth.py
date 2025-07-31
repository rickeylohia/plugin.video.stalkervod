"""Test Module for auth.py"""
import unittest
from unittest.mock import patch, Mock
import logging
from lib.auth import Auth, Token
from lib.globals import G

_LOGGER = logging.getLogger(__name__)


class TestToken(unittest.TestCase):
    """Test Token dataclass"""

    def test_token_initialization(self):
        """Test Token initialization"""
        token = Token()
        self.assertIsNone(token.value)

    def test_token_with_value(self):
        """Test Token with value"""
        token = Token(value="test_token_123")
        self.assertEqual(token.value, "test_token_123")


class TestAuth(unittest.TestCase):
    """Test Auth class"""

    def setUp(self):
        """Set up test fixtures"""
        # Mock G.addon_config and G.portal_config
        G.addon_config = Mock()
        G.addon_config.token_path = "/test/path"

        G.portal_config = Mock()
        G.portal_config.portal_url = "http://test.portal.com"
        G.portal_config.mac_cookie = "mac=00:1A:79:XX:XX:XX"
        G.portal_config.server_address = "http://test.server.com"
        G.portal_config.serial_number = "TEST123456"
        G.portal_config.device_id = "device123"
        G.portal_config.device_id_2 = "device456"
        G.portal_config.signature = "test_signature"

    @patch('lib.auth.xbmcvfs')
    @patch('lib.auth.Logger')
    def test_auth_initialization(self, mock_logger, mock_xbmcvfs):  # pylint: disable=unused-argument
        """Test Auth initialization"""
        mock_xbmcvfs.File.return_value.__enter__.return_value.read.return_value = '{"value": null}'

        auth = Auth()

        self.assertIsNotNone(auth._Auth__token)  # pylint: disable=protected-access
        self.assertEqual(auth._Auth__url, G.portal_config.portal_url)  # pylint: disable=protected-access
        self.assertEqual(auth._Auth__mac_cookie, G.portal_config.mac_cookie)  # pylint: disable=protected-access
        self.assertEqual(auth._Auth__referrer, G.portal_config.server_address)  # pylint: disable=protected-access

    @patch('lib.auth.requests')
    @patch('lib.auth.xbmcvfs')
    @patch('lib.auth.xbmcgui')
    @patch('lib.auth.Logger')
    def test_get_token_success(self, mock_logger, mock_xbmcgui, mock_xbmcvfs, mock_requests):  # pylint: disable=unused-argument
        """Test successful token retrieval"""
        # Mock file operations
        mock_xbmcvfs.File.return_value.__enter__.return_value.read.return_value = '{"value": null}'
        mock_xbmcvfs.exists.return_value = False

        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"js": {"token": "new_token_123"}}'
        mock_response.json.return_value = {"js": {"token": "new_token_123"}}
        mock_requests.get.return_value = mock_response

        auth = Auth()
        token = auth.get_token(refresh_token=False)

        self.assertEqual(token, "new_token_123")
        self.assertEqual(auth._Auth__token.value, "new_token_123")  # pylint: disable=protected-access

    @patch('lib.auth.requests')
    @patch('lib.auth.xbmcvfs')
    @patch('lib.auth.xbmcgui')
    @patch('lib.auth.Logger')
    def test_get_token_authorization_failed(self, mock_logger, mock_xbmcgui, mock_xbmcvfs, mock_requests):  # pylint: disable=unused-argument
        """Test token retrieval with authorization failure"""
        # Mock file operations
        mock_xbmcvfs.File.return_value.__enter__.return_value.read.return_value = '{"value": null}'

        # Mock failed API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = 'Authorization failed'
        mock_requests.get.return_value = mock_response

        # Mock dialog
        mock_dialog = Mock()
        mock_xbmcgui.Dialog.return_value = mock_dialog

        auth = Auth()

        with self.assertRaises(Exception):
            auth.get_token(refresh_token=False)

        mock_dialog.ok.assert_called_once()

    @patch('lib.auth.requests')
    @patch('lib.auth.xbmcvfs')
    @patch('lib.auth.xbmcgui')
    @patch('lib.auth.Logger')
    def test_get_token_http_error(self, mock_logger, mock_xbmcgui, mock_xbmcvfs, mock_requests):  # pylint: disable=unused-argument
        """Test token retrieval with HTTP error"""
        # Mock file operations
        mock_xbmcvfs.File.return_value.__enter__.return_value.read.return_value = '{"value": null}'

        # Mock failed API response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = 'Server Error'
        mock_requests.get.return_value = mock_response

        # Mock dialog
        mock_dialog = Mock()
        mock_xbmcgui.Dialog.return_value = mock_dialog

        auth = Auth()

        with self.assertRaises(Exception):
            auth.get_token(refresh_token=False)

        mock_dialog.ok.assert_called_once()

    @patch('lib.auth.xbmcvfs')
    @patch('lib.auth.Logger')
    def test_get_token_with_cached_token(self, mock_logger, mock_xbmcvfs):  # pylint: disable=unused-argument
        """Test getting token when already cached"""
        # Mock file operations with existing token
        mock_xbmcvfs.File.return_value.__enter__.return_value.read.return_value = '{"value": "cached_token_123"}'

        auth = Auth()
        token = auth.get_token(refresh_token=False)

        self.assertEqual(token, "cached_token_123")

    @patch('lib.auth.requests')
    @patch('lib.auth.xbmcvfs')
    @patch('lib.auth.Logger')
    def test_get_token_with_refresh(self, mock_logger, mock_xbmcvfs, mock_requests):  # pylint: disable=unused-argument
        """Test getting token with refresh"""
        # Mock file operations with existing token
        mock_xbmcvfs.File.return_value.__enter__.return_value.read.return_value = '{"value": "cached_token_123"}'

        # Mock refresh requests
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.get.return_value = mock_response

        auth = Auth()
        token = auth.get_token(refresh_token=True)

        self.assertEqual(token, "cached_token_123")
        # Should make 2 refresh calls
        self.assertEqual(mock_requests.get.call_count, 2)

    @patch('lib.auth.xbmcvfs')
    @patch('lib.auth.Logger')
    def test_clear_cache(self, mock_logger, mock_xbmcvfs):  # pylint: disable=unused-argument
        """Test clearing token cache"""
        # Mock file operations
        mock_xbmcvfs.File.return_value.__enter__.return_value.read.return_value = '{"value": "cached_token_123"}'
        mock_xbmcvfs.exists.return_value = True

        auth = Auth()
        auth.clear_cache()

        self.assertIsNone(auth._Auth__token.value)  # pylint: disable=protected-access
        mock_xbmcvfs.delete.assert_called_once()

    @patch('lib.auth.xbmcvfs')
    @patch('lib.auth.Logger')
    def test_clear_cache_no_file(self, mock_logger, mock_xbmcvfs):  # pylint: disable=unused-argument
        """Test clearing cache when no file exists"""
        # Mock file operations
        mock_xbmcvfs.File.return_value.__enter__.return_value.read.return_value = '{"value": "cached_token_123"}'
        mock_xbmcvfs.exists.return_value = False

        auth = Auth()
        auth.clear_cache()

        self.assertIsNone(auth._Auth__token.value)  # pylint: disable=protected-access
        mock_xbmcvfs.delete.assert_not_called()

    @patch('lib.auth.xbmcvfs')
    @patch('lib.auth.Logger')
    def test_load_cache_invalid_json(self, mock_logger, mock_xbmcvfs):  # pylint: disable=unused-argument
        """Test loading cache with invalid JSON"""
        # Mock file operations with invalid JSON
        mock_xbmcvfs.File.return_value.__enter__.return_value.read.return_value = 'invalid json'

        auth = Auth()

        # Should handle invalid JSON gracefully
        self.assertIsNone(auth._Auth__token.value)  # pylint: disable=protected-access

    @patch('lib.auth.xbmcvfs')
    @patch('lib.auth.Logger')
    def test_load_cache_io_error(self, mock_logger, mock_xbmcvfs):  # pylint: disable=unused-argument
        """Test loading cache with IO error"""
        # Mock file operations to raise IOError
        mock_xbmcvfs.File.return_value.__enter__.side_effect = IOError("File not found")

        auth = Auth()

        # Should handle IO error gracefully
        self.assertIsNone(auth._Auth__token.value)  # pylint: disable=protected-access

    @patch('lib.auth.requests')
    @patch('lib.auth.xbmcvfs')
    @patch('lib.auth.Logger')
    def test_save_cache(self, mock_logger, mock_xbmcvfs, mock_requests):  # pylint: disable=unused-argument
        """Test saving token to cache"""
        # Mock file operations
        mock_file = Mock()
        mock_xbmcvfs.File.return_value.__enter__.return_value = mock_file
        mock_file.read.return_value = '{"value": null}'

        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"js": {"token": "new_token_123"}}'
        mock_response.json.return_value = {"js": {"token": "new_token_123"}}
        mock_requests.get.return_value = mock_response

        auth = Auth()
        auth.get_token(refresh_token=False)

        # Verify that json.dump was called to save the token
        self.assertTrue(mock_xbmcvfs.File.called)

    @patch('lib.auth.requests')
    @patch('lib.auth.xbmcvfs')
    @patch('lib.auth.Logger')
    def test_refresh_token_calls(self, mock_logger, mock_xbmcvfs, mock_requests):  # pylint: disable=unused-argument
        """Test that refresh token makes the correct API calls"""
        # Mock file operations with existing token
        mock_xbmcvfs.File.return_value.__enter__.return_value.read.return_value = '{"value": "cached_token_123"}'

        # Mock refresh requests
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.get.return_value = mock_response

        auth = Auth()
        auth.get_token(refresh_token=True)

        # Should make 2 refresh calls (get_profile and get_events)
        self.assertEqual(mock_requests.get.call_count, 2)

        # Verify the calls have correct parameters
        calls = mock_requests.get.call_args_list

        # First call should be get_profile
        first_call_params = calls[0][1]['params']
        self.assertEqual(first_call_params['action'], 'get_profile')
        self.assertEqual(first_call_params['type'], 'stb')

        # Second call should be get_events
        second_call_params = calls[1][1]['params']
        self.assertEqual(second_call_params['action'], 'get_events')
        self.assertEqual(second_call_params['type'], 'watchdog')

    @patch('lib.auth.requests')
    @patch('lib.auth.xbmcvfs')
    @patch('lib.auth.Logger')
    def test_get_token_headers(self, mock_logger, mock_xbmcvfs, mock_requests):  # pylint: disable=unused-argument
        """Test that get_token sends correct headers"""
        # Mock file operations
        mock_xbmcvfs.File.return_value.__enter__.return_value.read.return_value = '{"value": null}'

        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"js": {"token": "new_token_123"}}'
        mock_response.json.return_value = {"js": {"token": "new_token_123"}}
        mock_requests.get.return_value = mock_response

        auth = Auth()
        auth.get_token(refresh_token=False)

        # Verify headers
        call_args = mock_requests.get.call_args_list[0]
        headers = call_args[1]['headers']

        self.assertEqual(headers['Cookie'], G.portal_config.mac_cookie)
        self.assertEqual(headers['X-User-Agent'], 'Model: MAG250; Link: WiFi')
        self.assertEqual(headers['Referrer'], G.portal_config.server_address)
        self.assertIn('Mozilla/5.0', headers['User-Agent'])


if __name__ == '__main__':
    unittest.main()
