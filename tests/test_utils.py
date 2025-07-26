"""Test Module for utils.py"""
import unittest
from unittest.mock import patch, Mock
import logging
from lib.utils import (
    ask_for_input, get_int_value, get_next_info_and_send_signal,
    upnext_signal, notify, jsonrpc, to_unicode, get_next_info
)

_LOGGER = logging.getLogger(__name__)


class TestAskForInput(unittest.TestCase):
    """Test ask_for_input function"""

    @patch('lib.utils.xbmcgui')
    def test_ask_for_input_success(self, mock_xbmcgui):
        """Test successful input dialog"""
        mock_dialog = Mock()
        mock_dialog.input.return_value = "test search query"
        mock_xbmcgui.Dialog.return_value = mock_dialog

        result = ask_for_input("Movies")

        self.assertEqual(result, "test search query")
        mock_dialog.input.assert_called_once_with(
            defaultt='',
            heading='Search in Movies',
            type=mock_xbmcgui.INPUT_ALPHANUM
        )

    @patch('lib.utils.xbmcgui')
    def test_ask_for_input_cancelled(self, mock_xbmcgui):
        """Test cancelled input dialog"""
        mock_dialog = Mock()
        mock_dialog.input.return_value = ""
        mock_xbmcgui.Dialog.return_value = mock_dialog

        result = ask_for_input("Movies")

        self.assertIsNone(result)

    @patch('lib.utils.xbmcgui')
    def test_ask_for_input_none_returned(self, mock_xbmcgui):
        """Test input dialog returning None"""
        mock_dialog = Mock()
        mock_dialog.input.return_value = None
        mock_xbmcgui.Dialog.return_value = mock_dialog

        result = ask_for_input("Movies")

        self.assertIsNone(result)


class TestGetIntValue(unittest.TestCase):
    """Test get_int_value function"""

    def test_get_int_value_valid_int(self):
        """Test getting valid integer value"""
        dictionary = {"episode": "5", "season": "2"}

        result = get_int_value(dictionary, "episode")

        self.assertEqual(result, 5)

    def test_get_int_value_valid_int_as_int(self):
        """Test getting valid integer value when already int"""
        dictionary = {"episode": 5, "season": 2}

        result = get_int_value(dictionary, "episode")

        self.assertEqual(result, 5)

    def test_get_int_value_invalid_string(self):
        """Test getting invalid string value"""
        dictionary = {"episode": "abc", "season": "2"}

        result = get_int_value(dictionary, "episode")

        self.assertEqual(result, 0)

    def test_get_int_value_missing_key(self):
        """Test getting value for missing key"""
        dictionary = {"season": "2"}

        result = get_int_value(dictionary, "episode")

        self.assertEqual(result, 0)

    def test_get_int_value_empty_string(self):
        """Test getting empty string value"""
        dictionary = {"episode": "", "season": "2"}

        result = get_int_value(dictionary, "episode")

        self.assertEqual(result, 0)

    def test_get_int_value_zero(self):
        """Test getting zero value"""
        dictionary = {"episode": "0", "season": "2"}

        result = get_int_value(dictionary, "episode")

        self.assertEqual(result, 0)


class TestJsonRpc(unittest.TestCase):
    """Test jsonrpc function"""

    @patch('lib.utils.xbmc')
    def test_jsonrpc_basic_call(self, mock_xbmc):
        """Test basic JSON RPC call"""
        mock_xbmc.executeJSONRPC.return_value = '{"result": "OK"}'

        result = jsonrpc(method='JSONRPC.Ping')

        self.assertEqual(result, {"result": "OK"})
        mock_xbmc.executeJSONRPC.assert_called_once()

    @patch('lib.utils.xbmc')
    def test_jsonrpc_with_params(self, mock_xbmc):
        """Test JSON RPC call with parameters"""
        mock_xbmc.executeJSONRPC.return_value = '{"result": "OK"}'

        result = jsonrpc(method='JSONRPC.NotifyAll', params={'sender': 'test', 'message': 'test'})

        self.assertEqual(result, {"result": "OK"})

    @patch('lib.utils.xbmc')
    def test_jsonrpc_auto_adds_id_and_jsonrpc(self, mock_xbmc):
        """Test that JSON RPC automatically adds id and jsonrpc fields"""
        mock_xbmc.executeJSONRPC.return_value = '{"result": "OK"}'

        jsonrpc(method='JSONRPC.Ping')

        # Get the call arguments
        call_args = mock_xbmc.executeJSONRPC.call_args[0][0]
        import json  # pylint: disable=import-outside-toplevel
        call_data = json.loads(call_args)

        self.assertEqual(call_data['id'], 0)
        self.assertEqual(call_data['jsonrpc'], '2.0')
        self.assertEqual(call_data['method'], 'JSONRPC.Ping')

    @patch('lib.utils.xbmc')
    def test_jsonrpc_preserves_custom_id(self, mock_xbmc):
        """Test that JSON RPC preserves custom id"""
        mock_xbmc.executeJSONRPC.return_value = '{"result": "OK"}'

        jsonrpc(method='JSONRPC.Ping', id=123)

        call_args = mock_xbmc.executeJSONRPC.call_args[0][0]
        import json  # pylint: disable=import-outside-toplevel
        call_data = json.loads(call_args)

        self.assertEqual(call_data['id'], 123)


