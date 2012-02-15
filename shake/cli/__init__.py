# -*- coding: utf-8 -*-
"""
# Shake.cli

Command-line scripts

"""
import hashlib
import os
from subprocess import Popen
import time

try:
    import virtualenv
except ImportError:
    virtualenv = False

from .globals import *
from .generators import generator


APP_SKELETON = os.path.join(ROOTDIR, 'application')

PIP_IGNORE_LINES = (
    'Requirement already', 'Cleaning up...',
    'warning:', 'no previously-included',
)

TAB = '      '


def make_secret():
    return hashlib.sha1(os.urandom(64)).hexdigest()


def make_env(app_path, quiet=False):
    if not virtualenv:
        return
    try:
        env_path = os.path.join(app_path, 'env')
        print voodoo.formatm('run', 'virtualenv %s' % env_path, color='green')
        virtualenv.create_environment(
            env_path,
            site_packages=False,
            unzip_setuptools=True,
            use_distribute=True
        )
        return True
    except:
        return False


def install_requirements(app_path, with_env=True, quiet=False):
    if not quiet:
        msg = 'pip install -r %s%srequirements.txt' % (app_path, os.path.sep)
        print voodoo.formatm('run', msg, color='green'), '\n'
    
    if with_env:
        msg = '%s%s%s' % (
            os.path.join(app_path, 'env', 'bin'),
            os.path.sep,
            msg
        )
    args = msg.split(' ')
    proc = Popen(args, shell=False)
    proc.communicate()


@manager.command
def new(app_path, skeleton=APP_SKELETON, **options):
    """APP_PATH [SKELETON_PATH]
    
    The 'shake new' command creates a new Shake application with a default
    directory structure at the path you specify.

    Example:
        shake new projects/wiki
    
    By default it uses Shake's built-in skeleton, but you can provide a custom
    one if you want.
    """
    quiet = options.get('quiet', options.get('q', False))
    pretend = options.get('pretend', options.get('p', False))

    app_path = app_path.rstrip(os.path.sep)
    data = {
        'SECRET1': make_secret(),
        'SECRET2': make_secret(),
    }
    voodoo.reanimate_skeleton(skeleton, app_path, data=data,
        filter_ext=FILTER, env_options=ENV_OPTIONS, **options)
    
    if not pretend:
        with_env = make_env(app_path, quiet)
        install_requirements(app_path, with_env, quiet)

    if not quiet:
        print '\n' + TAB + 'Done!'


def main():
    ok = manager.run()
    if not ok:
        print format_title('GENERAL OPTIONS') + """
    -h, [--help]     # Show help
    -p, [--pretend]  # Run but do not make any changes
    -f, [--force]    # Overwrite files that already exist
    -s, [--skip]     # Skip files that already exist
    -q, [--quiet]    # Suppress status output
    """


if __name__ == "__main__":
    main()
