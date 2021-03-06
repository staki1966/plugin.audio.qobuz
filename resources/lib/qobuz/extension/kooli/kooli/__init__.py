'''
    qobuz.extension.kooli
    ~~~~~~~~~~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2018 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from os import path as P
import logging
import os
import sys
kooli_path = P.abspath(P.join(P.dirname(__file__)))
base_path = P.join(kooli_path, P.pardir)
qobuz_lib_path = P.abspath(P.join(base_path, P.pardir, P.pardir, P.pardir))
try:
    import qobuz
except ImportError:
    sys.path.append(qobuz_lib_path)
log_dir = P.join(qobuz_lib_path, 'qobuz', '__data__', 'log')
if not P.exists(log_dir):
    os.makedirs(log_dir)
log_file = P.join(log_dir, 'extension-kooli.log')
logging.basicConfig(filename=log_file)
log = logging.getLogger('kooli')
