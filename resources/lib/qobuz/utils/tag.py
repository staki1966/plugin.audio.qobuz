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

import xbmcgui
import xbmcaddon

from debug import warn, info, log
from constants import *


class IQobuzTag(object):
    
    def __init__(self, Core, json = None, parent = None):
        self.__valid_tags = None
        self.__is_loaded = None
        self._json = json
        self._parent = parent
        self.Core = Core
        self._childs = []
        
    def add_child(self, child):
        self._childs.append(child)
    
    def get_childs(self):
        return self._childs
    
    def get_core(self):
        return self.Core
    
    def get_parent(self):
        return self._parent
    
    def get_raw_data(self):
        return self._json
    
    def parse_json(self, json):
        assert("load_json must be overloaded")
    
    def set_valid_tags(self, tags):
        self.__valid_tags = tags
    
    def get_valid_tags(self):
        return self.__valid_tags
    
    def get(self, key):
        if not self.is_loaded():
            assert("Json is not loaded")
        if key not in self.__valid_tags:
            assert("Invalid tag: " + key)
        return self.__dict__[key]
    
    def set(self, key, value):
        if key not in self.__valid_tags:
            assert("Invalid tag:" + key)
        v = ''
        try:
            v = str(value)
        except:
            if isinstance(value, basestring):
                v = value.encode('utf8', 'ignore')
            elif isinstance(value, bool):
                if value: v = '1'
                else: v = '0'
        if v == 'None':
            return
        self.__dict__[key] = v
    
    def auto_parse_json(self, json):
        valid_tags = self.get_valid_tags()
        for tag in valid_tags:
            try:
                self.set(tag, json[tag])
            except:
                pass
                #warn(self, "Could not set tag: " + tag)
    
    def is_loaded(self):
        return self.__is_loaded
    
    def getTitle(self):
        v = ''
        try: v = self.title
        except: return ''
        return v
    
    def getArtistId(self):
        label = []
        try: 
            label.append(self.artist_id)
        except:
            try:
                label.append(self.interpreter_id)
            except: 
                try:
                    label.append(self.composer_id)
                except: label.append('N/A')
        return ''.join(label)
    
    def getGenre(self, sep = ''):
        genre = ''
        childs = self.get_childs()
        for c in childs:
            genre = c.getGenre(sep)
            if genre: return genre
        return genre
    
    def getImage(self, sep = ''):
        data = ''
        childs = self.get_childs()
        for c in childs:
            data = c.getImage(sep)
            if data: return data
        return data
    
    def getDate(self, sep = ''):
        data = ''
        childs = self.get_childs()
        for c in childs:
            data = c.getDate(sep)
            if data: return data
        return data

    def getAlbum(self, sep = ''):
        data = ''
        childs = self.get_childs()
        for c in childs:
            data = c.getAlbum(sep)
            if data: return data 
        return data
    
    def getAlbumId(self, sep = ''):
        data = ''
        childs = self.get_childs()
        for c in childs:
            data = c.getAlbumId(sep)
            if data: return data 
        return data
    
    def getArtist(self, sep = ''):
        data = ''
        childs = self.get_childs()
        for c in childs:
            data = c.getArtist(sep)
            if data: return data
        return data
    
    def getComposer(self, sep = ''):
        data = ''
        childs = self.get_childs()
        for c in childs:
            data = c.getComposer(sep)
            if data: return data
        return data

    def getInterpreter(self, sep = ''):
        data = ''
        childs = self.get_childs()
        for c in childs:
            data = c.getInterpreter(sep)
            if data: return data
        return data
    
    def getDuration(self, sep = ''):
        data = 0
        childs = self.get_childs()
        for c in childs:
            data = c.getDuration(sep) 
            if data: return data
        return data
    
    def getTitle(self, sep = ''):
        data = ''
        childs = self.get_childs()
        for c in childs:
            data = c.getTitle(sep) 
            if data: return data
        return data
    
    def getXbmcItem(self):
        date = 0
        try:
            date = self.getDate('#').split('#')[0]
        except: data = 0
        year = 0
        if date:
            try:
                year = date.split('-')[0]
            except: pass
        genre = ''
        if self.get_parent():
            genre = self.get_parent().getGenre()
        else: genre = self.getGenre()
        i = xbmcgui.ListItem(self.getTitle())
        i.setInfo(type='music', infoLabels = {
                                             'title': self.getTitle(),
                                             'artist': self.getArtist(),
                                             'genre': self.getGenre(),
                                             'album': self.getAlbum(),
                                             'year': int(year),
                                             'comment': 'Qobuz Music Streaming (qobuz.com)'
                                             })
        image = self.getImage()
        if image:
            i.setThumbnailImage(image)
            i.setIconImage(image)
        return i
