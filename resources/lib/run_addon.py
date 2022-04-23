"""
Compatible with Kodi 19.x "Matrix" and above
"""
import json
import re
import sys
from unicodedata import category
from urllib.parse import urlencode, parse_qsl, urlsplit
import xbmcgui
import xbmcplugin
import xbmcaddon
import requests
import math
import simplecache
import xbmc
import os

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')

_cache = simplecache.SimpleCache()
_cache.data_is_json = False

def getBaseUrl(url):
    split_url = urlsplit(url)
    return split_url.scheme + '://' + split_url.netloc

# Get the plugin url in plugin:// notation.
_URL = sys.argv[0]
# Get the plugin handle as an integer number.
HANDLE = int(sys.argv[1])


MAC_COOKIE = 'mac=' + ADDON.getSetting('mac_address')
PORTAL_URL = ADDON.getSetting('server_address')
DEVICE_ID = ADDON.getSetting('device_id')
DEVICE_ID_2 = ADDON.getSetting('device_id_2')
SIGNATURE = ADDON.getSetting('signature')
TOKEN = _cache.get(ADDON_ID+'TOKEN')
BASE_URL = getBaseUrl(PORTAL_URL)
CONTEXT_PATH = '/stalker_portal/server/load.php'
DATA_PATH = ADDON.getAddonInfo('profile')
MAX_PAGE_LIMIT = 2
MAX_RETRIES = 1
ADDON_DATA_PATH = ADDON.getAddonInfo('path')


def _get_custom_thumb_path(thumb_file_name):
    return os.path.join(ADDON_DATA_PATH, 'resources', 'media', thumb_file_name)

def ask_for_input():
    return xbmcgui.Dialog().input(
        defaultt=None,
        heading='Search by title',
        type=xbmcgui.INPUT_ALPHANUM) or None

def callPortal(params):
    response = {}
    retries = 0
    while True:
        if not _cache.get(ADDON_ID+'TOKEN'):
            token = requests.get(url = BASE_URL+CONTEXT_PATH, 
                headers = {'Cookie':MAC_COOKIE},
                params = {'type': 'stb', 'action': 'handshake'}
            ).json()['js']['token']
            requests.get(url = BASE_URL+CONTEXT_PATH, 
                headers = {'Cookie':MAC_COOKIE, 'Authorization':'Bearer ' + token},
                params = {'type': 'stb', 'action': 'get_profile', 'hd': '1', 'auth_second_step': '1', 'device_id': DEVICE_ID, 'device_id2': DEVICE_ID_2, 'signature': SIGNATURE}
            )
            _cache.set(ADDON_ID+'TOKEN', token)
        response = requests.get(url = BASE_URL+CONTEXT_PATH, 
            headers={'Cookie':MAC_COOKIE, 'Authorization':'Bearer ' + _cache.get(ADDON_ID+'TOKEN')},
            params=params
        )
        if response.content.decode('utf-8') != 'Authorization failed.' or retries == MAX_RETRIES:
            break
        _cache.set(ADDON_ID+'TOKEN', '')
        retries+=1
    return response.json()

def get_url(**kwargs):
    return '{}?{}'.format(_URL, urlencode(kwargs))

def get_categories():
    params = {'type': 'vod', 'action': 'get_categories'}
    return callPortal(params)['js']

def get_videos(category_id, page, search_term):
    videos = []
    total_items = 0
    max_page_items = 0
    for x in range(int(page), int(page)+MAX_PAGE_LIMIT):
        params = {'type': 'vod', 'action': 'get_ordered_list', 'category': category_id, 'p': str(x), 'sortby': 'added'}
        if bool(search_term.strip()):
            params.update({'search': search_term})
        response = callPortal(params)['js']
        videos+=response['data']
        total_items = response['total_items']
        max_page_items = response['max_page_items']
    return {'max_page_items': max_page_items, 'total_items': total_items, 'data': videos}

def list_categories():
    xbmcplugin.setPluginCategory(HANDLE, 'VOD')
    xbmcplugin.setContent(HANDLE, 'videos')
    categories = get_categories()
    for category in categories:
            if category['title'] != 'All':
                list_item = xbmcgui.ListItem(label=category['title'])
                list_item.addContextMenuItems([('Search', "Container.Update(%s)" % get_url(action='search', category=category['title'], category_id=category['id']))])
                list_item.setInfo('video', {'title': category['title'], 'mediatype': 'video'})
                url = get_url(action='listing', category=category['title'], category_id=category['id'], page=1, updateListing=False, search_term='')
                xbmcplugin.addDirectoryItem(HANDLE, url, list_item, True)
    xbmcplugin.endOfDirectory(HANDLE, succeeded=True, updateListing=False, cacheToDisc=False)

