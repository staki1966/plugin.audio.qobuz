import os
from os import path as P
from flask import Flask
from flask import request
from qobuz.api import api
from qobuz.application import Application as QobuzApplication
from qobuz.cache import cache
from flask import Response, redirect
from qobuz import base_path
from qobuz.plugin import Plugin
from qobuz.bootstrap import MinimalBootstrap
from qobuz import debug
qobuzApp = QobuzApplication(Plugin('plugin.audio.qobuz'),
                            bootstrapClass=MinimalBootstrap)
qobuzApp.bootstrap.init_app()
debug.info(None, 'Username %s Password %s' % (qobuzApp.registry.get('username'),
                                   qobuzApp.registry.get('password')))
api.login(username=qobuzApp.registry.get('username'),
          password=qobuzApp.registry.get('password'))


application = Flask(__name__)

from qobuz.gui.util import getSetting
from werkzeug import exceptions
from flask import make_response, render_template
from functools import wraps, update_wrapper
from datetime import datetime

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)

def http_error(name):
    return getattr(exceptions, name)()

def get_format_id(default=3):
    stream_type = getSetting('streamtype')
    if stream_type == 'flac':
        return 5
    elif stream_type == 'mp3':
        return 3
    return default

def shutdown_server():
    debug.info(__name__, 'Shutting down server')
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@nocache
@application.route('/qobuz/album/<int:album_id>/track/<int:track_id>/file.mpc', methods=['HEAD'])
def route_track_head(album_id=None, track_id=None):
    response = api.get('/track/getFileUrl',
                       format_id=get_format_id(),
                       track_id=track_id)
    if response is None or 'url' not in response:
        return http_error('NotFound')
    return 'ok', 200

@nocache
@application.route('/qobuz/album/<int:album_id>/track/<int:track_id>/file.mpc', methods=['GET'])
def route_track(album_id=None, track_id=None):
    response = api.get('/track/getFileUrl',
                       format_id=get_format_id(),
                       track_id=track_id)
    if response is None or 'url' not in response:
        return http_error('NotFound')
    return redirect(response['url'], code=302)

@application.route('/<path:path>')
def sniff(path=None):
    debug.info(__name__, 'Request[{}] {}', request.method, path)
    return http_error('NotFound')

@nocache
@application.route('/qobuz/album/<int:album_id>/track/<int:track_id>/album.nfo', methods=['HEAD'])
def route_track_head(album_id=None, track_id=None):
    response = api.get('/album/get', album_id=album_id)
    if response is None or 'url' not in response:
        return http_error('NotFound')
    debug.info(__name__, 'Response: {}', response)
    return render_template('tpl/album.nfo.tpl', entries=response)
#  CCurlFile::Exists - Failed: Couldn't connect to server(7) for http://127.0.0.1:33574/qobuz/track/disc.png
# 23:23:34 T:123145335918592   ERROR: CCurlFile::Exists - Failed: Couldn't connect to server(7) for http://127.0.0.1:33574/qobuz/track/cdart.png
# 23:23:34 T:123145335918592   ERROR: CCurlFile::Exists - Failed: Couldn't connect to server(7) for http://127.0.0.1:33574/qobuz/album.nfo