'''
'''
class QobuzTagUserPlaylist(IQobuzTag):
    
    def __init__(self, Core, json):
        super(QobuzTagUserPlaylist, self).__init__(Core, json)
        self.set_valid_tags(['id', 'name', 'description', 'position', 
                             'created_at', 'updated_at', 'is_public', 
                             'is_collaborative', 'owner_id', 'owner_name', 'length'])
        if json:
            self.parse_json(json)
    
    def parse_json(self, p):
        self.set('id', p['id'])
        self.set('name', p['name'])
        self.set('description', p['description'])
        try:
            self.set('position', p['position'])
        except: pass
        try:
            self.set('created_at', p['created_at'])
        except: pass
        try:
            self.set('updated_at', p['updated_at'])
        except: pass
        self.set('is_public', p['is_public'])
        self.set('is_collaborative', p['is_collaborative'])
        self.set('owner_id', p['owner']['id'])
        self.set('owner_name', p['owner']['name'])
        try:
            p['length']
            self.set('length', p['length'])
        except:
            self.set('length', '-1')
        self._is_loaded = True

class QobuzTagArtist(IQobuzTag):
    
    def __init__(self, Core, json, parent = None):
        super(QobuzTagArtist, self).__init__(Core, json, parent)
        self.set_valid_tags(['id', 'name'])
        self.__album = None
        if json:
            self.parse_json(json)

    def parse_json(self, p):
        self.auto_parse_json(p)


    def getArtist(self, sep = ''):
        try: return self.name
        except: return ''        
        
    def getArtistId(self, sep = ''):
        try: return self.id
        except: return ''
'''
'''
class QobuzTagAlbum(IQobuzTag):
    
    def __init__(self, Core, json):
        super(QobuzTagAlbum, self).__init__(Core, json)
        self.set_valid_tags(['id', 'title', 'genre', 'label', 
                             'release_date', 'released_at'])
        if json:
            self.parse_json(json)
    
    def parse_json(self, p):
        self.auto_parse_json(p)
        if 'image' in p:
            image = QobuzTagImage(self.get_core(), p['image'])
            self.add_child(image)
        if 'label' in p:
            label = QobuzTagLabel(self.get_core(), p['label'])
            self.add_child(label)
        if 'genre' in p:
            genre = QobuzTagGenre(self.get_core(), p['genre'])
            self.add_child(genre)
        
        self._is_loaded = True
        
    def getAlbum(self, sep = ''):
        try:
            return self.title
        except: return ''
    
    def getAlbumId(self, sep = ''):
        try:
            return self.id
        except: return ''
    
    def getTitle(self, sep = ''):
        try: return self.title
        except: return ''
        
    def getDate(self, sep = ''):
        try:
            return self.release_date
        except:
            try: 
                return self.released_date
            except:
                return ''
    def getId(self, sep = ''):
        try: 
            return self.id
        except:
            return ''        

'''
'''
class QobuzTagProduct(IQobuzTag):
    
    def __init__(self, Core, json, parent = None):
        super(QobuzTagProduct, self).__init__(Core, json, parent)
        self.set_valid_tags(['id', 'artist', 'genre', 'description', 
                            'label', 'price', 'release_date', 'relevancy', 
                            'title', 'type', 'url', 'subtitle', 'goodies', 
                            'release_date', 'awards', 'url', 'added_date', 'length'
                            'added_date'])
        self.__tracks__ = None
        if json:
            self.parse_json(json)

        
    def get_tracks(self):
        return self.__tracks__
    
    def getXbmcItem(self):
        i = super(QobuzTagProduct, self).getXbmcItem()
        genre = self.getGenre()
        if genre:
            genre = ' [' + genre + ']'
        i.setLabel(self.getArtist() + ' - ' + self.getTitle() + genre)
        i.setInfo(type = 'music', infoLabels = {
                                               'album': self.getAlbum()
                                               })
        
        return i
    
    def getAlbum(self, sep =''):
        album = ''
        try: return self.Subtitle
        except: 
            for c in self.get_childs():
                album += c.getAlbum(sep)
                if sep: album += sep
        return album
    
    def getAlbumId(self, sep =''):
        albumid = ''
        try: return self.id
        except: 
            for c in self.get_childs():
                albumid += c.getAlbumId(sep)
                if sep: albumid += sep
        return albumid
                
    def getArtist(self, sep = ''):
        try: return self.artist
        except:
            for c in self.get_childs():
                artist = c.getArtist(sep)
                if artist: return artist
        return artist
    
    def getGenre(self, sep = ''):
        genre = super(QobuzTagProduct, self).getGenre()
