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
import pprint

import qobuz
from constants import *
from flag import NodeFlag
from node import Node
from debug import *

'''
    NODE USER PLAYLISTS
'''

from cache.user_playlists import Cache_user_playlists
from cache.current_playlist import Cache_current_playlist
from playlist import Node_playlist

class Node_user_playlists(Node):

    def __init__(self, parent = None, parameters = None):
        super(Node_user_playlists, self).__init__(parent, parameters)
        self.label = qobuz.utils.lang(30019)
        self.icon = self.thumb = qobuz.image.access.get('userplaylists')
        self.label2 = 'Keep your current playlist'
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_USERPLAYLISTS
        self.set_content_type('files')
        display_by = self.get_parameter('display-by')
        if not display_by: display_by = 'songs'
        self.set_display_by(display_by)
        self.cache = Cache_user_playlists()
        self.cache_current_playlist = Cache_current_playlist()
        

    def set_display_by(self, type):
        vtype = ('product', 'songs')
        if not type in vtype:
            error(self, "Invalid display by: " + type)
        self.display_by = type

    def get_display_by(self):
        return self.display_by

    def _build_down(self, lvl, flag = None):
        info(self, "Build-down: user playlists")
        data = self.cache.fetch_data()
        if not data:
            warn(self, "Build-down: Cannot fetch user playlists data")
            return False
        self.set_data(data)
        print "DATA: " + repr(data)
        jcurrent_playlist = self.cache_current_playlist.fetch_data()
        print "CURRENT PLAYLIST: " + jcurrent_playlist['id']
        for playlist in data:
            node = Node_playlist()
            node.set_data(playlist)
            if (jcurrent_playlist and jcurrent_playlist['id'] == str(node.get_id())):
                node.set_is_current(True)
            self.add_child(node)

    def _get_xbmc_items(self, list, lvl, flag):
        username = qobuz.addon.getSetting('username')
        color = qobuz.addon.getSetting('color_notowner')
        for playlist in self.childs:
            item = playlist.make_XbmcListItem()#tag.getXbmcItem()
            #print "URL: " + item.getProperty('Path')
            if playlist.get_owner() != username:
                item.setLabel(''.join([qobuz.utils.color(color, playlist.get_owner()), ' - ', playlist.get_name()]))
            else:
                self.attach_context_menu(item, playlist)
            
            if playlist.is_current():
                label = item.getLabel()
                item.setLabel(qobuz.utils.color(color, '-> ') + label + qobuz.utils.color(color, ' <-'))
            list.append((playlist.get_url(), item, playlist.is_folder()))
        return True

    def hook_attach_context_menu(self, item, node, menuItems, color):
#        ''' RENAME '''
#        url=sys.argv[0]+"?mode="+str(MODE_RENAME_PLAYLIST)+'&nt='+str(type)
#        if id: url+='&nid='+id
#        menuItems.append((qobuz.utils.color(qobuz.addon.getSetting('color_ctxitem'), 'Rename'), "XBMC.RunPlugin("+url+")"))
#        
#        ''' DELETE '''
#        url=sys.argv[0]+"?mode="+str(MODE_REMOVE_PLAYLIST)+'&nt='+str(type)
#        if id: url+='&nid='+id
#        menuItems.append((qobuz.utils.color(qobuz.addon.getSetting('color_ctxitem'), 'Delete'), "XBMC.RunPlugin("+url+")"))
#        
        ''' SET AS CURRENT '''
        url=sys.argv[0]+"?mode="+str(Mode.SELECT_CURRENT_PLAYLIST)+'&nt='+str(node.get_type())
        if node.get_id(): url +='&nid='+node.get_id()
        menuItems.append((qobuz.utils.color(color, 'Set as current: ' + item.getLabel()), "XBMC.RunPlugin("+url+")"))
#        
        ''' CREATE '''
        url=sys.argv[0]+"?mode="+str(Mode.CREATE_PLAYLIST)+'&nt='+str(node.get_type())
        if node.get_id(): url+='&nid='+node.get_id()
        menuItems.append((qobuz.utils.color(color, 'Create'), "XBMC.RunPlugin("+url+")"))

        ''' RENAME '''
        url=sys.argv[0]+"?mode="+str(Mode.RENAME_PLAYLIST)+'&nt='+str(node.get_type())
        if node.get_id(): url+='&nid='+node.get_id()
        menuItems.append((qobuz.utils.color(color, 'Rename'), "XBMC.RunPlugin("+url+")"))

        ''' REMOVE '''
        url=sys.argv[0]+"?mode="+str(Mode.REMOVE_PLAYLIST)+'&nt='+str(node.get_type())
        if node.get_id(): url+='&nid='+node.get_id()
        menuItems.append((qobuz.utils.color(color, 'Remove *CAUTION*'), "XBMC.RunPlugin("+url+")"))

        ''' Display by '''
#        display_by = 'songs'
#        if self.display_by == 'songs':
#            display_by = 'product'
#        url=sys.argv[0]+"?mode="+str(MODE_NODE)+'&nt='+str(self.type)+'&display-by='+display_by
#        menuItems.append((qobuz.utils.color(qobuz.addon.getSetting('color_ctxitem'), 'Display by: ' + display_by), "XBMC.RunPlugin("+url+")"))


    def set_current_playlist(self, id):
        info(self, "Set current playlist: " + str(id))
        from cache.current_playlist import Cache_current_playlist
        cp = Cache_current_playlist()
        if cp.get_id() == id:
            log(self, "Playlist already selected... do nothing")
            return True
        print "set cpls id: " + id
        cp.set_id(id)
        cp.save()
        xbmc.executebuiltin('Container.Refresh')
        return True

    def create_playlist(self):
        from utils.cache import cache_manager
        from cache.user_playlists import Cache_user_playlists
        query = self._get_keyboard(default="",heading='Create playlist')
        query = query.strip()
        #info(self, "Query: " + repr(query))
        if query != '':
            print "Creating playlist: " + query
        ret = qobuz.api.playlist_create(query, '', '', '', 'off', 'off')
        if not ret:
            warn(self, "Cannot create playlist name '"+ query +"'")
            return False
        print ret
        userplaylists = Cache_user_playlists()
        cm = cache_manager()
        cm.delete(userplaylists.get_cache_path())
        self.set_current_playlist(ret['playlist']['id'])
        info(self, "Container refreshing neeeded!")
        xbmc.executebuiltin('Container.Refresh')
        
    def rename_playlist(self, id):
        log(self, "rename playlist: " + str(id))
        from cache.playlist import Cache_playlist
        from utils.cache import cache_manager
        from cache.user_playlists import Cache_user_playlists
        userplaylist = Cache_playlist(id)
        userplaylist.fetch_data()
        currentname = userplaylist.get_data()['name']
        query = self._get_keyboard(default=currentname,heading='Rename playlist')
        query = query.strip()
        cm = cache_manager()
        userplaylists = Cache_user_playlists()
        cm.delete(userplaylists.get_cache_path())
        res = qobuz.api.playlist_update(id, query)
        xbmc.executebuiltin('Container.Refresh')
        
    def remove_playlist(self, id):
        from cache.user_playlists import Cache_user_playlists
        info(self, "Deleting playlist: " + id)
        res = qobuz.api.playlist_delete(id)
        if not res:
            print "Cannot delete playlist with id " + str(id)
            return False
        print "Playlist deleted: " + str(id)
        from utils.cache import cache_manager
        cm = cache_manager()
        userplaylists = Cache_user_playlists() 
        cm.delete(userplaylists.get_cache_path())
        xbmc.executebuiltin('Container.Refresh')