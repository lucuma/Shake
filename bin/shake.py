# -*- coding: utf-8 -*-
"""
    shake script
    ----------------------------------------------

    Scrip to create a project skeleton.

    :copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
    :license: BSD. See LICENSE for more details.

"""
import os, errno
import optparse


PUBLIC_DIR = 'public'
TESTS_DIR = 'tests'
APP_DIR = 'web'

CSS_DIR = 'css'
JS_DIR = 'js'
IMAGES_DIR = 'images'
VIEWS_DIR = 'views'



def make_dirs(*lpath):
    path = os.path.join(*lpath)
    try:
        os.makedirs(path)
    except (OSError), e:
        if e.errno != errno.EEXIST:
            raise
    return path


def make_file(lpath, content, wm='w'):
    path = os.path.join(*lpath)
    if os.path.exists(path):
        raise ValueError('File `%s` already exists' % path)
    f = open(path, wm)
    try:
        f.write(content)
    finally:
        f.close()


def make_project_skeleton(pathname):
    rp, name = os.path.split(pathname)

    path = make_dirs(pathname)
    make_file([path, 'manage.py'], '')
    
    path = make_dirs(pathname, TESTS_DIR)
    make_file([path, '__init__.py'], '')
    
    path = make_dirs(pathname, PUBLIC_DIR)
    make_file([path, 'robots.txt'], '')
    path = make_dirs(pathname, PUBLIC_DIR, CSS_DIR)
    make_file([path, name + '.css'], '')
    path = make_dirs(pathname, PUBLIC_DIR, JS_DIR)
    make_file([path, name + '.js'], '')
    path = make_dirs(pathname, PUBLIC_DIR, IMAGES_DIR)

    path = make_dirs(pathname, APP_DIR)
    make_file([path, '__init__.py'], '')
    make_file([path, 'app.py'], '')
    make_file([path, 'urls.py'], '')
    make_file([path, 'settings.py'], '')
    make_file([path, 'models.py'], '')
    
    path = make_dirs(pathname, APP_DIR, VIEWS_DIR)
    make_file([path, 'index.html'], '')


if __name__ == '__main__':
    parser = optparse.OptionParser()
    (opts, args) = parser.parse_args()
    make_project_skeleton(args[0])

