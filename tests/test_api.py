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

ACTION_RESPONSE_DICT = {'stb': {'get_profile': PROFILE},
                        'watchdog': {'get_events': EVENTS},
                        'itv': {'get_genres': GENRES, 'get_ordered_list': CHANNELS, 'create_link': ITV_STREAM},
                        'vod': {'get_ordered_list': VIDEOS, 'get_categories': CATEGORIES, 'create_link': VOD_STREAM,
                                'del_fav': ADD_REMOVE_FAV, 'set_fav': ADD_REMOVE_FAV}
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
        """Test get_tv_genres"""
        requests_get_mock.side_effect = mock_requests_get
        Api.add_favorites(122, 'vod')
        self.assertTrue(requests_get_mock.called)
