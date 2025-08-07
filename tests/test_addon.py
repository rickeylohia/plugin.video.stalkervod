"""Test Module for addon.py"""
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

    def test_invalid_param(self):
        """Test toggle_favorites"""
        params = 'action=invalid_action'
        with self.assertRaises(ValueError):
            self.stalker_addon.router(params)

    @patch('lib.addon.xbmc')
    @patch('lib.addon.Api')
    @patch('sys.argv', ['plugin://plugin.video.stalkervod/', '1'])
    def test_run(self, mock_api, mock_xbmc):
        """Test run"""
        run(['plugin://plugin.video.stalkervod/', '1', '?action=add_fav&video_id=1234&_type=vod'])
        mock_api.add_favorites.assert_called_with('1234', 'vod')
        mock_xbmc.executebuiltin.assert_called_with('Container.Refresh')

    @patch('lib.addon.xbmc')
    @patch('lib.addon.Api')
    def test_toggle_favorites_add(self, mock_api, mock_xbmc):
        """Test toggle_favorites"""
        params = 'action=add_fav&video_id=1234&_type=vod'
        self.stalker_addon.router(params)
        mock_api.add_favorites.assert_called_with('1234', 'vod')
        mock_xbmc.executebuiltin.assert_called_with('Container.Refresh')

    @patch('lib.addon.xbmc')
    @patch('lib.addon.Api')
    def test_toggle_favorites_remove(self, mock_api, mock_xbmc):
        """Test toggle_favorites"""
        params = 'action=remove_fav&video_id=1234&_type=vod'
        self.stalker_addon.router(params)
        mock_api.remove_favorites.assert_called_with('1234', 'vod')
        mock_xbmc.executebuiltin.assert_called_with('Container.Refresh')

    @patch('lib.addon.xbmcplugin')
    @patch('lib.addon.xbmcgui')
    @patch('lib.addon.Api')
    def test_play_video(self, mock_api, mock_xbmcgui, mock_xbmcplugin):
        """Test play_video"""
        mock_api.get_vod_stream_url.return_value = 'stream_url'
        params = 'action=play&video_id=1234&series=0'
        self.stalker_addon.router(params)
        mock_api.get_vod_stream_url.assert_called_with('1234', '0', '', '0')
        mock_xbmcgui.ListItem.assert_called_with(path='stream_url')
        mock_xbmcplugin.setResolvedUrl.assert_called()

    @patch('lib.addon.xbmcplugin')
    @patch('lib.addon.xbmcgui')
    @patch('lib.addon.Api')
    def test_play_tv(self, mock_api, mock_xbmcgui, mock_xbmcplugin):
        """Test play_tv"""
        mock_api.get_tv_stream_url.return_value = 'tv_stream_url'
        params = 'action=tv_play&cmd=cmd&use_http_tmp_link=1'
        self.stalker_addon.router(params)
        mock_api.get_tv_stream_url.assert_called_with({'action': 'tv_play', 'cmd': 'cmd', 'use_http_tmp_link': '1'})
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
        params = 'action=vod_listing&category=movies&category_id=1&page=0&update_listing=False'
        self.stalker_addon.router(params)
        mock_xbmcplugin.setPluginCategory.assert_called_with(1, 'VOD - movies')
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
                                                         'cmd': 'ffrt http://localhost/ch/353',
                                                         'use_http_tmp_link': 0
                                                     },
                                                     {
                                                         'id': 2222,
                                                         'name': 'TV Channel',
                                                         'cmd': 'ffrt http://localhost/ch/353',
                                                         'fav': 1,
                                                         'logo': 'logo'
                                                     }
                                                 ]}
        params = 'action=tv_listing&category=english&category_id=1&page=0&update_listing=False&fav=0'
        self.stalker_addon.router(params)
        mock_xbmcplugin.setPluginCategory.assert_called_with(1, 'TV - english')
        mock_xbmcplugin.setContent.assert_called()
        mock_api.get_tv_channels.assert_called_with('1', '0', '', '0')
        self.assertEqual(mock_xbmcgui.ListItem.call_count, 4)

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
        self.assertEqual(mock_xbmcgui.ListItem.call_count, 4)

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
        params = 'action=vod'
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
        params = 'action=vod_favorites&page=0&update_listing=False'
        self.stalker_addon.router(params)
        mock_xbmcplugin.setPluginCategory.assert_called_with(1, 'VOD FAVORITES')
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

    @patch('lib.addon.xbmcgui')
    @patch('lib.addon.Api')
    def test_list_main_menu(self, mock_api, mock_xbmcgui):
        """Test list_episodes"""
        mock_api.get_series_categories.return_value = []
        params = ''
        self.stalker_addon.router(params)
        self.assertEqual(mock_xbmcgui.ListItem.call_count, 2)

    @patch('lib.addon.xbmcgui')
    @patch('lib.addon.Api')
    def test_list_main_menu_2(self, mock_api, mock_xbmcgui):
        """Test list_episodes"""
        mock_api.get_series_categories.return_value = 'false'
        params = ''
        self.stalker_addon.router(params)
        self.assertEqual(mock_xbmcgui.ListItem.call_count, 2)

    @patch('lib.addon.xbmcgui')
    @patch('lib.addon.Api')
    def test_list_main_menu_with_series(self, mock_api, mock_xbmcgui):
        """Test list_episodes"""
        mock_api.get_series_categories.return_value = [
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
        self.assertEqual(mock_xbmcgui.ListItem.call_count, 3)

    @patch('lib.addon.xbmcplugin')
    @patch('lib.addon.xbmcgui')
    @patch('lib.addon.Api')
    def test_list_series_categories(self, mock_api, mock_xbmcgui, mock_xbmcplugin):
        """Test list_vod_categories"""
        mock_api.get_series_categories.return_value = [
            {
                'id': '*',
                'title': 'All',
            },
            {
                'id': '1',
                'title': 'ABCDE',
            }]
        params = 'action=series'
        self.stalker_addon.router(params)
        mock_xbmcplugin.setPluginCategory.assert_called_with(1, 'SERIES')
        mock_xbmcplugin.setContent.assert_called()
        mock_xbmcplugin.addDirectoryItem.assert_called()
        mock_xbmcplugin.endOfDirectory.assert_called()
        mock_api.get_series_categories.assert_called()
        self.assertEqual(mock_xbmcgui.ListItem.call_count, 4)  # SERIES FAVORITES + SEARCH + 2 categories

    @patch('lib.addon.xbmc')
    @patch('lib.addon.xbmcplugin')
    @patch('lib.addon.xbmcgui')
    @patch('lib.addon.Api')
    def test_list_series_favorites(self, mock_api, mock_xbmcgui, mock_xbmcplugin, mock_xbmc):
        """Test list_vod_favorites"""
        mock_api.get_series_favorites.return_value = {'total_items': 0, 'max_page_items': 2, 'data': []}
        params = 'action=series_favorites&page=0&update_listing=False'
        self.stalker_addon.router(params)
        mock_xbmcplugin.setPluginCategory.assert_called_with(1, 'SERIES FAVORITES')
        mock_xbmcplugin.setContent.assert_called()
        mock_api.get_series_favorites.assert_called_with('0')
        self.assertEqual(mock_xbmcgui.ListItem.call_count, 0)
        self.assertEqual(mock_xbmc.Actor.call_count, 0)

    @patch('lib.addon.xbmc')
    @patch('lib.addon.xbmcplugin')
    @patch('lib.addon.xbmcgui')
    @patch('lib.addon.Api')
    def test_list_tv_favorites(self, mock_api, mock_xbmcgui, mock_xbmcplugin, mock_xbmc):
        """Test list_vod_favorites"""
        mock_api.get_tv_favorites.return_value = {'total_items': 0, 'max_page_items': 2, 'data': []}
        params = 'action=tv_favorites&page=0&update_listing=False'
        self.stalker_addon.router(params)
        mock_xbmcplugin.setPluginCategory.assert_called_with(1, 'TV FAVORITES')
        mock_xbmcplugin.setContent.assert_called()
        mock_api.get_tv_favorites.assert_called_with('0')
        self.assertEqual(mock_xbmcgui.ListItem.call_count, 0)
        self.assertEqual(mock_xbmc.Actor.call_count, 0)

    @patch('lib.addon.xbmc')
    @patch('lib.addon.xbmcplugin')
    @patch('lib.addon.xbmcgui')
    @patch('lib.addon.Api')
    def test_list_series(self, mock_api, mock_xbmcgui, mock_xbmcplugin, mock_xbmc):
        """Test list_videos"""
        mock_api.get_series.return_value = {'total_items': 10, 'max_page_items': 2,
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
        params = 'action=series_listing&category=hindi series&category_id=1&page=0&update_listing=False'
        self.stalker_addon.router(params)
        mock_xbmcplugin.setPluginCategory.assert_called_with(1, 'SERIES - hindi series')
        mock_xbmcplugin.setContent.assert_called()
        mock_api.get_series.assert_called_with('1', '0', '', 0)
        self.assertEqual(mock_xbmcgui.ListItem.call_count, 6)
        self.assertEqual(mock_xbmc.Actor.call_count, 4)

    @patch('lib.addon.xbmc')
    @patch('lib.addon.xbmcplugin')
    @patch('lib.addon.xbmcgui')
    @patch('lib.addon.Api')
    def test_list_season(self, mock_api, mock_xbmcgui, mock_xbmcplugin, mock_xbmc):
        """Test list_vod_favorites"""
        mock_api.get_seasons.return_value = {'total_items': 0, 'max_page_items': 2,
                                             'data': [
                                                 {
                                                     "id": "7861:6",
                                                     "name": "Season 6",
                                                     "series": [
                                                         1,
                                                         2,
                                                         3,
                                                         4,
                                                         5,
                                                         6,
                                                         7,
                                                         8,
                                                         9,
                                                         10
                                                     ],
                                                     'actors': 'actors',
                                                 }]}
        params = 'action=season_listing&name=Rookie&video_id=7861&poster_url=None'
        self.stalker_addon.router(params)
        mock_xbmcplugin.setPluginCategory.assert_called_with(1, 'Rookie')
        mock_xbmcplugin.setContent.assert_called()
        mock_api.get_seasons.assert_called_with('7861')
        self.assertEqual(mock_xbmcgui.ListItem.call_count, 1)
        self.assertEqual(mock_xbmc.Actor.call_count, 1)

    @patch('lib.addon.xbmc')
    @patch('lib.addon.ask_for_input')
    def test_search_vod(self, mock_ask_for_input, mock_xbmc):
        """Test list_vod_favorites"""
        mock_ask_for_input.return_value = 'search_term'
        params = 'action=vod_search&category=English Movies'
        self.stalker_addon.router(params)
        mock_xbmc.executebuiltin.assert_called_with('Container.Update(plugin://plugin.video.stalkervod/?action=vod_listing&category=English+Movies&update_listing=False&search_term=search_term&page=1)')

    @patch('lib.addon.xbmc')
    @patch('lib.addon.ask_for_input')
    def test_search_tv(self, mock_ask_for_input, mock_xbmc):
        """Test list_vod_favorites"""
        mock_ask_for_input.return_value = 'search_term'
        params = 'action=tv_search&category=English Movies'
        self.stalker_addon.router(params)
        mock_xbmc.executebuiltin.assert_called_with('Container.Update(plugin://plugin.video.stalkervod/?action=tv_listing&category=English+Movies&update_listing=False&search_term=search_term&page=1)')

    @patch('lib.addon.xbmc')
    @patch('lib.addon.ask_for_input')
    def test_search_series(self, mock_ask_for_input, mock_xbmc):
        """Test list_vod_favorites"""
        mock_ask_for_input.return_value = 'search_term'
        params = 'action=series_search&category=English Movies'
        self.stalker_addon.router(params)
        mock_xbmc.executebuiltin.assert_called_with('Container.Update(plugin://plugin.video.stalkervod/?action=series_listing&category=English+Movies&update_listing=False&search_term=search_term&page=1)')

    @patch('lib.addon.xbmcplugin')
    @patch('lib.addon.xbmcgui')
    @patch('lib.addon.Api')
    def test_play_video_with_episode(self, mock_api, mock_xbmcgui, mock_xbmcplugin):
        """Test play_video with episode information (covers lines 42-45)"""
        mock_api.get_vod_stream_url.return_value = 'stream_url'
        mock_list_item = mock_xbmcgui.ListItem.return_value
        mock_video_info = mock_list_item.getVideoInfoTag.return_value

        # Test with episode number > 0 to trigger episode-specific code
        params = 'action=play&video_id=1234&series=5&season_no=2&title=Test Show'
        self.stalker_addon.router(params)

        # Verify episode-specific methods are called (lines 42-45)
        mock_video_info.setEpisode.assert_called_with(5)
        mock_video_info.setSeason.assert_called_with(2)
        mock_video_info.setMediaType.assert_called_with('episode')
        mock_video_info.setTvShowTitle.assert_called_with('Test Show')
        mock_xbmcplugin.setResolvedUrl.assert_called()

    @patch('lib.addon.xbmcplugin')
    @patch('lib.addon.xbmcgui')
    def test_list_episodes_movie_type(self, mock_xbmcgui, mock_xbmcplugin):
        """Test list_episodes when name doesn't match season pattern (covers line 431)"""
        mock_list_item = mock_xbmcgui.ListItem.return_value
        mock_video_info = mock_list_item.getVideoInfoTag.return_value

        # Test with name that doesn't end with season pattern (e.g., "S01")
        params = 'action=sub_folder&name=Movie Title&start=1&end=1&poster_url=None&video_id=1234'
        self.stalker_addon.router(params)

        # Verify movie media type is set (line 431)
        mock_video_info.setMediaType.assert_called_with('movie')
        mock_xbmcplugin.setPluginCategory.assert_called_with(1, 'Movie Title')
        mock_xbmcplugin.setContent.assert_called()

    @patch('lib.addon.xbmcplugin')
    @patch('lib.addon.xbmcgui')
    @patch('lib.addon.Api')
    @patch('lib.addon.ask_for_input')
    def test_search_vod_non_context(self, mock_ask_for_input, mock_api, mock_xbmcgui, mock_xbmcplugin):  # pylint: disable=unused-argument
        """Test search_vod with isContextMenuSearch=false (covers line 451)"""
        mock_ask_for_input.return_value = 'search_term'
        mock_api.get_videos.return_value = {'total_items': 0, 'max_page_items': 2, 'data': []}

        # Test with isContextMenuSearch=false to trigger __list_vod call
        params = 'action=vod_search&category=English Movies&category_id=1&page=1&isContextMenuSearch=false'
        self.stalker_addon.router(params)

        # Verify that __list_vod is called instead of executebuiltin (line 451)
        mock_api.get_videos.assert_called()
        mock_xbmcplugin.setPluginCategory.assert_called()

    @patch('lib.addon.xbmcplugin')
    @patch('lib.addon.xbmcgui')
    @patch('lib.addon.Api')
    @patch('lib.addon.ask_for_input')
    def test_search_tv_non_context(self, mock_ask_for_input, mock_api, mock_xbmcgui, mock_xbmcplugin):  # pylint: disable=unused-argument
        """Test search_tv with isContextMenuSearch=false (covers line 474)"""
        mock_ask_for_input.return_value = 'search_term'
        mock_api.get_tv_channels.return_value = {'total_items': 0, 'max_page_items': 2, 'data': []}

        # Test with isContextMenuSearch=false to trigger __list_channels call
        params = 'action=tv_search&category=English Channels&category_id=1&page=1&isContextMenuSearch=false'
        self.stalker_addon.router(params)

        # Verify that __list_channels is called instead of executebuiltin (line 474)
        mock_api.get_tv_channels.assert_called()
        mock_xbmcplugin.setPluginCategory.assert_called()

    @patch('lib.addon.Api.get_vod_categories')
    @patch('lib.addon.ask_for_category_selection')
    @patch('lib.addon.ask_for_input')
    @patch('lib.addon.xbmc')
    def test_search_vod_with_category_selection(self, mock_xbmc, mock_ask_for_input, mock_ask_for_category_selection, mock_get_vod_categories):
        """Test search_vod with category selection popup"""
        # Mock category selection
        mock_ask_for_category_selection.return_value = {'id': '1', 'title': 'Movies'}
        mock_ask_for_input.return_value = 'search_term'
        mock_get_vod_categories.return_value = [
            {'id': '*', 'title': 'All'},
            {'id': '1', 'title': 'Movies'}
        ]

        # Test with missing category to trigger category selection
        params = 'action=vod_search'
        self.stalker_addon.router(params)

        # Verify category selection was called
        mock_ask_for_category_selection.assert_called_once_with(
            [{'id': '*', 'title': 'All'}, {'id': '1', 'title': 'Movies'}], 'VOD Category'
        )
        # Verify search input was called with selected category
        mock_ask_for_input.assert_called_once_with('Movies')
        # Verify executebuiltin was called with updated params
        mock_xbmc.executebuiltin.assert_called()

    @patch('lib.addon.xbmcplugin')
    @patch('lib.addon.Api.get_vod_categories')
    @patch('lib.addon.ask_for_category_selection')
    def test_search_vod_category_selection_cancelled(self, mock_ask_for_category_selection, mock_get_vod_categories, mock_xbmcplugin):
        """Test search_vod when category selection is cancelled"""
        # Mock category selection returning None (cancelled)
        mock_ask_for_category_selection.return_value = None
        mock_get_vod_categories.return_value = [
            {'id': '*', 'title': 'All'},
            {'id': '1', 'title': 'Movies'}
        ]

        # Test with missing category to trigger category selection
        params = 'action=vod_search'
        self.stalker_addon.router(params)

        # Verify category selection was called but search was cancelled
        mock_ask_for_category_selection.assert_called_once()
        # Verify endOfDirectory was called to prevent hanging
        mock_xbmcplugin.endOfDirectory.assert_called_once()

    @patch('lib.addon.Api.get_tv_genres')
    @patch('lib.addon.ask_for_category_selection')
    @patch('lib.addon.ask_for_input')
    @patch('lib.addon.xbmc')
    def test_search_tv_with_category_selection(self, mock_xbmc, mock_ask_for_input, mock_ask_for_category_selection, mock_get_tv_genres):
        """Test search_tv with category selection popup"""
        # Mock category selection
        mock_ask_for_category_selection.return_value = {'id': '1', 'title': 'English'}
        mock_ask_for_input.return_value = 'search_term'
        mock_get_tv_genres.return_value = [
            {'id': '*', 'title': 'All'},
            {'id': '1', 'title': 'English'}
        ]

        # Test with missing category to trigger category selection
        params = 'action=tv_search'
        self.stalker_addon.router(params)

        # Verify category selection was called
        mock_ask_for_category_selection.assert_called_once_with(
            [{'id': '*', 'title': 'All'}, {'id': '1', 'title': 'English'}], 'TV Genre'
        )
        # Verify search input was called with selected category
        mock_ask_for_input.assert_called_once_with('English')
        # Verify executebuiltin was called
        mock_xbmc.executebuiltin.assert_called()

    @patch('lib.addon.xbmcplugin')
    @patch('lib.addon.Api.get_tv_genres')
    @patch('lib.addon.ask_for_category_selection')
    def test_search_tv_category_selection_cancelled(self, mock_ask_for_category_selection, mock_get_tv_genres, mock_xbmcplugin):
        """Test search_tv when category selection is cancelled"""
        # Mock category selection returning None (cancelled)
        mock_ask_for_category_selection.return_value = None
        mock_get_tv_genres.return_value = [
            {'id': '*', 'title': 'All'},
            {'id': '1', 'title': 'English'}
        ]

        # Test with missing category to trigger category selection
        params = 'action=tv_search'
        self.stalker_addon.router(params)

        # Verify category selection was called but search was cancelled
        mock_ask_for_category_selection.assert_called_once()
        # Verify endOfDirectory was called to prevent hanging
        mock_xbmcplugin.endOfDirectory.assert_called_once()

    @patch('lib.addon.Api.get_series_categories')
    @patch('lib.addon.ask_for_category_selection')
    @patch('lib.addon.ask_for_input')
    @patch('lib.addon.xbmc')
    def test_search_series_with_category_selection(self, mock_xbmc, mock_ask_for_input, mock_ask_for_category_selection, mock_get_series_categories):
        """Test search_series with category selection popup"""
        # Mock category selection
        mock_ask_for_category_selection.return_value = {'id': '1', 'title': 'Drama'}
        mock_ask_for_input.return_value = 'search_term'
        mock_get_series_categories.return_value = [
            {'id': '*', 'title': 'All'},
            {'id': '1', 'title': 'Drama'}
        ]

        # Test with the missing category to trigger category selection
        params = 'action=series_search'
        self.stalker_addon.router(params)

        # Verify category selection was called
        mock_ask_for_category_selection.assert_called_once_with(
            [{'id': '*', 'title': 'All'}, {'id': '1', 'title': 'Drama'}], 'Series Category'
        )
        # Verify search input was called with the selected category
        mock_ask_for_input.assert_called_once_with('Drama')
        # Verify executebuiltin was called
        mock_xbmc.executebuiltin.assert_called()

    @patch('lib.addon.xbmcplugin')
    @patch('lib.addon.Api.get_series_categories')
    @patch('lib.addon.ask_for_category_selection')
    def test_search_series_category_selection_cancelled(self, mock_ask_for_category_selection, mock_get_series_categories, mock_xbmcplugin):
        """Test search_series when category selection is cancelled"""
        # Mock category selection returning None (cancelled)
        mock_ask_for_category_selection.return_value = None
        mock_get_series_categories.return_value = [
            {'id': '*', 'title': 'All'},
            {'id': '1', 'title': 'Drama'}
        ]

        # Test with missing category to trigger category selection
        params = 'action=series_search'
        self.stalker_addon.router(params)

        # Verify category selection was called but search was cancelled
        mock_ask_for_category_selection.assert_called_once()
        # Verify endOfDirectory was called to prevent hanging
        mock_xbmcplugin.endOfDirectory.assert_called_once()

    @patch('lib.addon.Api.get_vod_categories')
    @patch('lib.addon.ask_for_category_selection')
    @patch('lib.addon.ask_for_input')
    def test_search_vod_with_missing_category(self, mock_ask_for_input, mock_ask_for_category_selection, mock_get_vod_categories):
        """Test search_vod when category parameter is missing"""
        # Mock category selection
        mock_ask_for_category_selection.return_value = {'id': '1', 'title': 'Movies'}
        mock_ask_for_input.return_value = 'search_term'
        mock_get_vod_categories.return_value = [
            {'id': '*', 'title': 'All'},
            {'id': '1', 'title': 'Movies'}
        ]

        # Test with missing category parameter
        params = 'action=vod_search'
        self.stalker_addon.router(params)

        # Verify category selection was called
        mock_ask_for_category_selection.assert_called_once_with(
            [{'id': '*', 'title': 'All'}, {'id': '1', 'title': 'Movies'}], 'VOD Category'
        )
        # Verify search input was called with selected category
        mock_ask_for_input.assert_called_once_with('Movies')

    @patch('lib.addon.Api.get_tv_genres')
    @patch('lib.addon.ask_for_category_selection')
    @patch('lib.addon.ask_for_input')
    def test_search_tv_with_missing_category(self, mock_ask_for_input, mock_ask_for_category_selection, mock_get_tv_genres):
        """Test search_tv when category parameter is missing"""
        # Mock category selection
        mock_ask_for_category_selection.return_value = {'id': '1', 'title': 'English'}
        mock_ask_for_input.return_value = 'search_term'
        mock_get_tv_genres.return_value = [
            {'id': '*', 'title': 'All'},
            {'id': '1', 'title': 'English'}
        ]

        # Test with missing category parameter
        params = 'action=tv_search'
        self.stalker_addon.router(params)

        # Verify category selection was called
        mock_ask_for_category_selection.assert_called_once_with(
            [{'id': '*', 'title': 'All'}, {'id': '1', 'title': 'English'}], 'TV Genre'
        )
        # Verify search input was called with selected category
        mock_ask_for_input.assert_called_once_with('English')

    @patch('lib.addon.Api.get_series_categories')
    @patch('lib.addon.ask_for_category_selection')
    @patch('lib.addon.ask_for_input')
    def test_search_series_with_missing_category(self, mock_ask_for_input, mock_ask_for_category_selection, mock_get_series_categories):
        """Test search_series when category parameter is missing"""
        # Mock category selection
        mock_ask_for_category_selection.return_value = {'id': '1', 'title': 'Drama'}
        mock_ask_for_input.return_value = 'search_term'
        mock_get_series_categories.return_value = [
            {'id': '*', 'title': 'All'},
            {'id': '1', 'title': 'Drama'}
        ]

        # Test with missing category parameter
        params = 'action=series_search'
        self.stalker_addon.router(params)

        # Verify category selection was called
        mock_ask_for_category_selection.assert_called_once_with(
            [{'id': '*', 'title': 'All'}, {'id': '1', 'title': 'Drama'}], 'Series Category'
        )
        # Verify search input was called with selected category
        mock_ask_for_input.assert_called_once_with('Drama')
