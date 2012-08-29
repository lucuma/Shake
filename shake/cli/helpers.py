# -*- coding: utf-8 -*-
"""
    Shake.cli.helpers
    --------------------------

"""
import hashlib
import io
import os
from subprocess import Popen
import re

import inflector
import voodoo


inf = inflector.English()

_IMPORTS_RE = re.compile(r'"(\n*\s*(#[^\n]*|(from [a-zA-Z0-9_\.]+\s+)?import\s+.*))+')


def make_secret():
    return hashlib.sha1(os.urandom(64)).hexdigest()


def install_requirements(app_path, quiet=False):
    args = {'app': app_path, 'sep': os.path.sep}
    msg = 'pip install -r %(app)s%(sep)srequirements%(sep)sdevelopment.txt' % args
    if not quiet:
        print voodoo.formatm('run', msg, color='green'), '\n'

    args = msg.split(' ')
    proc = Popen(args, shell=False)
    proc.communicate()


def sanitize_name(name):
    singular = inf.singularize(name)
    plural = name
    if singular == name:
        plural = inf.pluralize(name)

    num = 2
    while os.path.exists(plural + '.py'):
        plural = plural + str(num)
        num = num + 1

    class_name = inf.camelize(singular)
    return singular, plural, class_name


def get_model_fields(args):
    fields = []
    for f in args:
        try:
            fname, ftype = f.split(':')
        except ValueError:
            fname = f
            ftype = 'string'
        fields.append((fname, ftype))
    return fields


def insert_import(path, imp):
    with io.open(path, 'r') as f:
        s = f.read()
    m = re.search(r'\n%s\s*\n' % imp, s)
    if m:
        return
    m = re.search(_IMPORTS_RE, s)
    if not m:
        return
    end = m.end()
    new_s = '%s\n%s%s' % (s[:end], imp, s[end:])
    with io.open(path, 'w') as f:
        f.write(new_s)