def list_videos(category, category_id, page, updateListing, search_term):
    xbmcplugin.setPluginCategory(HANDLE, category)
    xbmcplugin.setContent(HANDLE, 'movies')
    videos = get_videos(category_id, page, search_term)
    item_count = len(videos['data'])
    directoryItems = []
    for video in videos['data']:
        label=video['name'] if video['hd'] == 1 else video['name']+' (SD)'
        list_item = xbmcgui.ListItem(label=label)
        is_folder = False
        url = get_url(action='play', video_id=video['id'], series=0)
        info = {}
        img = BASE_URL+video['screenshot_uri']
        if video['series']:
            url = get_url(action='sub_folder', video_id=video['id'], start=video['series'][0], end=video['series'][-1], name=video['name'], screen=img)
            is_folder = True
            info['mediatype'] = 'season'
        else:
            if video['time'] and video['time'] != '0':
                info['duration'] = float(video['time'])*60
            info['mediatype'] = 'movie'
            list_item.setProperty('IsPlayable', 'true')
        
        info['title'] = video['name']
        info['originaltitle'] = video['name']
        info['sorttitle'] = video['name']
        info['country'] = video['country']
        info['director'] = video['director']
        info['plot'] = video['description']
        info['plotoutline'] = video['description']
        info['cast'] = video['actors'].split(',')
        info['lastplayed'] = video['last_played']
        info['dateadded'] = video['added']
        if video['year'].isdigit():
            info['year'] = int(video['year'])
        list_item.setInfo('video', info)        
        list_item.setArt({'poster': img})
        directoryItems.append((url, list_item, is_folder))
    if int(videos['total_items']) > int(videos['max_page_items']):
        totalPages = int(math.ceil(float(videos['total_items'])/float(videos['max_page_items'])))
        if MAX_PAGE_LIMIT > 1:
            totalPages = totalPages if (totalPages % MAX_PAGE_LIMIT) == 0 else totalPages + MAX_PAGE_LIMIT - (totalPages % MAX_PAGE_LIMIT)
        list_item = xbmcgui.ListItem('<< Previous page')
        list_item.setArt({'thumb': _get_custom_thumb_path('FolderPagePrevious.png')})
        list_item.setProperty('specialsort', 'top')
        prevPage = totalPages - MAX_PAGE_LIMIT + 1 if int(page) == 1 else int(page) - MAX_PAGE_LIMIT
        url = get_url(action='listing', category=category, category_id=category_id, page=prevPage, updateListing=True, search_term=search_term)
        directoryItems.insert(0, (url, list_item, True))

        list_item = xbmcgui.ListItem('Next page >>')
        list_item.setArt({'thumb': _get_custom_thumb_path('FolderPageNext.png')})
        list_item.setProperty('specialsort', 'bottom')
        nextPage = 1 if int(page) == totalPages - MAX_PAGE_LIMIT + 1 else int(page) + MAX_PAGE_LIMIT
        url = get_url(action='listing', category=category, category_id=category_id, page=nextPage, updateListing=True, search_term=search_term)
        directoryItems.append((url, list_item, True))
        item_count = item_count + 2
    xbmcplugin.addDirectoryItems(HANDLE, directoryItems, item_count)
    xbmcplugin.endOfDirectory(HANDLE, succeeded=True, updateListing=updateListing == 'True', cacheToDisc=False)


def play_video(video_id, series):
    path = callPortal(
        {'type': 'vod', 'action': 'create_link', 'cmd': '/media/'+video_id+'.mpg', 'series': str(series)}
    )['js']['cmd']
    callPortal({'type': 'stb', 'action': 'log', 'real_action': 'play', 'param': path, 'content_id': video_id})
    play_item = xbmcgui.ListItem(path=path)
    xbmcplugin.setResolvedUrl(HANDLE, True, listitem=play_item)

def list_episodes(video_id, start, end, name, screen):
    xbmcplugin.setPluginCategory(HANDLE, name)
    xbmcplugin.setContent(HANDLE, 'videos')
    for x in range(int(start), int(end)):
        list_item = xbmcgui.ListItem(label='Episode '+str(x))
        list_item.setInfo('video', {'title': name, 'originaltitle': name, 'episode': x,
                                    'mediatype': 'movie'})
        list_item.setProperty('IsPlayable', 'true')
        list_item.setArt({'poster': screen})
        url = get_url(action='play', video_id=video_id, series=x)
        xbmcplugin.addDirectoryItem(HANDLE, url, list_item, False)
    xbmcplugin.endOfDirectory(HANDLE, succeeded=True, updateListing=False, cacheToDisc=False)

def router(paramstring):
    params = dict(parse_qsl(paramstring))
    if params:
        if params['action'] == 'listing':
            search_term = ''
            if 'search_term' in params:
                search_term = params['search_term']
            list_videos(params['category'], params['category_id'], params['page'], params['updateListing'], search_term)
        elif params['action'] == 'sub_folder':
            list_episodes(params['video_id'], params['start'], params['end'], params['name'], params['screen'])
        elif params['action'] == 'play':
            play_video(params['video_id'], params['series'])
        elif params['action'] == 'search':
            search(params['category'], params['category_id'])
        else:
            raise ValueError('Invalid paramstring: {}!'.format(paramstring))
    else:
        list_categories()

def search(category, category_id):
    search_term = ask_for_input()
    list_videos(category, category_id, 1, False, search_term)

def run(argv):
    router(sys.argv[2][1:])