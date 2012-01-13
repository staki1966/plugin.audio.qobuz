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
import os
import sys
import pprint

import xbmcaddon
import xbmcplugin
import xbmcgui
import xbmc


from utils.icacheable import ICacheable
from debug import *
#from utils import _sc
from constants import *
from utils.tag import QobuzTagProduct
from utils.tag import QobuzTagTrack

###############################################################################
# Class QobuzProduct
###############################################################################
class QobuzProduct(ICacheable):

    def __init__(self, Core, id, context_type = "playlist" ):
        self.Core = Core
        self.id = id
        self.context_type = context_type
        super(QobuzProduct, self).__init__( self.Core.Bootstrap.cacheDir, 
                                          'product',
                                          self.id)
        self.set_cache_refresh(self.Core.Bootstrap.__addon__.getSetting('cache_duration_album'))
        info(self, "Cache duration: " + str(self.cache_refresh))
        self.fetch_data()

    def _fetch_data(self):
        data = self.Core.Api.get_product(str(self.id),self.context_type)['product']
        return data

    def length(self):
        return len(self._raw_data['tracks'])

    def add_to_directory(self):
        n = self.length()
#        xp = self.Core.Bootstrap.Player.Playlist
#        xp.clear()
        i = 0
        h = int(sys.argv[1])
        p = QobuzTagProduct(self.Core, self.get_data())
        for t in p.get_childs():
            if not isinstance(t, QobuzTagTrack):
                continue
            item = t.getXbmcItem('album')
            u = sys.argv[0] + "?mode=" + str(MODE_SONG) + "&id=" + t.id + "&pos=" + str(i) + "&context_type=" + self.context_type
            self.Core.Bootstrap.GUI.addDirectoryItem(u , item, False, n)
#            xp.add(u, item, int(t.id))
            i = i + 1
#        xp.save()
        return n