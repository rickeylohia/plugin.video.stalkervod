"""
Compatible with Kodi 19.x "Matrix" and above
"""
from __future__ import absolute_import, division, unicode_literals
import re
import math
from urllib.parse import parse_qsl
import xbmc
import xbmcgui
import xbmcplugin
from .globals import G
from .utils import _ask_for_input
from .api import (get_categories, get_tv_genres, remove_favorites, add_favorites, get_vod_favorites,
                  get_tv_channels, get_videos, get_vod_stream_url, get_tv_stream_url)


def remove_favorites_refresh(params):
    """Remove from favorites and refresh"""
    remove_favorites(params['video_id'])
    url = G.get_plugin_url({'action': 'favorites', 'page': params['page'], 'update_listing': False})
    func_str = f'Container.Update({url})'
    xbmc.executebuiltin(func_str)


def play_video(video_id, series):
    """Play video"""
    stream_url = get_vod_stream_url(video_id, series)
    play_item = xbmcgui.ListItem(path=stream_url)
    xbmcplugin.setResolvedUrl(G.get_handle(), True, listitem=play_item)


def play_tv(cmd):
    """Play TV Channel"""
    stream_url = get_tv_stream_url(cmd)
    play_item = xbmcgui.ListItem(path=stream_url)
    xbmcplugin.setResolvedUrl(G.get_handle(), True, listitem=play_item)


def list_categories():
    """List categories"""
    xbmcplugin.setPluginCategory(G.get_handle(), 'VOD')
    xbmcplugin.setContent(G.get_handle(), 'videos')

    list_item = xbmcgui.ListItem(label='FAVORITES')
    url = G.get_plugin_url({'action': 'favorites', 'page': 1, 'update_listing': False})
    xbmcplugin.addDirectoryItem(G.get_handle(), url, list_item, True)

    list_item = xbmcgui.ListItem(label='TV CHANNELS')
    url = G.get_plugin_url({'action': 'tv', 'page': 1, 'update_listing': False})
    xbmcplugin.addDirectoryItem(G.get_handle(), url, list_item, True)
    categories = get_categories()
    for category in categories:
        list_item = xbmcgui.ListItem(label=category['title'])
        url = G.get_plugin_url({'action': 'search', 'category': category['title'], 'category_id': category['id']})
        list_item.addContextMenuItems([('Search', f'RunPlugin({url}, False)')])
        # list_item.setInfo('video', {'title': category['title'], 'mediatype': 'video'})
        url = G.get_plugin_url({'action': 'listing', 'category': category['title'], 'category_id': category['id'],
                                'page': 1, 'update_listing': False, 'search_term': ''})
        xbmcplugin.addDirectoryItem(G.get_handle(), url, list_item, True)
    xbmcplugin.endOfDirectory(G.get_handle(), succeeded=True, updateListing=False, cacheToDisc=False)


def list_tv_genres():
    """List TV channel genres"""
    xbmcplugin.setPluginCategory(G.get_handle(), 'TV CHANNELS')
    xbmcplugin.setContent(G.get_handle(), 'videos')
    genres = get_tv_genres()
    for genre in genres:
        list_item = xbmcgui.ListItem(label=genre['title'].upper())
        url = G.get_plugin_url({'action': 'tv_listing', 'category': genre['title'].upper(), 'category_id': genre['id'],
                                'page': 1, 'update_listing': False})
        xbmcplugin.addDirectoryItem(G.get_handle(), url, list_item, True)
    xbmcplugin.endOfDirectory(G.get_handle(), succeeded=True, updateListing=False, cacheToDisc=False)


