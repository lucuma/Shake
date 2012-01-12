# -*- coding: utf-8 -*-
"""
# Shake.cli

Command-line scripts

"""
import hashlib
import os
from subprocess import Popen, PIPE
import tempfile
import time

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


def install_requirements(app_path, quiet=False):
    if not quiet:
        msg = 'pip install -r %s%srequirements.txt' % (app_path, os.path.sep)
        print voodoo.formatm('run', msg, color='green'), '\n'
    
    args = msg.split(' ')
    pipe_output, file_name = tempfile.mkstemp()
    proc = Popen(args, shell=False, stdout=pipe_output)
    
    # # proc.poll() returns None while the program is still running
    # while proc.poll() is None:
    #     # sleep for 1 second
    #     time.sleep(1)
    #     last_line =  open(file_name).readline()
    #     # It's possible that it hasn't output yet
    #     if len(last_line) == 0:
    #         continue
    #     line = last_line[-1].strip()
    #     if line and not line.startswith(PIP_IGNORE_LINES):
    #         print TAB + line
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
        install_requirements(app_path, quiet)

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
