'''
    qobuz.node.album
    ~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from inode import INode
from qobuz.debug import warn
#from xbmcpy.util import getImage, getSetting, htm2xbmc
from qobuz.api import api
from qobuz.node import getNode, Flag
from qobuz.i8n import _
from qobuz.settings import settings

SPECIAL_PURCHASES = ['0000020110926', '0000201011300', '0000020120220',
                     '0000020120221']

class Node_album(INode):
    '''
        @class Node_product:
    '''
    def __init__(self, parameters={}):
        super(Node_album, self).__init__(parameters)
        self.kind = Flag.ALBUM
        self.image = ''
        self.content_type = 'songs'
        self.is_special_purchase = False
        self.offset = None
        self.imageDefaultSize = 'large'
        self.label = _('Album')
        self.imageDefaultSize = settings.get('image_size_default')

    def fetch(self, renderer=None):
        data = api.get('/album/get', album_id=self.nid)
        if not data:
            warn(self, "Cannot fetch product data")
            return False
        self.data = data
        return True

    def populate(self, renderer=None):
        for track in self.data['tracks']['items']:
            node = getNode(Flag.TRACK, self.parameters)
            if not 'image' in track:
                track['image'] = self.get_image()
            node.data = track
            
            self.append(node)
        return len(self.data['tracks']['items'])

    def url(self, **ka):
#        if 'asLocalURL' in ka and ka['asLocalURL']:
#            from constants import Mode
#            ka['mode'] = Mode.SCAN
        return super(Node_album, self).url(**ka)

#    def makeListItem(self, replaceItems=False):
#        import xbmc, xbmcgui
#        image = self.get_image()
#        thumb = xbmc.getCacheThumbName(image)
#        item = xbmcgui.ListItem(
#            label=self.get_label(),
#            label2=self.get_label(),
#            iconImage=image,
#            thumbnailImage=image,
#            path=self.make_url(),
#        )
#        item.setInfo('music', infoLabels={
#            'genre': self.get_genre(),
#            'year': self.get_year(),
#            'artist': self.get_artist(),
#            'title': self.get_title(),
#            'album': self.get_title(),
#            'comment': self.get_description()
#        })
#        ctxMenu = contextMenu()
#        self.attach_context_menu(item, ctxMenu)
#        item.addContextMenuItems(ctxMenu.getTuples(), replaceItems)
#        return item

    '''
    PROPERTIES
    '''
    def get_artist(self):
        return self.get_property(['artist/name',
                               'interpreter/name', 
                               'composer/name'])

    def get_album(self):
        album = self.get_property('name')
        if not album:
            return ''
        return album

    def get_artist_id(self):
        return self.get_property(['artist/id',
                               'interpreter/id',
                              'composer/id'])

    def get_title(self):
        return self.get_property('title')

    def get_image(self, size = None):
        if not size:
            size = self.imageDefaultSize
        return self.get_property(['image/%s' % (size),
                                   'image/large', 
                                   'image/small',
                                   'image/thumbnail'])

    def get_label(self):
        artist = self.get_artist() or 'VA'
        label = '%s - %s' % (artist, self.get_title())
        return label

    def get_genre(self):
        return self.get_property('genre/name')

    def get_year(self):
        import time
        date = self.get_property('released_at')
        year = 0
        try:
            year = time.strftime("%Y", time.localtime(date))
        except:
            pass
        return year

    def get_description(self):
        return self.get_property('description')
