#     Copyright 2011 Joachim Basmaison, Cyril Leclerc
#
#     This file is part of xbmc-qobuz.
#
#     xbmc-qobuz is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     xbmc-qobuz is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.   See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with xbmc-qobuz.   If not, see <http://www.gnu.org/licenses/>.
import sys
import xbmcgui
import xbmcplugin
from utils import _sc
from constants import *
from mydebug import log, info, warn

import pprint

from easytag import QobuzTagArtist

###############################################################################
# Class QobuzSearchArtists
###############################################################################
class QobuzSearchArtists():

    def __init__(self, Core):
        self.Core = Core
        self._raw_data = []
        
    def get_data(self):
        return self._raw_data
    
    def search(self, query, limit = 100):
        self._raw_data = self.Core.Api.search_artists(query, limit)
        return self
        
    def length(self):
        try:
            self._raw_data['results']
        except: return 0
        try:
            self._raw_data['results']['artists']
        except: return 0
        return len(self._raw_data['results']['artists'])
    
    def add_to_directory(self):
        self.xbmc_directory_products()
    
    def add_to_directory_by_artist(self):
        self.xbmc_directory_products_by_artist()

    def xbmc_directory_products(self):
        for p in self.get_data()['results']['artists']:
            a = QobuzTagArtist(self.Core, p)
            u = sys.argv[0] + "?mode=" + str(MODE_ARTIST) + "&id=" + a.id
            item   = xbmcgui.ListItem()
            item.setLabel(a.getArtist() )
            self.Core.Bootstrap.GUI.addDirectoryItem(u , item, True, self.length())

    def xbmc_directory_products_by_artist():
        artist = self.get_data()['artist']['name']
        for p in json['artist']['albums']:
            a = QobuzTagAlbum(self.Core, p)
            u = sys.argv[0] + "?mode=" + str(MODE_ALBUM) + "&id=" + a.id
            item = a.getXbmcItem('album')
            self.Core.Bootstrap.GUI.addDirectoryItem(u , item, True, self.length())