class TestToUnicode(unittest.TestCase):
    """Test to_unicode function"""

    def test_to_unicode_bytes(self):
        """Test converting bytes to unicode"""
        test_bytes = "Hello World".encode('utf-8')

        result = to_unicode(test_bytes)

        self.assertEqual(result, "Hello World")
        self.assertIsInstance(result, str)

    def test_to_unicode_string(self):
        """Test converting string (already unicode)"""
        test_string = "Hello World"

        result = to_unicode(test_string)

        self.assertEqual(result, "Hello World")
        self.assertIsInstance(result, str)

    def test_to_unicode_bytes_with_encoding(self):
        """Test converting bytes with specific encoding"""
        test_bytes = "Héllo Wörld".encode('latin-1')

        result = to_unicode(test_bytes, encoding='latin-1')

        self.assertEqual(result, "Héllo Wörld")

    def test_to_unicode_bytes_with_errors(self):
        """Test converting bytes with error handling"""
        test_bytes = b'\xff\xfe'  # Invalid UTF-8

        result = to_unicode(test_bytes, errors='ignore')

        self.assertIsInstance(result, str)


class TestNotify(unittest.TestCase):
    """Test notify function"""

    @patch('lib.utils.jsonrpc')
    @patch('lib.utils.Logger')
    def test_notify_success(self, mock_logger, mock_jsonrpc):
        """Test successful notification"""
        mock_jsonrpc.return_value = {"result": "OK"}

        result = notify("test.sender", "test_message", ["test_data"])

        self.assertTrue(result)
        mock_jsonrpc.assert_called_once_with(
            method='JSONRPC.NotifyAll',
            params={
                'sender': "test.sender",
                'message': "test_message",
                'data': ["test_data"]
            }
        )
        mock_logger.debug.assert_called_with('Notification sent to upnext')

    @patch('lib.utils.jsonrpc')
    @patch('lib.utils.Logger')
    def test_notify_failure(self, mock_logger, mock_jsonrpc):
        """Test failed notification"""
        mock_jsonrpc.return_value = {
            "error": {"message": "Failed to send notification"}
        }

        result = notify("test.sender", "test_message", ["test_data"])

        self.assertFalse(result)
        mock_logger.warn.assert_called_with('Failed to send notification: Failed to send notification')


class TestUpnextSignal(unittest.TestCase):
    """Test upnext_signal function"""

    @patch('lib.utils.notify')
    def test_upnext_signal(self, mock_notify):
        """Test upnext signal sending"""
        test_info = {"test": "data"}

        upnext_signal(test_info)

        mock_notify.assert_called_once()
        call_args = mock_notify.call_args

        # Check if called with keyword arguments
        if call_args.kwargs:
            self.assertEqual(call_args.kwargs['sender'], 'plugin.video.stalkervod.SIGNAL')
            self.assertEqual(call_args.kwargs['message'], 'upnext_data')
            encoded_data = call_args.kwargs['data'][0]
        else:
            self.assertEqual(call_args.args[0], 'plugin.video.stalkervod.SIGNAL')
            self.assertEqual(call_args.args[1], 'upnext_data')
            encoded_data = call_args.args[2][0]

        # Verify the data is base64 encoded JSON
        import base64  # pylint: disable=import-outside-toplevel
        import json  # pylint: disable=import-outside-toplevel
        decoded_data = json.loads(base64.b64decode(encoded_data).decode())
        self.assertEqual(decoded_data, test_info)


class TestGetNextInfoAndSendSignal(unittest.TestCase):
    """Test get_next_info_and_send_signal function"""

    @patch('lib.utils.upnext_signal')
    @patch('lib.utils.get_next_info')
    def test_get_next_info_and_send_signal(self, mock_get_next_info, mock_upnext_signal):
        """Test getting next info and sending signal"""
        test_params = {"video_id": "123", "series": "2"}
        test_url = "plugin://plugin.video.stalkervod/play?video_id=123&series=3"
        test_info = {"next_episode": {"title": "Episode 3"}}

        mock_get_next_info.return_value = test_info

        get_next_info_and_send_signal(test_params, test_url)

        mock_get_next_info.assert_called_once_with(test_params, test_url)
        mock_upnext_signal.assert_called_once_with(test_info)


