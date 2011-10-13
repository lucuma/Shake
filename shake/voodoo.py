#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Voodoo
    ----------------------------------------------
    Reanimate an application skeleton and put it at your service.
    
    :Copyright © 2010-2011 by Lúcuma labs (http://lucumalabs.com).
    :MIT License. (http://www.opensource.org/licenses/mit-license.php)

"""
import datetime
import errno
import hashlib
import os
import re

import jinja2
from .pyceo import Manager, formatm


manager = Manager()
ROOTDIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),
    'skeleton')
FILTER = ('.pyc', '.DS_Store', '.pyo')
TABSPACE = ' '*5


def make_secret():
    return hashlib.sha1(os.urandom(64)).hexdigest()


def make_dirs(*lpath):
    path = os.path.join(*lpath)
    try:
        os.makedirs(os.path.dirname(path))
    except (OSError), e:
        if e.errno != errno.EEXIST:
            raise
    return path


def make_project_skeleton(pathname, skeleton, env_options):
    print 'Using skeleton:', skeleton
    ppath, pname = os.path.split(pathname)
    print '\n   %s/' % pathname

    jinja_loader = jinja2.FileSystemLoader(skeleton)
    env_options = env_options or {}
    env_options.setdefault('loader', jinja_loader)
    env_options.setdefault('block_start_string', '<%')
    env_options.setdefault('block_end_string', '%>')
    env_options.setdefault('variable_start_string', '<=')
    env_options.setdefault('variable_end_string', '=>')
    env_options.setdefault('autoescape', False)
    jinja_env = jinja2.Environment(**env_options)
    data = {
        'PNAME': pname,
        'SECRET1': make_secret(),
        'SECRET2': make_secret(),
        'PS': os.path.sep,
        'NOW': datetime.datetime.utcnow(),
    }

    for folder, subs, files in os.walk(skeleton):
        ffolder = os.path.relpath(folder, skeleton)
        
        for filename in files:
            if filename.endswith(FILTER):
                continue
            src_path = os.path.join(folder, filename)
            f = open(src_path, 'rb')
            content = f.read()
            f.close()
            
            if filename.endswith('.tmpl'):
                if not isinstance(content, unicode):
                    content = unicode(content, 'utf-8')
                filename = re.sub(r'\.tmpl$', '', filename)
                tmpl = jinja_env.from_string(content)
                content = tmpl.render(data).encode('utf-8')
            filename = re.sub(r'%PNAME%', pname, filename)
            
            print formatm(TABSPACE + 'create  ', 
                os.path.join(ffolder, filename).lstrip('./'), 'OKGREEN')
            
            final_path = make_dirs(pathname, ffolder, filename)
            f = open(final_path, 'wb')
            f.write(content)
            f.close()


@manager.command
def new(pathname, skeleton=ROOTDIR, **env_options):
    """APP_PATH [SKELETON_PATH]
    
    The 'shake new' command creates a new Shake application with a default
    directory structure at the path you specify.

    Example:
        shake new ~/Projects/wiki
    
    By default it uses Shake's built-in skeleton, but you can provide a custom
    one if you want.
    """
    pathname = pathname.rstrip(os.path.sep)
    make_project_skeleton(pathname, skeleton, env_options)

    msg = ['\n',
        TABSPACE, 'Now run\n', TABSPACE, 
        formatm(''.join(['  pip install -r ', pathname,
            os.path.sep, 'requirements.txt']), '\n', color='BOLD'),
        TABSPACE, 'to finish installing your application requirements.\n']
    print ''.join(msg)


def main():
    manager.run()


if __name__ == "__main__":
    main()
