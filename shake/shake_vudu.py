#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    shake vudu
    ----------------------------------------------
    Reanimate an skeleton, just for your project!
    
    :copyright © 2010-2011 by Lúcuma labs (http://lucumalabs.com).
    :license: BSD. See LICENSE for more details.

"""
import hashlib
import errno
import optparse
import os
import re


ROOTDIR = os.path.join(os.path.dirname(__file__), 'skeleton')
FILTER = ('.pyc', '.DS_Store', '.pyo')


class Colors(object):
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
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


def make_project_skeleton(pathname):
    ppath, pname = os.path.split(pathname)
    data = {
        r'<%PNAME%>': pname,
        r'<%SECRET1%>': make_secret(),
        r'<%SECRET2%>': make_secret(),
    }
    
    print '   %s/' % pathname
    
    for folder, subs, files in os.walk(ROOTDIR):
        ffolder = os.path.relpath(folder, ROOTDIR)
        
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
            
            msg = [Colors.OKGREEN, ' '*5, 'create  ', Colors.ENDC,
                os.path.join(ffolder, filename).lstrip('./')]
            print ''.join(msg)
            
            final_path = make_dirs(pathname, ffolder, filename)
            f = open(final_path, 'wb')
            f.write(content)
            f.close()


def main():
    parser = optparse.OptionParser()
    (opts, args) = parser.parse_args()
    pathname = args[0].rstrip(os.path.sep)
    make_project_skeleton(pathname)


if __name__ == '__main__':
    main()
