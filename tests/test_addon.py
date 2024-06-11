"""
Compatible with Kodi 19.x "Matrix" and above
"""
from __future__ import absolute_import, division, unicode_literals
import unittest
from unittest.mock import patch
from lib.addon import StalkerAddon, run
from lib.globals import G


class TestStalkerAddon(unittest.TestCase):
    """TestStalkerAddon class"""
    stalker_addon = StalkerAddon()

    @patch('sys.argv', ['plugin://plugin.video.stalkervod/', '1'])
    def __init__(self, method_name='runTest'):
        """Init test"""
        super().__init__(method_name)
        G.init_globals()

    @patch('lib.addon.xbmc')
    @patch('lib.addon.Api')
    @patch('sys.argv', ['plugin://plugin.video.stalkervod/', '1'])
    def test_run(self, mock_api, mock_xbmc):
        """Test run"""
        run(['plugin://plugin.video.stalkervod/', '1', '?action=add_fav&video_id=1234'])
        mock_api.add_favorites.assert_called_with('1234')
        mock_xbmc.executebuiltin.assert_called_with('Container.Refresh')

    @patch('lib.addon.xbmc')
    @patch('lib.addon.Api')
    def test_toggle_favorites_add(self, mock_api, mock_xbmc):
        """Test toggle_favorites"""
        params = 'action=add_fav&video_id=1234'
        self.stalker_addon.router(params)
        mock_api.add_favorites.assert_called_with('1234')
        mock_xbmc.executebuiltin.assert_called_with('Container.Refresh')

    @patch('lib.addon.xbmc')
    @patch('lib.addon.Api')
    def test_toggle_favorites_remove(self, mock_api, mock_xbmc):
        """Test toggle_favorites"""
        params = 'action=remove_fav&video_id=1234'
        self.stalker_addon.router(params)
        mock_api.remove_favorites.assert_called_with('1234')
        mock_xbmc.executebuiltin.assert_called_with('Container.Refresh')

    @patch('lib.addon.xbmcplugin')
    @patch('lib.addon.xbmcgui')
    @patch('lib.addon.Api')
    def test_play_video(self, mock_api, mock_xbmcgui, mock_xbmcplugin):
        """Test play_video"""
        mock_api.get_vod_stream_url.return_value = 'stream_url'
        params = 'action=play&video_id=1234&series=0'
        self.stalker_addon.router(params)
        mock_api.get_vod_stream_url.assert_called_with('1234', '0')
        mock_xbmcgui.ListItem.assert_called_with(path='stream_url')
        mock_xbmcplugin.setResolvedUrl.assert_called()

    @patch('lib.addon.xbmcplugin')
    @patch('lib.addon.xbmcgui')
    @patch('lib.addon.Api')
    def test_play_tv(self, mock_api, mock_xbmcgui, mock_xbmcplugin):
        """Test play_tv"""
        mock_api.get_tv_stream_url.return_value = 'tv_stream_url'
        params = 'action=tv_play&cmd=cmd'
        self.stalker_addon.router(params)
        mock_api.get_tv_stream_url.assert_called_with('cmd')
        mock_xbmcgui.ListItem.assert_called_with(path='tv_stream_url')
        mock_xbmcplugin.setResolvedUrl.assert_called()

    @patch('lib.addon.xbmc')
    @patch('lib.addon.xbmcplugin')
    @patch('lib.addon.xbmcgui')
    @patch('lib.addon.Api')
    def test_list_videos(self, mock_api, mock_xbmcgui, mock_xbmcplugin, mock_xbmc):
        """Test list_videos"""
        mock_api.get_videos.return_value = {'total_items': 10, 'max_page_items': 2,
                                            'data': [
                                                {
                                                    'id': 123,
                                                    'name': 'Video1',
                                                    'fav': 0,
                                                    'series': [],
                                                    'time': 2,
                                                    'director': 'director',
                                                    'description': 'description',
                                                    'actors': 'actors',
                                                    'last_played': 'last_played',
                                                    'added': 'added',
                                                    'year': '2010'
                                                },
                                                {
                                                    'id': 456,
                                                    'name': 'Video2',
                                                    'fav': 1,
                                                    'series': [],
                                                    'time': '2',
                                                    'director': 'director',
                                                    'description': 'description',
                                                    'actors': 'actors',
                                                    'last_played': 'last_played',
                                                    'added': 'added',
                                                    'year': 'added'
                                                },
                                                {
                                                    'id': 2223,
                                                    'name': 'Video3',
                                                    'fav': 1,
                                                    'series': [1, 2, 3],
                                                    'time': '0',
                                                    'director': 'director',
                                                    'description': 'description',
                                                    'actors': 'actors',
                                                    'last_played': 'last_played',
                                                    'added': 'added',
                                                    'year': 'added',
                                                    'screenshot_uri': 'dddd/dd'
                                                },
                                                {
                                                    'id': 2223,
                                                    'name': 'Video3',
                                                    'fav': 1,
                                                    'series': [],
                                                    'time': 0,
                                                    'director': 'director',
                                                    'description': 'description',
                                                    'actors': 'actors',
                                                    'last_played': 'last_played',
                                                    'added': 'added',
                                                    'year': 2010,
                                                    'screenshot_uri': 'http://test',
                                                    'country': 'USA'
                                                }]}
        params = 'action=listing&category=movies&category_id=1&page=0&update_listing=False'
        self.stalker_addon.router(params)
        mock_xbmcplugin.setPluginCategory.assert_called_with(1, 'movies')
        mock_xbmcplugin.setContent.assert_called()
        mock_api.get_videos.assert_called_with('1', '0', '', 0)
        self.assertEqual(mock_xbmcgui.ListItem.call_count, 6)
        self.assertEqual(mock_xbmc.Actor.call_count, 4)

    @patch('lib.addon.xbmcplugin')
    @patch('lib.addon.xbmcgui')
    @patch('lib.addon.Api')
    def test_list_channels(self, mock_api, mock_xbmcgui, mock_xbmcplugin):
        """Test list_channels"""
        mock_api.get_tv_channels.return_value = {'total_items': 10, 'max_page_items': 2,
                                                 'data': [
                                                     {
                                                         'id': 123,
                                                         'name': 'TV Channel',
                                                         'cmd': 'ffrt http://localhost/ch/353'
                                                     }]}
        params = 'action=tv_listing&category=english&category_id=1&page=0&update_listing=False'
        self.stalker_addon.router(params)
        mock_xbmcplugin.setPluginCategory.assert_called_with(1, 'TV CHANNELS - english')
        mock_xbmcplugin.setContent.assert_called()
        mock_api.get_tv_channels.assert_called_with('1', '0')
        self.assertEqual(mock_xbmcgui.ListItem.call_count, 3)

    @patch('lib.addon.xbmcplugin')
    @patch('lib.addon.xbmcgui')
    @patch('lib.addon.Api')
    def test_list_tv_genres(self, mock_api, mock_xbmcgui, mock_xbmcplugin):
        """Test list_tv_genres"""
        mock_api.get_tv_genres.return_value = [
            {
                'id': '*',
                'title': 'All',
            },
            {
                'id': '1',
                'title': 'english',
            }]
        params = 'action=tv'
        self.stalker_addon.router(params)
        mock_xbmcplugin.setPluginCategory.assert_called_with(1, 'TV CHANNELS')
        mock_xbmcplugin.setContent.assert_called()
        mock_xbmcplugin.addDirectoryItem.assert_called()
        mock_xbmcplugin.endOfDirectory.assert_called()
        mock_api.get_tv_genres.assert_called()
        self.assertEqual(mock_xbmcgui.ListItem.call_count, 2)

    @patch('lib.addon.xbmcplugin')
    @patch('lib.addon.xbmcgui')
    @patch('lib.addon.Api')
    def test_list_vod_categories(self, mock_api, mock_xbmcgui, mock_xbmcplugin):
        """Test list_vod_categories"""
        mock_api.get_vod_categories.return_value = [
            {
                'id': '*',
                'title': 'All',
            },
            {
                'id': '1',
                'title': 'ENGLISH MOVIES | LATEST',
            }]
        params = ''
        self.stalker_addon.router(params)
        mock_xbmcplugin.setPluginCategory.assert_called_with(1, 'VOD')
        mock_xbmcplugin.setContent.assert_called()
        mock_xbmcplugin.addDirectoryItem.assert_called()
        mock_xbmcplugin.endOfDirectory.assert_called()
        mock_api.get_vod_categories.assert_called()
        self.assertEqual(mock_xbmcgui.ListItem.call_count, 4)

    @patch('lib.addon.xbmc')
    @patch('lib.addon.xbmcplugin')
    @patch('lib.addon.xbmcgui')
    @patch('lib.addon.Api')
    def test_list_vod_favorites(self, mock_api, mock_xbmcgui, mock_xbmcplugin, mock_xbmc):
        """Test list_vod_favorites"""
        mock_api.get_vod_favorites.return_value = {'total_items': 0, 'max_page_items': 2, 'data': []}
        params = 'action=favorites&page=0&update_listing=False'
        self.stalker_addon.router(params)
        mock_xbmcplugin.setPluginCategory.assert_called_with(1, 'FAVORITES')
        mock_xbmcplugin.setContent.assert_called()
        mock_api.get_vod_favorites.assert_called_with('0')
        self.assertEqual(mock_xbmcgui.ListItem.call_count, 0)
        self.assertEqual(mock_xbmc.Actor.call_count, 0)

    @patch('lib.addon.xbmc')
    @patch('lib.addon.xbmcplugin')
    @patch('lib.addon.xbmcgui')
    def test_list_episodes(self, mock_xbmcgui, mock_xbmcplugin, mock_xbmc):
        """Test list_episodes"""
        params = 'action=sub_folder&name=series S01&start=1&end=20&poster_url=None&video_id=1234'
        self.stalker_addon.router(params)
        mock_xbmcplugin.setPluginCategory.assert_called_with(1, 'series S01')
        mock_xbmcplugin.setContent.assert_called()
        self.assertEqual(mock_xbmcgui.ListItem.call_count, 20)
        self.assertEqual(mock_xbmc.Actor.call_count, 0)
