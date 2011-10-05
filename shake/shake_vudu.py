#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Shake vudu
    ----------------------------------------------
    Reanimate an skeleton, just for your project!
    
    :Copyright © 2010-2011 by Lúcuma labs (http://lucumalabs.com).
    :MIT License. (http://www.opensource.org/licenses/mit-license.php)

"""
import hashlib
import errno
import os
import re

from shake import manager


ROOTDIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),
    'skeleton')
FILTER = ('.pyc', '.DS_Store', '.pyo')
TABSPACE = ' '*5

class Colors(object):
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'


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


def replace_vars(text, data):
    for key, value in data.items():
        text = re.sub(key, value, text)
    return text


def make_project_skeleton(pathname, skeleton):
    print 'Using skeleton:', skeleton

    ppath, pname = os.path.split(pathname)
    data = {
        r'<%PNAME%>': pname,
        r'<%SECRET1%>': make_secret(),
        r'<%SECRET2%>': make_secret(),
    }
    
    print '\n   %s/' % pathname

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
                filename = re.sub(r'\.tmpl$', '', filename)
                content = replace_vars(content, data)
            filename = re.sub(r'%PNAME%', pname, filename)
            
            msg = [Colors.OKGREEN, TABSPACE, 'create  ', Colors.ENDC,
                os.path.join(ffolder, filename).lstrip('./')]
            print ''.join(msg)
            
            final_path = make_dirs(pathname, ffolder, filename)
            f = open(final_path, 'wb')
            f.write(content)
            f.close()


@manager.command
def new(pathname, skeleton=ROOTDIR):
    """PATH
    Create a new project skeleton
    """
    pathname = pathname.rstrip(os.path.sep)
    make_project_skeleton(pathname, skeleton)

    msg = ['\n',
        TABSPACE, 'Now run\n',
        TABSPACE, Colors.BOLD, '  pip install -r ', 
        pathname, os.path.sep, 'requirements.txt', Colors.ENDC, '\n',
        TABSPACE, 'to finish installing the project requirements.\n']
    print ''.join(msg)


def main():
    manager.run()


if __name__ == "__main__":
    main()