#        for c in self.get_childs():
#            genre += c.getGenre(sep)
#        if sep: genre += sep
        if not genre:
            try: genre = self.genre
            except : pass
        return genre
    
    def getDate(self, sep = 0):
        try: 
            return self.release_date
        except: return ''
        
    def getTitle(self, sep = ''):
        try: return self.title
        except: return ''
        
    def getAlbum(self, sep = ''):
        album = ''
        try: return self.title
        except:
            for c in self.get_childs():
                album += c.getAlbum(sep)
                if sep: album += sep
        return album

    def getAlbumId(self, sep = ''):
        albumid = ''
        try: return self.id
        except:
            for c in self.get_childs():
                albumid += c.getAlbumId(sep)
                if sep: albumid += sep
        return albumid
    
    def parse_json(self, p):
        self.auto_parse_json(p)
        if 'image' in p:
            self.add_child(QobuzTagImage(self.Core, p['image'], self))
        if 'genre' in p:
            genre = ''
            tag = QobuzTagGenre(self.Core, p['genre'], self)
            genre = tag.getGenre()
            if genre:
                self.add_child(tag)
        if 'artist' in p:
            artist = ''
            tag = QobuzTagArtist(self.Core, p['artist'], self)
            artist = tag.getArtist()
            if artist:
                self.add_child(tag)
                if self.artist:
                    del self.__dict__['artist']

        if 'tracks' in p:
            for track in p['tracks']:
                self.add_child(QobuzTagTrack(self.Core, track, self))
        self._is_loaded = True
        

class QobuzTagInterpreter(IQobuzTag):
    def __init__(self, Core, json, parent = None):
        super(QobuzTagInterpreter, self).__init__(Core, json, parent = None)
        self.set_valid_tags(['name', 'id'])
        if json:
            self.auto_parse_json(json)

    def getInterpreter(self, sep = ''):
        try: return self.name
        except: return ''

class QobuzTagComposer(IQobuzTag):
    def __init__(self, Core, json, parent = None):
        super(QobuzTagComposer, self).__init__(Core, json, parent = None)
        self.set_valid_tags(['name', 'id'])
        self.parent = None
        if json:
            self.auto_parse_json(json)
        
    def getComposer(self, sep = ''):
        try: return self.name
        except: return ''

class QobuzTagGenre(IQobuzTag):
    def __init__(self, Core, json, parent = None):
        super(QobuzTagGenre, self).__init__(Core, json, parent = None)
        self.set_valid_tags(['name', 'id'])
        self.parent = None
        if json:
            self.auto_parse_json(json)
            
    def getGenre(self, sep = ''):
        try:
            if self.name == 'None':
                return '' 
            return self.name
        except: return ''

class QobuzTagLabel(IQobuzTag):
    def __init__(self, Core, json, parent = None):
        super(QobuzTagLabel, self).__init__(Core, json, parent = None)
        self.set_valid_tags(['name', 'id'])
        self.parent = None
        if json:
            self.auto_parse_json(json)

class QobuzTagImage(IQobuzTag):
    def __init__(self, Core, json, parent = None):
        super(QobuzTagImage, self).__init__(Core, json, parent = None)
        self.set_valid_tags(['large', 'small', 'thumbnail'])
        self.parent = None
        if json:
            self.auto_parse_json(json)
            
    def getImage(self, sep = ''):
        try: return self.large
        except:
            try: return self.small
            except:
                try: return self.thumbnail
                except: return ''
