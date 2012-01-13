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
import xbmcplugin
import xbmcgui

from utils.icacheable import ICacheable
from debug import log, info, warn
from constants import *
from utils.tag import IQobuzTag, QobuzTagUserPlaylist
'''
    Class QobuzUserPLaylists
'''
class QobuzUserPlaylists(ICacheable):

    def __init__(self, Core):
        self.Core = Core
        super(QobuzUserPlaylists, self).__init__(
                                               self.Core.Bootstrap.cacheDir,
                                               'userplaylists',
                                               0)
        self.set_cache_refresh(self.Core.Bootstrap.__addon__.getSetting('cache_duration_userplaylist'))
        self.fetch_data()

    def _fetch_data(self):
        raw_data = self.Core.Api.get_user_playlists()
        data = []
        for p in raw_data:
            data.append(p['playlist'])
        return data

    def length(self):
        if not self._raw_data:
           return 0
        return len(self._raw_data)

    def add_to_directory(self):
        n = self.length()
        if n < 1: return 0
        log(self,"Found " + str(n) + " playlist(s)")
        h = int(sys.argv[1])
        for track in self.get_data():
            t = QobuzTagUserPlaylist(self.Core, track)
            u = sys.argv[0] + "?mode=" + str(MODE_PLAYLIST) + "&id=" + t.id
            item = xbmcgui.ListItem()
            item.setLabel(t.owner_name + ' - ' + t.name)
            item.setInfo(type="Music",infoLabels={ "title": t.name })
            item.setProperty('Music','true')
            item.setProperty('IsPlayable','false');
            xbmcplugin.addDirectoryItem(handle=h,url=u,listitem=item,isFolder=True,totalItems=n)
        xbmcplugin.addSortMethod(h,xbmcplugin.SORT_METHOD_LABEL)
        return n
            