class TestGetNextInfo(unittest.TestCase):
    """Test get_next_info function"""

    @patch('lib.utils.get_int_value')
    def test_get_next_info_complete(self, mock_get_int_value):
        """Test get_next_info with complete parameters"""
        test_params = {
            'video_id': '123',
            'title': 'Test Series',
            'season_no': '1',
            'series': '2',
            'poster_url': 'http://example.com/poster.jpg'
        }
        test_url = "plugin://plugin.video.stalkervod/play?video_id=123&series=3"

        # Mock get_int_value calls
        mock_get_int_value.side_effect = lambda params, key: {
            'series': 2 if 'series' in str(params) else 2
        }.get(key, 2)

        result = get_next_info(test_params, test_url)

        # Verify structure
        self.assertIn('current_episode', result)
        self.assertIn('next_episode', result)
        self.assertIn('play_url', result)

        # Verify current episode
        current = result['current_episode']
        self.assertEqual(current['tvshowid'], '123')
        self.assertEqual(current['title'], 'Test Series')
        self.assertEqual(current['season'], '1')
        self.assertEqual(current['episode'], 1)  # series - 1 = 2 - 1 = 1
        self.assertEqual(current['showtitle'], 'Test Series')

        # Verify next episode
        next_ep = result['next_episode']
        self.assertEqual(next_ep['tvshowid'], '123')
        self.assertEqual(next_ep['title'], 'Test Series')
        self.assertEqual(next_ep['season'], '1')
        self.assertEqual(next_ep['episode'], 2)  # series = 2
        self.assertEqual(next_ep['showtitle'], 'Test Series')

        # Verify play URL
        self.assertEqual(result['play_url'], test_url)

    @patch('lib.utils.get_int_value')
    def test_get_next_info_minimal_params(self, mock_get_int_value):
        """Test get_next_info with minimal parameters"""
        test_params = {
            'video_id': '456',
            'title': 'Minimal Series',
            'season_no': '2'
        }
        test_url = "plugin://plugin.video.stalkervod/play?video_id=456&series=1"

        mock_get_int_value.return_value = 1

        result = get_next_info(test_params, test_url)

        # Verify it handles missing poster_url gracefully
        current = result['current_episode']
        self.assertEqual(current['art']['tvshow.poster'], '')

        next_ep = result['next_episode']
        self.assertEqual(next_ep['art']['tvshow.poster'], '')

    @patch('lib.utils.get_int_value')
    def test_get_next_info_episode_ids(self, mock_get_int_value):
        """Test get_next_info episode ID generation"""
        test_params = {
            'video_id': '789',
            'title': 'ID Test Series',
            'season_no': '3',
            'series': '5'
        }
        test_url = "plugin://plugin.video.stalkervod/play?video_id=789&series=6"

        # Mock to return series - 1 for current, series for next
        def mock_get_int_side_effect(params, key):  # pylint: disable=unused-argument
            if key == 'series':
                return 5
            return 0

        mock_get_int_value.side_effect = mock_get_int_side_effect

        result = get_next_info(test_params, test_url)

        # Verify episode IDs are constructed correctly
        self.assertEqual(result['current_episode']['episodeid'], '7894')  # video_id + (series-1)
        self.assertEqual(result['next_episode']['episodeid'], '7895')     # video_id + series

    @patch('lib.utils.get_int_value')
    def test_get_next_info_art_fields(self, mock_get_int_value):
        """Test get_next_info art field population"""
        test_params = {
            'video_id': '999',
            'title': 'Art Test Series',
            'season_no': '1',
            'poster_url': 'http://example.com/test_poster.jpg'
        }
        test_url = "plugin://plugin.video.stalkervod/play?video_id=999&series=2"

        mock_get_int_value.return_value = 1

        result = get_next_info(test_params, test_url)

        # Verify all art fields are populated with poster_url
        expected_art = {
            'thumb': '',
            'tvshow.clearart': 'http://example.com/test_poster.jpg',
            'tvshow.clearlogo': 'http://example.com/test_poster.jpg',
            'tvshow.fanart': 'http://example.com/test_poster.jpg',
            'tvshow.landscape': 'http://example.com/test_poster.jpg',
            'tvshow.poster': 'http://example.com/test_poster.jpg',
        }

        self.assertEqual(result['current_episode']['art'], expected_art)
        self.assertEqual(result['next_episode']['art'], expected_art)


if __name__ == '__main__':
    unittest.main()