'''
'''
class QobuzTagTrack(IQobuzTag):
    
    def __init__(self, Core, json, parent = None):
        super(QobuzTagTrack, self).__init__(Core, json, parent)
        self.set_valid_tags(['playlist_track_id', 'position', 'id', 'title', 
                             'track_number', 'media_number', 'duration',
                             'created_at', 'streaming_type'])
        self.parent = None
        if json:
            self.parse_json(json)

    def getLabel(self):
        label = []
        label.append(self.track_number)
        label.append(' - ')
        label.append(self.getArtist())
        label.append(' - ')
        label.append(self.title)
        return ''.join(label)

    def parse_json(self, p):
        self.auto_parse_json(p)
        if 'album' in p:
            data = QobuzTagAlbum(self.get_core(), p['album'])
            self.add_child( data )
        if 'interpreter' in p:
            data = QobuzTagInterpreter(self.get_core(), p['interpreter'])
            self.add_child( data )
        if 'composer' in p:
            data = QobuzTagComposer(self.get_core(), p['composer'])
            self.add_child( data )
        if 'image' in p:
            print "Add image to child"
            data = QobuzTagImage(self.get_core(), p['image'])
            self.add_child( data )
            
        self._is_loaded = True

    def getDuration(self, sep = 0):
        try:
            (sh,sm,ss) = self.duration.split(':')
        except:
            return 0
        return (int(sh) * 3600 + int(sm) * 60 + int(ss))

    def getTrackNumber(self, sep = ''):
        try: return int(self.track_number)
        except: return 0

    def getTitle(self, sep = ''):
        try: return self.title
        except: return ''

    def getArtist(self, sep = ''):
        artist = ''
        artist = self.getInterpreter()
        if artist:
            return artist
        return self.getComposer()

    def getAlbum(self, sep = ''):
        album = super(QobuzTagTrack, self).getAlbum(sep)
        parent = self.get_parent()
        if not album and parent:
            try:
                album = parent.title
            except: pass
        return album

    def getAlbumId(self, sep = ''):
        albumid = super(QobuzTagTrack, self).getAlbumId(sep)
        parent = self.get_parent()
        if not albumid and parent:
            albumid = parent.id
        return albumid

    def getStreamingType(self, sep = ''):
        try: return self.streaming_type
        except: return ''

    def getXbmcItem(self, context = 'album'):
        parent = self.get_parent()
        i = xbmcgui.ListItem()
        album = self.getAlbum()
        artist = self.getArtist()
        track_number = self.getTrackNumber()
        date = ''
        if parent: date = parent.getDate()
        else: date = self.getDate()
        year = 0
        if date:
            try:
                year = date.split('-')[0]
            except: pass
        genre = ''
        try: genre = parent.getGenre()
        except: genre = self.getGenre()
            
        image = self.getImage()  
        if not image and parent: 
            image = parent.getImage()

        title = self.getTitle()
        duration = self.getDuration()
        label = ''
        if context == 'album':
            label = str(track_number) + ' - ' + artist + ' - '  + title
        elif context == 'playlist': 
            label = artist + ' - ' + title
        elif context == 'songs': 
            label = album + ' - ' + artist + ' - ' + title
        elif context == 'player':
            label = str(track_number) + ' - ' + artist + ' - '  + title
        else:
            raise "Unknown display context"
        if self.getStreamingType() != 'full':
            label =  '[COLOR=FF555555]' + label + '[/COLOR] [[COLOR=55FF0000]Sample[/COLOR]]'

        i.setLabel(label)
        i.setInfo(type = 'music',
                  infoLabels = {'songid': str(self.id),
                                'title': title,
                                'artist': artist,
                                'genre': genre,
                                'tracknumber': track_number,
                                'album': album,
                                'duration': duration,
                                'year': int(year),
                                'comment': 'Qobuz Music Streaming Service'
                                })
        if context != 'player':
            i.setProperty('IsPlayable', 'true')
            i.setProperty('Music', 'true')
        else:
            i.setProperty('IsPlayable', 'true')
            i.setProperty('Music', 'true')
        i.setThumbnailImage(image)
        i.setIconImage(image)
        i.setProperty('image', image)
        '''
            Context Menu
        '''
#        #b = self.Core.Bootstrap
#        retstr = sys.argv[2]
#        go = 'http://plugin.audio.qobuz/?mode='+MODE_ARTIST+'&id='+self.getArtistId()
#        albumfromthisartist= ('Show albums from this artist', 'ActivateWindow(Music,'+go+','+retstr+')')
#        i.addContextMenuItems([albumfromthisartist], False)
        return i

'''
'''
class QobuzTagPlaylist(IQobuzTag):
    def __init__(self, Core, json, parent = None):
        super(QobuzTagPlaylist, self).__init__(Core, json, parent)
        self.set_valid_tags([])
        if json:
            self.parse_json(json)
    
    def parse_json(self, p):
        for track in p['tracks']:
            self.add_child(QobuzTagTrack(self.Core, track, self))
        self._is_loaded = True

'''
'''
class QobuzTagSearch(IQobuzTag):
    
    def __init__(self, Core, json):
        super(QobuzTagSearch, self).__init__(Core, json)
        self.__tracks__ = []
        if json:
            self.parse_json(json)
        
    def parse_json(self, p):
        for track in p['tracks']:
            self.add_child(QobuzTagTrack(self.get_core(), track, self))
        self._is_loaded = True
