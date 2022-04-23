"""
Compatible with Kodi 19.x "Matrix" and above
"""
import sys
from urllib.parse import urlencode, parse_qsl
import xbmcgui
import xbmcplugin
import xbmcaddon
import requests

# Get the plugin url in plugin:// notation.
_URL = sys.argv[0]
# Get the plugin handle as an integer number.
_HANDLE = int(sys.argv[1])

addon = xbmcaddon.Addon()
mac_address = 'mac='+addon.getSetting('mac_address')
server_address = addon.getSetting('server_address')
device_id = addon.getSetting('device_id')
device_id_2 = addon.getSetting('device_id_2')
signature = addon.getSetting('signature')
token = 'DB5EE1F7864815AE3227929505349FC5'

def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.
    :param kwargs: "argument=value" pairs
    :return: plugin call URL
    :rtype: str
    """
    return '{}?{}'.format(_URL, urlencode(kwargs))


def get_categories():
    """
    Get the list of video categories.
    Here you can insert some parsing code that retrieves
    the list of video categories (e.g. 'Movies', 'TV-shows', 'Documentaries' etc.)
    from some site or API.
    .. note:: Consider using `generator functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.
    :return: The list of video categories
    :rtype: types.GeneratorType
    """
    return requests.get(url = 'http://new.atnt.cc/stalker_portal/server/load.php?type=vod&action=get_categories&JsHttpRequest=1-xml', headers={'Cookie':mac_address, 'Authorization':'Bearer '+token}).json()['js']


def get_videos(category_id):
    """
    Get the list of videofiles/streams.
    Here you can insert some parsing code that retrieves
    the list of video streams in the given category from some site or API.
    .. note:: Consider using `generators functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.
    :param category: Category name
    :type category: str
    :return: the list of videos in the category
    :rtype: list
    """
    page = 1
    while True:
        vidoes = requests.get(url = 'http://new.atnt.cc/stalker_portal/server/load.php?type=vod&action=get_ordered_list&category='+category_id+'&fav=0&sortby=added&hd=0&not_ended=0&p='+str(page)+'&JsHttpRequest=1-xml', headers={'Cookie':mac_address, 'Authorization':'Bearer '+token}).json()['js']['data']
        if vidoes:
            page = page + 1
            for video in vidoes:
                yield video
        break



def list_categories():
    """
    Create the list of video categories in the Kodi interface.
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_HANDLE, 'VOD')
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_HANDLE, 'videos')
    # Get video categories
    categories = get_categories()
    # Iterate through categories
    for category in categories:
            if category['title'] != 'All':
                # Create a list item with a text label and a thumbnail image.
                list_item = xbmcgui.ListItem(label=category['title'])
                # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
                # Here we use the same image for all items for simplicity's sake.
                # In a real-life plugin you need to set each image accordingly.
                # list_item.setArt({'thumb': VIDEOS[category][0]['thumb'],
                #                 'icon': VIDEOS[category][0]['thumb'],
                #                 'fanart': VIDEOS[category][0]['thumb']})
                # Set additional info for the list item.
                # Here we use a category name for both properties for for simplicity's sake.
                # setInfo allows to set various information for an item.
                # For available properties see the following link:
                # https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
                # 'mediatype' is needed for a skin to display info for this ListItem correctly.
                list_item.setInfo('video', {'title': category['title'],
                                            'mediatype': 'video'})
                # Create a URL for a plugin recursive call.
                # Example: plugin://plugin.video.example/?action=listing&category=Animals
                url = get_url(action='listing', category=category['title'], category_id=category['id'])
                # is_folder = True means that this item opens a sub-list of lower level items.
                is_folder = True
                # Add our item to the Kodi virtual folder listing.
                xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    # xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_HANDLE)


def list_videos(category, category_id):
    xbmcplugin.setPluginCategory(_HANDLE, category)
    xbmcplugin.setContent(_HANDLE, 'movies')
    for video in list(get_videos(category_id)):
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=video['name'])
        # Set additional info for the list item.
        # 'mediatype' is needed for skin to display info for this ListItem correctly.
        is_folder = False
        url = get_url(action='play', video_id=video['id'], series=0)
        info = {}
        img = 'http://new.atnt.cc'+video['screenshot_uri']
        if video['series']:
            url = get_url(action='sub_folder', video_id=video['id'], start=video['series'][0], end=video['series'][-1], name=video['name'], screen=img)
            is_folder = True
            info['mediatype'] = 'season'
        else:
            if video['time'] != '0':
                info['duration'] = int(video['time'])*60
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
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        
        list_item.setArt({'poster': img})
        xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)
    xbmcplugin.endOfDirectory(_HANDLE)


def play_video(video_id, series):
    """
    Play a video by the provided path.
    :param path: Fully-qualified video URL
    :type path: str
    """
    # Create a playable item with a path to play.
    path = requests.get(url = 'http://new.atnt.cc/stalker_portal/server/load.php?type=vod&action=create_link&cmd=/media/'+video_id+'.mpg&series='+str(series)+'&forced_storage=&disable_ad=0&download=0&JsHttpRequest=1-xml', headers={'Cookie':mac_address, 'Authorization':'Bearer '+token}).json()['js']['cmd']
    requests.get(url='http://new.atnt.cc/stalker_portal/server/load.php?type=stb&action=log&real_action=play&param='+path+'&content_id='+video_id+'&tmp_type=2&JsHttpRequest=1-xml', headers={'Cookie':mac_address, 'Authorization':'Bearer '+token})
    play_item = xbmcgui.ListItem(path=path)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_HANDLE, True, listitem=play_item)

def list_episodes(video_id, start, end, name, screen):
    xbmcplugin.setPluginCategory(_HANDLE, name)
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_HANDLE, 'videos')
    for x in range(int(start), int(end)):
        list_item = xbmcgui.ListItem(label='Episode '+str(x))
        list_item.setInfo('video', {'title': name, 'originaltitle': name, 'episode': x,
                                    'mediatype': 'movie'})
        list_item.setProperty('IsPlayable', 'true')
        list_item.setArt({'poster': screen})
        url = get_url(action='play', video_id=video_id, series=x)
        is_folder = False
        xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)
    xbmcplugin.endOfDirectory(_HANDLE)

def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring
    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'listing':
            # Display the list of videos in a provided category.
            list_videos(params['category'], params['category_id'])
        elif params['action'] == 'sub_folder':
            # Play a video from a provided URL.
            list_episodes(params['video_id'], params['start'], params['end'], params['name'], params['screen'])
        elif params['action'] == 'play':
            # Play a video from a provided URL.
            play_video(params['video_id'], params['series'])
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_categories()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])