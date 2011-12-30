# -*- coding: utf-8 -*-
"""
# Shake.cli

Command-line scripts

"""
import hashlib
import os
from subprocess import Popen, PIPE

from .globals import *
from .generators import generator


APP_SKELETON = os.path.join(ROOTDIR, 'application')


def make_secret():
    return hashlib.sha1(os.urandom(64)).hexdigest()


def install_requirements(app_path, quiet=False):
    if not quiet:
        msg = 'pip install -r %s%srequirements.txt -q' % (app_path, os.path.sep)
        print voodoo.formatm('run', msg, color='green')

    args = msg.split(' ')
    proc = Popen(args, shell=False, stderr=PIPE, stdout=PIPE)
    retcode = proc.wait()
    if retcode != 0:
        raise Exception(proc.stderr.read())
    if not quiet:
        print proc.stdout.read()


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
        install_requirements(app_path, quiet)

    if not quiet:
        print voodoo.formatm('Done!', '', color='green')


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
