#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# shake.scripts

Command-line scripts


--------------------------------
Copyright © 2010-2011 by Lúcuma labs (http://lucumalabs.com).

MIT License. (http://www.opensource.org/licenses/mit-license.php).

"""
import hashlib
import os

from pyceo import Manager, formatm
import voodoo


manager = Manager()

ROOTDIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),
    'skeleton')

ENV_OPTIONS = {
    'autoescape': False,
    'block_start_string': '[%',
    'block_end_string': '%]',
    'variable_start_string': '[[',
    'variable_end_string': ']]',
}

FILTER = ('.pyc', '.DS_Store', '.pyo')

TABSPACE = ' ' * 5


def make_secret():
    return hashlib.sha1(os.urandom(64)).hexdigest()


@manager.command
def new(app_path, skeleton=ROOTDIR):
    """APP_PATH [SKELETON_PATH]
    
    The 'shake new' command creates a new Shake application with a default
    directory structure at the path you specify.

    Example:
        shake new projects/wiki
    
    By default it uses Shake's built-in skeleton, but you can provide a custom
    one if you want.
    """
    app_path = app_path.rstrip(os.path.sep)
    data = {
        'SECRET1': make_secret(),
        'SECRET2': make_secret(),
        'PS': os.path.sep,
    }
    env_options = ENV_OPTIONS.copy()

    vodoo.reanimate_skeleton(skeleton, app_path, data=data,
        filter_ext=FILTER, env_options=env_options)

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
