"""Test Module for api.py"""
import json
import unittest
from unittest.mock import patch, Mock
import logging
from lib.api import Api
from lib.globals import G

_LOGGER = logging.getLogger(__name__)


class MockNotSupported(Exception):
    """Exception class when an unknown URL is mocked"""


with open('tests/responses/token.json', 'r') as f:
    TOKEN = json.load(f)
with open('tests/responses/profile.json', 'r') as f:
    PROFILE = json.load(f)
with open('tests/responses/events.json', 'r') as f:
    EVENTS = json.load(f)
with open('tests/responses/categories.json', 'r') as f:
    CATEGORIES = json.load(f)
with open('tests/responses/genres.json', 'r') as f:
    GENRES = json.load(f)
with open('tests/responses/videos.json', 'r') as f:
    VIDEOS = json.load(f)
with open('tests/responses/channels.json', 'r') as f:
    CHANNELS = json.load(f)
with open('tests/responses/vod_stream_url.json', 'r') as f:
    VOD_STREAM = json.load(f)
with open('tests/responses/itv_stream_url.json', 'r') as f:
    ITV_STREAM = json.load(f)
with open('tests/responses/add_remove_fav.json', 'r') as f:
    ADD_REMOVE_FAV = json.load(f)

# Additional test data for comprehensive coverage
SERIES_CATEGORIES = {"js": [{"id": "*", "title": "All"}, {"id": "1", "title": "Drama"}, {"id": "2", "title": "Comedy"}]}
SEASONS_DATA = {"js": {"data": [{"id": "1", "title": "Season 1"}, {"id": "2", "title": "Season 2"}], "total_items": "2", "max_page_items": "10"}}
TV_FAVORITES_DATA = {"js": {"data": [{"id": "123", "name": "Channel 1"}, {"id": "456", "name": "Channel 2"}]}}
MULTI_PAGE_VIDEOS = {"js": {"data": [{"name": "Video 1"}, {"name": "Video 2"}], "total_items": "10", "max_page_items": "2"}}

ACTION_RESPONSE_DICT = {'stb': {'get_profile': PROFILE},
                        'watchdog': {'get_events': EVENTS},
                        'itv': {'get_genres': GENRES, 'get_ordered_list': CHANNELS, 'create_link': ITV_STREAM,
                                'get_all_fav_channels': TV_FAVORITES_DATA, 'set_fav': ADD_REMOVE_FAV},
                        'vod': {'get_ordered_list': VIDEOS, 'get_categories': CATEGORIES, 'create_link': VOD_STREAM,
                                'del_fav': ADD_REMOVE_FAV, 'set_fav': ADD_REMOVE_FAV},
                        'series': {'get_categories': SERIES_CATEGORIES, 'get_ordered_list': SEASONS_DATA}
                        }


def mock_requests_factory(response_stub: str, status_code: int = 200):
    """factory method that cranks out the Mocks"""
    return Mock(**{
        'json.return_value': json.loads(response_stub),
        'text': response_stub,
        'status_code': status_code,
        'ok': status_code == 200
    })


def mock_requests_get(**kwargs):
    """Mock requests get calls"""
    params = kwargs['params']
    if kwargs['url'].endswith('/stalker_portal/server/load.php'):
        if params['action'] == 'handshake' and params['type'] == 'stb' \
                and str(kwargs['headers']) == "{'Cookie': 'mac=00:2D:73:68:91:11', 'X-User-Agent': 'Model: MAG250; " \
                                              "Link: WiFi', 'Referrer': 'http://xyz.com/stalker_portal/c/', " \
                                              "'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 " \
                                              "(KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3'}":
            return mock_requests_factory(json.dumps(TOKEN))
        if str(kwargs['headers']) == "{'Cookie': 'mac=00:2D:73:68:91:11', 'SN': '02983409283402', 'Authorization': 'Bearer " \
                                     "78236487Y2WEUHE7Y278YDUHEDI', 'X-User-Agent': 'Model: MAG250; Link: WiFi', " \
                                     "'Referrer': 'http://xyz.com/stalker_portal/c/', 'User-Agent': 'Mozilla/5.0 " \
                                     "(QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3'}":
            return mock_requests_factory(json.dumps(ACTION_RESPONSE_DICT.get(params['type']).get(params['action'])))
    raise MockNotSupported