def list_channels(params):
    """List TV Channels"""
    page = params['page']
    update_listing = params['update_listing']
    xbmcplugin.setPluginCategory(G.get_handle(), 'TV CHANNELS - ' + params['category'])
    xbmcplugin.setContent(G.get_handle(), 'videos')
    videos = get_tv_channels(params['category_id'], page)
    item_count = len(videos['data'])
    directory_items = []
    for video in videos['data']:
        label = video['name']
        list_item = xbmcgui.ListItem(label, label)
        list_item.setProperty('IsPlayable', 'true')
        url = G.get_plugin_url({'action': 'tv_play', 'cmd': video['cmd']})
        directory_items.append((url, list_item, False))
    if int(videos['total_items']) > item_count:
        add_navigation_items(params, videos, directory_items)
        item_count = item_count + 2
    xbmcplugin.addDirectoryItems(G.get_handle(), directory_items, item_count)
    xbmcplugin.addSortMethod(G.get_handle(), xbmcplugin.SORT_METHOD_NONE, '%DA')
    xbmcplugin.endOfDirectory(G.get_handle(), succeeded=True, updateListing=update_listing == 'True', cacheToDisc=False)


def list_videos(params):
    """List videos for a category"""
    search_term = params.get('search_term', '')
    xbmcplugin.setPluginCategory(G.get_handle(), params['category'])
    xbmcplugin.setContent(G.get_handle(), 'videos')
    videos = get_videos(params['category_id'], params['page'], search_term)
    create_video_listing(videos, params)


def list_favorites(params):
    """List Favorites Channels"""
    xbmcplugin.setPluginCategory(G.get_handle(), 'FAVORITES')
    xbmcplugin.setContent(G.get_handle(), 'videos')
    videos = get_vod_favorites(params['page'])
    create_video_listing(videos, params)


def create_video_listing(videos, params):
    """Create paginated listing"""
    page = params['page']
    update_listing = params['update_listing']
    item_count = len(videos['data'])
    directory_items = []
    for video in videos['data']:
        label = video['name'] if video['hd'] == 1 else video['name'] + ' (SD)'
        list_item = xbmcgui.ListItem(label, label)
        if params['action'] == 'favorites':
            url = G.get_plugin_url({'action': 'remove_fav', 'video_id': video['id'], 'page': page})
            list_item.addContextMenuItems([('Remove from favorites', f'RunPlugin({url}, False)')])
        else:
            url = G.get_plugin_url({'action': 'add_fav', 'video_id': video['id']})
            list_item.addContextMenuItems([('Add to favorites', f'RunPlugin({url}, False)')])

        is_folder = False
        poster_url = G.portal_config.portal_base_url + video['screenshot_uri']
        video_info = list_item.getVideoInfoTag()
        if video['series']:
            url = G.get_plugin_url({'action': 'sub_folder', 'video_id': video['id'], 'start': video['series'][0],
                                   'end': video['series'][-1], 'name': video['name'], 'poster_url': poster_url})
            is_folder = True
            video_info.setMediaType('season')
        else:
            url = G.get_plugin_url({'action': 'play', 'video_id': video['id'], 'series': 0})
            # if video['time'] and video['time'] != '0':
            #     video_info.setDuration(int(video['time']) * 60)
            video_info.setMediaType('movie')
            list_item.setProperty('IsPlayable', 'true')

        video_info.setTitle(video['name'])
        video_info.setOriginalTitle(video['name'])
        video_info.setSortTitle(video['name'])
        video_info.setCountries([video['country']])
        video_info.setDirectors([video['director']])
        video_info.setPlot(video['description'])
        video_info.setPlotOutline(video['description'])
        actors = [xbmc.Actor(actor) for actor in video['actors'].split(',') if actor]  # pylint: disable=maybe-no-member
        video_info.setCast(actors)
        video_info.setLastPlayed(video['last_played'])
        video_info.setDateAdded(video['added'])
        if video['year'].isdigit():
            video_info.setYear(int(video['year']))
        list_item.setArt({'poster': poster_url})
        directory_items.append((url, list_item, is_folder))
    # Add navigation items
    if int(videos['total_items']) > item_count:
        add_navigation_items(params, videos, directory_items)
        item_count = item_count + 2
    xbmcplugin.addDirectoryItems(G.get_handle(), directory_items, item_count)
    xbmcplugin.addSortMethod(G.get_handle(), xbmcplugin.SORT_METHOD_NONE, '%DA')
    xbmcplugin.endOfDirectory(G.get_handle(), succeeded=True, updateListing=update_listing == 'True', cacheToDisc=False)


