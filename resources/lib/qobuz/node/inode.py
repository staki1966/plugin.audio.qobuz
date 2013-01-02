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
import weakref
import pprint

import xbmcgui

import qobuz
from constants import Mode
from flag import NodeFlag as Flag
from exception import QobuzXbmcError
from gui.util import color, lang, runPlugin, containerUpdate, formatControlLabel

'''
    @class Inode:
'''

class INode(object):

    def __init__(self, parent=None, parameters=None):
        self.parameters = parameters or {}
        self.id = self.get_parameter('nid')
        self.parent = parent
        self.type = self.get_parameter('nt') or Flag.NODE
        self.content_type = "files"
        self.image = None
        self.childs = []
        self.label = ''
        self.label2 = ''
        self.is_folder = True
        self._data = None
        self.pagination_next = None
        self.pagination_prev = None
        self.offset = None

    ''' Id '''
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @id.getter
    def id(self):
        if self._data and 'id' in self._data:
            return self._data['id']
        return self._id

    ''' Parent '''
    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        if not parent:
            self._parent = None
            return
        self._parent = weakref.proxy(parent)

    @parent.getter
    def parent(self):
        return self._parent

    def delete_tree(self):
        for child in self.childs:
            child.delete_tree()
        del self.childs
        del self.parent
        del self.parameters

    ''' content_type '''
    @property
    def content_type(self):
        return self._content_type

    @content_type.getter
    def content_type(self):
        return self._content_type

    @content_type.setter
    def content_type(self, type):
        if type not in ['songs', 'albums', 'files', 'artist']:
            raise QobuzXbmcError(
                who=self, what='invalid_type', additional=type)
        self._content_type = type

    ''' data '''
    @property
    def data(self):
        return self._data

    @data.getter
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self.hook_post_data()

    ''' Called after node data is set '''
    def hook_post_data(self):
        pass

    ''' Property are just a easy way to access JSON data when set '''
    def get_property(self, path):
        if not self._data:
            return ''
        if isinstance(path, basestring):
            if path in self._data and self._data[path] and self._data[path] != 'None':
                return self._data[path]
            return ''
        root = self._data
        for i in range(0, len(path)):
            if not path[i] in root:
                return ''
            root = root[path[i]]
        if root and root != 'None':
            return root
        return ''

    '''
    Called with data from our API, adding special child if pagination
    is required
    '''
    def add_pagination(self, data):
        paginated = ['albums', 'labels', 'tracks', 'artists',
                     'playlists', 'playlist']
        items = None
        need_pagination = False
        for p in paginated:
            if p in data:
                items = data[p]
                if items['limit'] is None:
                    continue
                if items['total'] > (items['offset'] + items['limit']):
                    need_pagination = True
                    break
        if not need_pagination:
            return False
        url = self.make_url(offset=items['offset'] + items['limit'])
        self.pagination_next = url
        self.pagination_total = items['total']
        self.pagination_offset = items['offset']
        self.pagination_limit = items['limit']
        self.pagination_next_offset = items['offset'] + items['limit']

    def to_s(self):
        s = "[Node][" + str(self.type) + "\n"
        s += " id: " + str(self.id) + "\n"
        s += " Label : " + str(self.label) + "\n"
        s += " label2: " + str(self.label2) + "\n"
        data = self.data
        if data:
            s += 'data:' + pprint.pformat(data)
        return s

    '''
        Parameters
        A hash for storing script parameter, each node have a copy of them.
        TODO: each node don't need to copy parameter
    '''
    def set_parameters(self, params):
        self.parameters = params

    def set_parameter(self, name, value):
        self.parameters[name] = value

    def get_parameter(self, name):
        if not name in self.parameters:
            return None
        return self.parameters[name]

    '''
        Make url
        This function is responsible to create the link to this node.
        Class who implement custom parameter must overload this method
    '''
    def make_url(self, **ka):
        if not 'mode' in ka:
            ka['mode'] = Mode.VIEW
        else:
            ka['mode'] = int(ka['mode'])
        if not 'type' in ka:
            ka['type'] = self.type
        if not 'id' in ka and self.id:
            ka['id'] = self.id
        url = sys.argv[0] + '?mode=' + str(ka['mode']) + '&nt=' + \
            str(ka['type'])
        offset = self.offset
        if 'offset' in ka: offset = ka['offset']
        if offset != None:
            url += '&offset=' + str(offset)
        if 'id' in ka:
            url += "&nid=" + str(ka['id'])
        action = self.get_parameter('action')
        if action:
            url += "&action=" + action
        if 'nm' in ka:
            url += '&nm=' + ka['nm']
        qnt = self.get_parameter('qnt')
        if 'qnt' in ka:
            qnt = ka['qnt']
        if qnt:
            url+= '&qnt=' + str(qnt)
        if 'query' in ka:
            url+= '&query=' + ka['query']
      
        return url

    '''
        Make Xbmc List Item
        return  a xbml list item
        Class can overload this method
    '''
    def make_XbmcListItem(self, **ka):
        if not 'url' in ka:
            ka['url'] = self.make_url()
        if not 'label' in ka:
            ka['label'] = self.get_label()
        if not 'label2' in ka:
            ka['label2'] = self.get_label2()
        if not 'image' in ka:
            ka['image'] = self.get_image()
        item = xbmcgui.ListItem(
            ka['label'],
            ka['label2'],
            ka['image'],
            ka['image'],
            ka['url']
        )
        menuItems = []
        self.attach_context_menu(item, menuItems)
        if len(menuItems) > 0:
            item.addContextMenuItems(menuItems, replaceItems=False)
        return item

    def add_child(self, child):
        child.parent = self
        child.set_parameters(self.parameters)
        self.childs.append(child)
        return self

    def get_childs(self):
        return self.childs

    def get_siblings(self, type):
        list = []
        for c in self.childs:
            if c.getType() == type:
                list.append(c)
        return list

    def set_label(self, label):
        self.label = label.encode('utf8', 'replace')
        return self

    def get_image(self):
        if self.image:
            return self.image
        if self.parent:
            return self.parent.get_image()
        return ''

    def set_image(self, image):
        self.image = image
        return self

    def set_label2(self, label):
        self.label2 = label.encode('utf8', 'replace')
        return self

    def get_label(self):
        return self.label

    def get_label2(self):
        return self.label2

    def set_type(self, type):
        self.type = type

    def get_type(self):
        return self.type

    def filter(self, flag):
        if not flag:
            return False
        if flag & self.get_type():
            return False
        return True
      
    def _add_pagination_node(self, Dir, lvl=1, whiteFlag=Flag.NODE):
        limit = qobuz.addon.getSetting('pagination_limit')
        from renderer.irenderer import IRenderer
        r = IRenderer(self.type, self.id)
        if self.pagination_next:
            colorItem = qobuz.addon.getSetting('color_item')
            params = qobuz.boot.params
            params['offset'] = self.pagination_next_offset
            params['nid'] = self.id
            node = r.import_node(self.type, params)
            label = self.get_label()
            if self.label2: label = self.label2
            #if self.parent: label = self.parent.label
            nextLabel = (
                '[ %s  %s / %s ]') % (color(colorItem, label),
                                      self.pagination_next_offset,
                                      self.pagination_total)
            node.label = nextLabel
            node.label2 = label
            self.add_child(node)
    
    # When returning False we are not displaying directory content
    def pre_build_down(self, xbmc_directory, lvl=1, whiteFlag=Flag.NODE):
        return True
    
    
    '''
        build_down:
        This method fetch data from cache recursively and build our tree
        Node without cached data don't need to overload this method
    '''

    def build_down(self, Dir, lvl=1, whiteFlag=Flag.NODE):
        if lvl != -1 and lvl < 1:
            return False
        if not self.pre_build_down(Dir, lvl, whiteFlag):
            return False
        self._build_down(Dir, lvl, whiteFlag)
        self._add_pagination_node(Dir, lvl, whiteFlag)
        if lvl != -1:
            lvl -= 1
        if Dir.is_canceled():
            return False
        total = len(self.childs)
        count = 0
        label = self.get_label()
        Dir.update(0, total, 'Working', label, '')
        for child in self.childs:
            if Dir.is_canceled():
                break
            if not (child.type & Flag.TRACK):
                Dir.update(
                    count, total, "Working", label, child.get_label())
            if child.type & whiteFlag:
                Dir.add_node(child)
            child.build_down(Dir, lvl, whiteFlag)
            count += 1
        return True

    '''
        _build_down:
        This method is called by build_down method, each object who
        inherit from node object can implement their own code. Lot of object
        simply fetch data from qobuz (cached data)
    '''
    def _build_down(self, xbmc_directory, lvl, flag):
        pass
    
    def attach_context_menu(self, item, menuItems=[]):
        colorItem = qobuz.addon.getSetting('color_item')

        if self.type & (Flag.PRODUCT | Flag.TRACK | Flag.ARTIST):
            artist_id = self.get_artist_id()
            artist_name = self.get_artist()
            urlArtist = self.make_url(type=Flag.ARTIST, id=artist_id)
            menuItems.append((formatControlLabel(artist_name), 
                              containerUpdate(urlArtist)))

            ''' Similar artist '''
            url = self.make_url(type=Flag.SIMILAR_ARTIST, 
                                id=artist_id, mode=Mode.VIEW)
            cmd = containerUpdate(url)
            label = '%s' % (color(colorItem, lang(39004)))
            menuItems.append((label, cmd))
        
        menuItems.append((formatControlLabel('General'), containerUpdate('')))

        ''' VIEW BIG DIR '''
        cmd = containerUpdate(self.make_url(mode=Mode.VIEW_BIG_DIR))
        menuItems.append((color(colorItem, lang(39002)), cmd))
      
        ''' ADD TO CURRENT PLAYLIST '''
        cmd = containerUpdate(self.make_url(type=Flag.PLAYLIST, 
                                            nm='add_to_current'))
        menuItems.append((color(colorItem, lang(39005)), cmd))

        if self.parent and not (self.parent.type & Flag.FAVORITES):
            ''' ADD TO FAVORITES '''
            cmd = runPlugin(self.make_url(mode=Mode.FAVORITES_ADD_TO_CURRENT))
            menuItems.append((color(colorItem, lang(39011)), cmd))

        ''' ADD AS NEW '''
        cmd = containerUpdate(self.make_url(type=Flag.PLAYLIST,
                                            nm='add_as_new', 
                                            qnt=self.type,
                                            query=self.get_label()))
        menuItems.append((color(colorItem, lang(30080)), cmd))

        ''' Show playlist '''
        if not (self.type & Flag.PLAYLIST):
            cmd = containerUpdate(self.make_url(type=Flag.USERPLAYLISTS))
            menuItems.append((color(colorItem, lang(39005)), cmd))

        if self.type & Flag.USERPLAYLISTS:
            ''' CREATE '''
            cmd = runPlugin(self.make_url(mode=Mode.PLAYLIST_CREATE))
            menuItems.append((color(colorItem, lang(39008)), cmd))

        ''' SCAN '''
        if qobuz.addon.getSetting('enable_scan_feature') == 'true':
            url = self.make_url(mode=Mode.SCAN)
            try:
                label = color(colorItem, lang(39003) + ": ") + \
                    self.get_label().decode('utf8', 'replace')
                menuItems.append(
                    (label, 'XBMC.UpdateLibrary("music", "%s")' % (url)))
            except:
                pass

        ''' ERASE CACHE '''
        colorItem = qobuz.addon.getSetting('color_item_caution')
        cmd = runPlugin(self.make_url(type=Flag.ROOT, nm="cache_remove"))
        menuItems.append((color(colorItem, lang(31009)), cmd))

        menuItems.append((formatControlLabel('System (i8n)'), containerUpdate(''))) 