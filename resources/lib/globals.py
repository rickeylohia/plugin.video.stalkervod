import sys
from unicodedata import category
from urllib.parse import urlencode, parse_qsl, urlsplit
import xbmcgui
import xbmcplugin
import xbmcaddon
import requests
import math

class GlobalVariables:

    def __init__(self):
        self.IS_ADDON_FIRSTRUN = None
        self.ADDON = None
        self.ADDON_DATA_PATH = None
        self.DATA_PATH = None
        self.CACHE_MANAGEMENT = None
        self.CACHE_TTL = None
        self.CACHE_MYLIST_TTL = None
        self.CACHE_METADATA_TTL = None

    def init_globals(self, argv):
        self.URL = urlparse(argv[0])
        self.ADDON = xbmcaddon.Addon()
MAC_COOKIE = 'mac='+ADDON.getSetting('mac_address')
PORTAL_URL = ADDON.getSetting('server_address')
DEVICE_ID = ADDON.getSetting('device_id')
DEVICE_ID_2 = ADDON.getSetting('device_id_2')
SIGNATURE = ADDON.getSetting('signature')
TOKEN = 'AF5283DE7CCCC3BCF3CE3DFBBB74F989'
BASE_URL = getBaseUrl(PORTAL_URL)
CONTEXT_PATH = '/stalker_portal/server/load.php'
DATA_PATH = ADDON.getAddonInfo('profile')

    def getBaseUrl(url):
        split_url = urlsplit(url)
        return split_url.scheme + '://' + split_url.netloc