def add_navigation_items(params, videos, directory_items):
    """Add navigation list items"""
    page = params['page']
    total_pages = int(math.ceil(float(videos['total_items']) / float(videos['max_page_items'])))
    _max_page_limit = G.addon_config.max_page_limit
    if _max_page_limit > 1:
        total_pages = total_pages if (total_pages % _max_page_limit) == 0 else total_pages + _max_page_limit - (
                total_pages % _max_page_limit)
    label = '<< Last Page' if int(page) == 1 else '<< Previous Page'
    list_item = xbmcgui.ListItem(label)
    list_item.setArt({'thumb': G.get_custom_thumb_path('pagePrevious.png')})
    list_item.setProperty('specialsort', 'top')
    prev_page = total_pages - _max_page_limit + 1 if int(page) == 1 else int(page) - _max_page_limit
    params.update({'page': prev_page, 'update_listing': True})
    url = G.get_plugin_url(params)
    directory_items.insert(0, (url, list_item, True))

    label = 'First Page >>' if int(page) == total_pages - _max_page_limit + 1 else 'Next Page >>'
    list_item = xbmcgui.ListItem(label)
    list_item.setArt({'thumb': G.get_custom_thumb_path('pageNext.png')})
    list_item.setProperty('specialsort', 'bottom')
    next_page = 1 if int(page) == total_pages - _max_page_limit + 1 else int(page) + _max_page_limit
    params.update({'page': next_page, 'update_listing': True})
    url = G.get_plugin_url(params)
    directory_items.append((url, list_item, True))


def list_episodes(params):
    """List episodes for a series"""
    name = params['name']
    xbmcplugin.setPluginCategory(G.get_handle(), name)
    xbmcplugin.setContent(G.get_handle(), 'videos')
    temp = name.split(' ')
    match = re.match("^S[0-9]+$", temp[-1])
    season = None
    if match:
        season = int(match.string[1:])
        name = ' '.join(temp[:-1])
    for episode_no in range(int(params['start']), int(params['end']) + 1):
        list_item = xbmcgui.ListItem(label='Episode ' + str(episode_no))
        video_info = list_item.getVideoInfoTag()
        video_info.setTitle(name)
        video_info.setOriginalTitle(name)
        if match:
            video_info.setEpisode(episode_no)
            video_info.setSeason(season)
            video_info.setSortSeason(season)
            video_info.setMediaType('episode')
            video_info.setTvShowTitle(name)
        else:
            video_info.setMediaType('movie')
        list_item.setProperties({'IsPlayable': 'true'})
        list_item.setArt({'poster': params['poster_url']})
        url = G.get_plugin_url({'action': 'play', 'video_id': params['video_id'], 'series': episode_no})
        xbmcplugin.addDirectoryItem(G.get_handle(), url, list_item, False)
    xbmcplugin.endOfDirectory(G.get_handle(), succeeded=True, updateListing=False, cacheToDisc=False)


def search(params):
    """Search for videos"""
    search_term = _ask_for_input(params['category'])
    if search_term:
        params.update({'action': 'listing', 'update_listing': False, 'search_term': search_term, 'page': 1})
        url = G.get_plugin_url(params)
        func_str = f'Container.Update({url})'
        xbmc.executebuiltin(func_str)


def router(param_string):
    """Route calls"""
    params = dict(parse_qsl(param_string))
    if params:
        if params['action'] == 'listing':
            list_videos(params)
        elif params['action'] == 'tv_listing':
            list_channels(params)
        elif params['action'] == 'sub_folder':
            list_episodes(params)
        elif params['action'] == 'play':
            play_video(params['video_id'], params['series'])
        elif params['action'] == 'tv_play':
            play_tv(params['cmd'])
        elif params['action'] == 'search':
            search(params)
        elif params['action'] == 'tv':
            list_tv_genres()
        elif params['action'] == 'favorites':
            list_favorites(params)
        elif params['action'] == 'remove_fav':
            remove_favorites_refresh(params)
        elif params['action'] == 'add_fav':
            add_favorites(params['video_id'])
        else:
            raise ValueError('Invalid param string: {}!'.format(param_string))
    else:
        list_categories()


def run(argv):
    """Run"""
    G.init_globals()
    router(argv[2][1:])
