'''
    boot
    ~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from xbmcpy.plugin import Plugin
from qobuz.node import getNode, Flag
from qobuz.cache import cache
from qobuz.api import api
from qobuz.xbmc import settings, ItemFactory
"""Main
"""
import os
plugin = Plugin('plugin.audio.qobuz')
profile = plugin.profile()
cache.base_path = os.path.join(profile, 
                               plugin.plugin_id, 'cache')
api.pagination_limit = int(settings['pagination_limit'])
api.login(settings['username'],
          settings['password'])

import xbmc  # @UnresolvedImport
from qobuz.xbmc.renderer import XbmcRenderer
from qobuz.xbmc.commander import QobuzXbmcCommander
from qobuz.xbmc.player import Player
renderer = XbmcRenderer(plugin,
                        QobuzXbmcCommander(Flag, getNode),
                        ItemFactory(),
                        Player(plugin=plugin))
#except Exception as e:
#    from node.renderer.console import ConsoleRenderer, ItemFactory
#    renderer = ConsoleRenderer()
#    renderer.itemFactory = ItemFactory()
#    renderer.whiteFlag = Flag.ALL & ~Flag.TRACK

#while renderer.alive:
renderer.render(plugin.route(Flag, getNode))
#        renderer.ask()

cache.delete_old()