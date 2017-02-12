'''
    qobuz.node.user
    ~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import xbmcgui
import time
from qobuz.node.inode import INode
from qobuz import debug
from qobuz.gui.util import getImage
from qobuz.gui.contextmenu import contextMenu
from qobuz.api import api
from qobuz.node import getNode, Flag
from qobuz.api.user import current as user
from qobuz import config
from qobuz.theme import color


class Node_user(INode):
    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_user, self).__init__(
            parent=parent, parameters=parameters, data=data)
        self.nt = Flag.USER
        self.content_type = 'artists'
        self.is_folder = True
        self.data = self.fetch()

    def get_label(self):
        return u'[{subscription} - {login}]'.format(
            login=user.get_property(
                'user/login', default='Demo'),
            country=user.get_property('user/country_code'),
            lang=user.get_property('user/language_code'),
            subscription=user.get_property(
                'user/credential/description', default='Free'))

    def get_image(self):
        return user.get_property('user/avatar')

    def fetch(self, *a, **ka):
        return user.data

    def populate(self, *a, **ka):
        self.add_child(getNode(Flag.TESTING))

    def get_description(self):
        return u'''[{credential_description}]
- label: {credential_label}
- lossy_streaming: {lossy_streaming}
- offline streaming: {offline_streaming}
- mobile streaming: {mobile_streaming}
- lossless streaming: {lossless_streaming}
'''.format(
            credential_label=color(
                self.get_property(
                    'user/credential/parameters/color_scheme/logo',
                    default='#0000FF00',
                    to='color'),
                self.get_property('user/credential/label')),
            credential_description=self.get_property(
                'user/credential/description'),
            lossy_streaming=self.get_property(
                'user/credential/parameters/lossy_streaming'),
            offline_streaming=self.get_property(
                'user/credential/parameters/offline_streaming'),
            mobile_streaming=self.get_property(
                'user/credential/parameters/mobile_streaming'),
            lossless_streaming=self.get_property(
                'user/credential/parameters/lossless_streaming'))

    def makeListItem(self, replaceItems=False):
        item = xbmcgui.ListItem(self.get_label(),
                                self.get_label2(),
                                self.get_image(), self.get_image(), None)
        if not item:
            debug.warn(self, 'Error: Cannot make xbmc list item')
            return None
        item.setInfo(
            'Music', infoLabels={'artist': user.get_property('user/login')})
        item.setProperty('artist_description', self.get_description())
        return item