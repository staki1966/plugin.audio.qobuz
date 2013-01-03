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
import urllib
import time

import xbmcplugin
import xbmcgui
import xbmc

from constants import *
from debug import *
from debug import __debugging__

import qobuz


class Progress(xbmcgui.DialogProgress):

    def __init__(self, active=True):
        self.active = active
        if self.active:
            super(Progress, self).__init__()
        self.line1 = 'Working...'
        self.line2 = ''
        self.line3 = ''
        self.percent = 0
        self.started_on = None

    def create(self, line1, line2='', line3=''):
        self.line1 = line1
        self.line2 = line2
        self.line3 = line3
        if not self.active:
            return False
        self.started_on = time.time()
        try:
            return super(Progress, self).create(line1, line2, line3)
        except:
            warn(self, "Cannot create progress bar")
            return False

    def _pretty_time(self, time):
        hours = (time / 3600)
        minutes = (time / 60) - (hours * 60)
        seconds = time % 60
        return '%02i:%02i:%02i' % (hours, minutes, seconds)

    def update(self, percent, line1, line2='', line3=''):
        if line1:
            self.line1 = line1
        self.line2 = line2
        self.line3 = line3
        if not self.active:
            return False
        elapsed = self._pretty_time((time.time() - self.started_on))
        try:
            return super(Progress, self).update(percent,
                                                '[%s] %s' % (elapsed, line1),
                                                line2, line3)
        except:
            warn(self, "Cannot update progress bar")
            return False

    def update_line1(self, line):
        if not line or line == self.line1:
            return False
        self.line1 = line
        try:
            return self.update(self.percent, self.line1, self.line2, self.line3)
        except:
            warn(self, "Cannot update line1 progress bar")
            return False
    def onAction(self, key):
        print "onKey(%s)" % (repr(key))
        
    def iscanceled(self):
        if not self.active:
            return True
        bs = True
        try:
            bs = super(Progress, self).iscanceled()
        except:
            warn(self, 'Cannot cancel progress...')
            return True
        return bs
   
    def close(self):
        if not self.active:
            return False
        try:
            return super(Progress, self).close()
        except:
            warn(self, "Cannot close progress bar")
            return False