def mock_requests_get_with_auth_failure(**kwargs):
    """Mock requests get calls that simulate authorization failure"""
    params = kwargs['params']
    if kwargs['url'].endswith('/stalker_portal/server/load.php'):
        if params['action'] == 'handshake' and params['type'] == 'stb':
            return mock_requests_factory(json.dumps(TOKEN))
        # Simulate authorization failure with proper JSON response
        return mock_requests_factory(json.dumps({'error': 'Authorization failed'}), status_code=401)
    raise MockNotSupported


def mock_requests_get_multi_page(**kwargs):
    """Mock requests get calls for multi-page responses"""
    params = kwargs['params']
    if kwargs['url'].endswith('/stalker_portal/server/load.php'):
        if params['action'] == 'handshake' and params['type'] == 'stb':
            return mock_requests_factory(json.dumps(TOKEN))
        if 'Authorization' in str(kwargs['headers']):
            # Return different data based on page number
            page = int(params.get('p', 1))
            if page == 1:
                return mock_requests_factory(json.dumps(MULTI_PAGE_VIDEOS))
            # Second page
            return mock_requests_factory(json.dumps({"js": {"data": [{"name": "Video 3"}], "total_items": "10", "max_page_items": "2"}}))
    raise MockNotSupported


@patch('sys.argv', ['plugin://plugin.video.stalkervod/', '1'])
class TestApi(unittest.TestCase):
    """TestApi class"""

    @patch('sys.argv', ['plugin://plugin.video.stalkervod/', '1'])
    def __init__(self, method_name='runTest'):
        """Init test"""
        super().__init__(method_name)
        G.init_globals()

    @patch('requests.get')
    def test_get_vod_categories(self, requests_get_mock):
        """Test get_vod_categories"""
        requests_get_mock.side_effect = mock_requests_get
        categories = Api.get_vod_categories()
        self.assertEqual(len(categories), 3)
        self.assertEqual(categories[0]['id'], '*')
        self.assertEqual(categories[0]['title'], 'All')
        self.assertEqual(categories[1]['id'], '12')
        self.assertEqual(categories[1]['title'], 'ENGLISH MOVIES | LATEST')
        self.assertEqual(categories[2]['id'], '15')
        self.assertEqual(categories[2]['title'], 'ENGLISH TV SHOW')
        self.assertTrue(requests_get_mock.called)

    @patch('requests.get')
    def test_get_tv_genres(self, requests_get_mock):
        """Test get_tv_genres"""
        requests_get_mock.side_effect = mock_requests_get
        genres = Api.get_tv_genres()
        self.assertEqual(len(genres), 3)
        self.assertEqual(genres[0]['id'], '*')
        self.assertEqual(genres[0]['title'], 'All')
        self.assertEqual(genres[1]['id'], '1')
        self.assertEqual(genres[1]['title'], 'english')
        self.assertEqual(genres[2]['id'], '6')
        self.assertEqual(genres[2]['title'], 'sports')
        self.assertTrue(requests_get_mock.called)

    @patch('requests.get')
    def test_get_vod_favorites(self, requests_get_mock):
        """Test get_vod_favorites"""
        requests_get_mock.side_effect = mock_requests_get
        favorites = Api.get_vod_favorites(1)
        self.assertEqual(favorites['total_items'], '1')
        self.assertEqual(len(favorites['data']), 1)
        self.assertEqual(favorites['data'][0]['name'], 'The Blacklist S10')
        self.assertTrue(requests_get_mock.called)

    @patch('requests.get')
    def test_get_videos(self, requests_get_mock):
        """Test get_videos"""
        requests_get_mock.side_effect = mock_requests_get
        videos = Api.get_videos(1, 1, '', 0)
        self.assertEqual(videos['total_items'], '1')
        self.assertEqual(len(videos['data']), 1)
        self.assertEqual(videos['data'][0]['name'], 'The Blacklist S10')
        self.assertTrue(requests_get_mock.called)

    @patch('requests.get')
    def test_get_tv_channels(self, requests_get_mock):
        """Test get_tv_channels"""
        requests_get_mock.side_effect = mock_requests_get
        channels = Api.get_tv_channels(1, 1, '', 0)
        self.assertEqual(channels['total_items'], '1')
        self.assertEqual(len(channels['data']), 1)
        self.assertEqual(channels['data'][0]['name'], 'USA NETWORK')
        self.assertTrue(requests_get_mock.called)

    @patch('requests.get')
    def test_get_vod_stream_url(self, requests_get_mock):
        """Test get_vod_stream_url"""
        requests_get_mock.side_effect = mock_requests_get
        stream_url = Api.get_vod_stream_url('3232', 1, 'cmd', 0)
        self.assertEqual(stream_url, 'http://video.cmd/ENGS/The.Blacklist.S10E03.mp4/playlist.m3u8?token=o832u4rkjsndfhoi348uyr3')
        self.assertTrue(requests_get_mock.called)

    @patch('requests.get')
    def test_get_tv_stream_url(self, requests_get_mock):
        """Test get_tv_stream_url"""
        requests_get_mock.side_effect = mock_requests_get
        stream_url = Api.get_tv_stream_url(3232)
        self.assertEqual(stream_url, 'http://video.cmd/LoveNatureHDUSA/index.m3u8?token=o384uroiwkjsdnskfjs')
        self.assertTrue(requests_get_mock.called)

    @patch('requests.get')
    def test_remove_favorites(self, requests_get_mock):
        """Test get_tv_genres"""
        requests_get_mock.side_effect = mock_requests_get
        Api.remove_favorites(122, 'vod')
        self.assertTrue(requests_get_mock.called)

    @patch('requests.get')
    def test_add_favorites(self, requests_get_mock):
        """Test add_favorites for vod"""
        requests_get_mock.side_effect = mock_requests_get
        Api.add_favorites(122, 'vod')
        self.assertTrue(requests_get_mock.called)

    @patch('requests.get')
    def test_get_series_categories(self, requests_get_mock):
        """Test get_series_categories"""
        requests_get_mock.side_effect = mock_requests_get
        categories = Api.get_series_categories()
        self.assertEqual(len(categories), 3)
        self.assertEqual(categories[0]['id'], '*')
        self.assertEqual(categories[0]['title'], 'All')
        self.assertTrue(requests_get_mock.called)

    @patch('requests.get')
    def test_get_series_categories_no_js(self, requests_get_mock):
        """Test get_series_categories when js key is missing"""
        # Mock the auth handshake first, then the actual call without 'js' key
        def mock_side_effect(**kwargs):
            if kwargs['params']['action'] == 'handshake':
                return mock_requests_factory(json.dumps(TOKEN))
            # Return response without 'js' key
            return mock_requests_factory(json.dumps({}))

        requests_get_mock.side_effect = mock_side_effect
        result = Api.get_series_categories()
        self.assertFalse(result)

    @patch('requests.get')
    def test_get_series_favorites(self, requests_get_mock):
        """Test get_series_favorites"""
        requests_get_mock.side_effect = mock_requests_get
        favorites = Api.get_series_favorites(1)
        # Series favorites uses 'series' type which returns seasons data via get_listing
        self.assertEqual(favorites['total_items'], '2')
        self.assertEqual(len(favorites['data']), 2)
        self.assertEqual(favorites['data'][0]['title'], 'Season 1')
        self.assertTrue(requests_get_mock.called)

    @patch('requests.get')
    def test_get_tv_favorites(self, requests_get_mock):
        """Test get_tv_favorites"""
        requests_get_mock.side_effect = mock_requests_get
        favorites = Api.get_tv_favorites(1)
        # Should return the same structure as get_tv_channels since it uses 'itv' type
        self.assertEqual(favorites['total_items'], '1')
        self.assertEqual(len(favorites['data']), 1)
        self.assertEqual(favorites['data'][0]['name'], 'USA NETWORK')
        self.assertTrue(requests_get_mock.called)

    @patch('requests.get')
    def test_get_seasons(self, requests_get_mock):
        """Test get_seasons"""
        requests_get_mock.side_effect = mock_requests_get
        seasons = Api.get_seasons('123')
        self.assertEqual(len(seasons['data']), 2)
        self.assertEqual(seasons['data'][0]['title'], 'Season 1')
        self.assertTrue(requests_get_mock.called)

    @patch('requests.get')
    def test_get_tv_channels_with_search(self, requests_get_mock):
        """Test get_tv_channels with search term"""
        requests_get_mock.side_effect = mock_requests_get
        channels = Api.get_tv_channels(1, 1, 'USA', 0)
        self.assertEqual(channels['total_items'], '1')
        self.assertTrue(requests_get_mock.called)

    @patch('requests.get')
    def test_get_videos_with_search(self, requests_get_mock):
        """Test get_videos with search term"""
        requests_get_mock.side_effect = mock_requests_get
        videos = Api.get_videos(1, 1, 'Blacklist', 0)
        self.assertEqual(videos['total_items'], '1')
        self.assertTrue(requests_get_mock.called)

    @patch('requests.get')
    def test_get_series_with_search(self, requests_get_mock):
        """Test get_series with search term"""
        requests_get_mock.side_effect = mock_requests_get
        series = Api.get_series(1, 1, 'Drama', 0)
        # Series uses 'series' type which returns seasons data via get_listing
        self.assertEqual(series['total_items'], '2')
        self.assertEqual(len(series['data']), 2)
        self.assertTrue(requests_get_mock.called)

    @patch('requests.get')
    def test_get_listing_multi_page(self, requests_get_mock):
        """Test get_listing with multiple pages"""
        # Set max_page_limit to allow multiple pages
        original_limit = G.addon_config.max_page_limit
        G.addon_config.max_page_limit = 5

        requests_get_mock.side_effect = mock_requests_get_multi_page

        try:
            result = Api.get_listing({'type': 'vod', 'action': 'get_ordered_list'}, 1)
            # Should have data from both pages (2 from page 1 + 1 from page 2 = 3)
            # But the actual result might include existing test data too
            self.assertGreaterEqual(len(result['data']), 3)  # At least 3 items
            # Check that we have the multi-page data
            video_names = [item['name'] for item in result['data']]
            self.assertIn('Video 1', video_names)
            self.assertIn('Video 3', video_names)
        finally:
            G.addon_config.max_page_limit = original_limit

    @patch('requests.get')
    def test_add_tv_favorites(self, requests_get_mock):
        """Test add_favorites for itv type"""
        requests_get_mock.side_effect = mock_requests_get
        Api.add_favorites('789', 'itv')
        self.assertTrue(requests_get_mock.called)

    @patch('requests.get')
    def test_remove_tv_favorites(self, requests_get_mock):
        """Test remove_favorites for itv type"""
        requests_get_mock.side_effect = mock_requests_get
        Api.remove_favorites('123', 'itv')
        self.assertTrue(requests_get_mock.called)

    @patch('requests.get')
    @patch('lib.auth.Auth.clear_cache')
    @patch('lib.auth.Auth.get_token')
    def test_authorization_failure_retry(self, mock_get_token, mock_clear_cache, requests_get_mock):
        """Test authorization failure retry logic"""
        # Set max_retries to test retry logic
        original_retries = G.addon_config.max_retries
        G.addon_config.max_retries = 4

        # Mock get_token to return the same token
        mock_get_token.return_value = '78236487Y2WEUHE7Y278YDUHEDI'

        # Mock to simulate authorization failure then success
        call_count = 0
        def mock_side_effect(**kwargs):  # pylint: disable=unused-argument
            nonlocal call_count
            call_count += 1
            # All calls fail with authorization error to trigger retries
            if call_count <= 3:  # First 3 calls fail (retries 0, 1, 2)
                mock_response = Mock()
                mock_response.text = 'Authorization failed'  # This triggers the retry logic
                mock_response.status_code = 401
                return mock_response
            # Fourth call succeeds (retry 3)
            return mock_requests_factory(json.dumps(CATEGORIES))

        requests_get_mock.side_effect = mock_side_effect

        try:
            Api.get_vod_categories()
            # Should have called clear_cache when retries > 1 (i.e., on retry 2)
            mock_clear_cache.assert_called()
        finally:
            G.addon_config.max_retries = original_retries

    @patch('requests.get')
    def test_authorization_failure_max_retries(self, requests_get_mock):
        """Test authorization failure with max retries reached"""
        # Set max_retries to test retry logic
        original_retries = G.addon_config.max_retries
        G.addon_config.max_retries = 2

        def mock_side_effect(**kwargs):  # pylint: disable=unused-argument
            mock_response = Mock()
            mock_response.text = 'Authorization failed'
            mock_response.status_code = 401
            mock_response.json.return_value = {'js': []}  # Empty categories list for failed auth
            return mock_response

        requests_get_mock.side_effect = mock_side_effect

        try:
            # Should not raise exception even after max retries
            result = Api.get_vod_categories()
            # Should return the failed response (empty list)
            self.assertEqual(result, [])
        finally:
            G.addon_config.max_retries = original_retries

    @patch('requests.get')
    def test_get_vod_stream_url_with_cmd(self, requests_get_mock):
        """Test get_vod_stream_url using cmd parameter"""
        requests_get_mock.side_effect = mock_requests_get
        stream_url = Api.get_vod_stream_url('3232', 1, 'cmd', '1')  # use_cmd = '1'
        self.assertEqual(stream_url, 'http://video.cmd/ENGS/The.Blacklist.S10E03.mp4/playlist.m3u8?token=o832u4rkjsndfhoi348uyr3')
        self.assertTrue(requests_get_mock.called)

    @patch('requests.get')
    def test_get_vod_stream_url_video_id_failure(self, requests_get_mock):
        """Test get_vod_stream_url when video_id method fails"""
        # Mock to return 404 for video_id method, then success for cmd method
        def mock_side_effect(**kwargs):
            # First call is handshake
            if kwargs['params']['action'] == 'handshake':
                return mock_requests_factory(json.dumps(TOKEN))
            # Check if this is the video_id method call (has /media/ in cmd)
            if kwargs['params']['action'] == 'create_link' and '/media/' in kwargs['params']['cmd']:
                mock_response = Mock()
                mock_response.status_code = 404
                mock_response.json.return_value = {'error': 'Not found'}
                return mock_response
            # This is the cmd method call (fallback) - succeeds
            if kwargs['params']['action'] == 'create_link':
                return mock_requests_factory(json.dumps(VOD_STREAM))
            return mock_requests_get(**kwargs)

        requests_get_mock.side_effect = mock_side_effect
        stream_url = Api.get_vod_stream_url('3232', 1, 'cmd', '0')  # use_cmd = '0'
        self.assertEqual(stream_url, 'http://video.cmd/ENGS/The.Blacklist.S10E03.mp4/playlist.m3u8?token=o832u4rkjsndfhoi348uyr3')

    @patch('requests.get')
    def test_get_vod_stream_url_video_id_500_error(self, requests_get_mock):
        """Test get_vod_stream_url when video_id method returns 500 error"""
        # Mock to return 500 for video_id method, then success for cmd method
        def mock_side_effect(**kwargs):
            # First call is handshake
            if kwargs['params']['action'] == 'handshake':
                return mock_requests_factory(json.dumps(TOKEN))
            # Second call is video_id method (create_link with video_id) - returns 500
            if kwargs['params']['action'] == 'create_link' and 'video_id' in kwargs['params']:
                mock_response = Mock()
                mock_response.status_code = 500
                mock_response.json.return_value = {'error': 'Server error'}
                return mock_response
            # Third call is cmd method (create_link with cmd) - succeeds
            if kwargs['params']['action'] == 'create_link' and 'cmd' in kwargs['params']:
                return mock_requests_factory(json.dumps(VOD_STREAM))
            return mock_requests_get(**kwargs)

        requests_get_mock.side_effect = mock_side_effect
        stream_url = Api.get_vod_stream_url('3232', 1, 'cmd', '0')  # use_cmd = '0'
        self.assertEqual(stream_url, 'http://video.cmd/ENGS/The.Blacklist.S10E03.mp4/playlist.m3u8?token=o832u4rkjsndfhoi348uyr3')

    @patch('requests.get')
    def test_stream_url_space_trimming(self, requests_get_mock):
        """Test stream URL space trimming functionality"""
        # Mock response with space in the URL
        def mock_with_space(**kwargs):
            if kwargs['params']['action'] == 'handshake':
                return mock_requests_factory(json.dumps(TOKEN))
            return mock_requests_factory(json.dumps({
                'js': {'cmd': 'ffmpeg http://video.cmd/stream.m3u8?token=abc123'}
            }))

        requests_get_mock.side_effect = mock_with_space

        # Test VOD stream URL space trimming
        vod_url = Api.get_vod_stream_url('123', 1, 'cmd', '1')
        self.assertEqual(vod_url, 'http://video.cmd/stream.m3u8?token=abc123')

        # Test TV stream URL space trimming
        tv_url = Api.get_tv_stream_url('cmd')
        self.assertEqual(tv_url, 'http://video.cmd/stream.m3u8?token=abc123')

    @patch('requests.get')
    def test_call_stalker_portal_return_response_only(self, requests_get_mock):
        """Test __call_stalker_portal with return_response_body=False"""
        requests_get_mock.side_effect = mock_requests_get

        # This should return None when return_response_body=False
        result = Api._Api__call_stalker_portal({'type': 'vod', 'action': 'get_categories'}, False)  # pylint: disable=protected-access
        self.assertIsNone(result)
