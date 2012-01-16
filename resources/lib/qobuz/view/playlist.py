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
import xbmc
import xbmcgui
import xbmcplugin

from utils.icacheable import ICacheable
from constants import *
from debug import * 
from utils.tag import QobuzTagPlaylist
from utils.tag import QobuzTagTrack
'''
    Class QobuzPLaylist
'''
class QobuzPlaylist(ICacheable):

    def __init__(self, Core, id):
        self.Core = Core
        self.id = id
        super(QobuzPlaylist, self).__init__(self.Core.Bootstrap.cacheDir,
                                            'playlist',
                                            self.id)
        self.set_cache_refresh(self.Core.Bootstrap.__addon__.getSetting('cache_duration_userplaylist'))
        info(self, "Cache duration: " + str(self.cache_refresh))
        self.fetch_data()

    def _fetch_data(self):
        data = self.Core.Api.get_playlist(self.id)['playlist']
        return data

    def length(self):
        return len(self._raw_data['tracks'])

    def get_items(self):
        p = QobuzTagPlaylist(self.get_data())
        list = []
        for t in p.get_childs():
            if not isinstance(t, QobuzTagTrack):
                continue
            item = t.getXbmcItem('playlist')
            print "Label:" + item.getLabel()
            u = self.Core.Bootstrap.build_url(MODE_SONG, str(t.id))
            item.setPath(u) 
            list.append((u, item, False))
        return list
