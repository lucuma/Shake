# -*- coding: utf-8 -*-
"""
# Shake.cli.utils

"""
import hashlib
import os
from subprocess import Popen
import re

import voodoo

from .globals import (FIELD_TYPES, DEFAULT_FIELD_TYPE,
    SINGULAR_RULES, PLURAL_RULES)


_FIRST_CAP_RE = re.compile('(.)([A-Z][a-z]+)')
_ALL_CAP_RE = re.compile('([a-z0-9])([A-Z])')


def make_secret():
    return hashlib.sha1(os.urandom(64)).hexdigest()


def install_requirements(app_path, quiet=False):
    msg = 'pip install -r %s%srequirements.txt' % (app_path, os.path.sep)
    if not quiet:
        print voodoo.formatm('run', msg, color='white'), '\n'

    args = msg.split(' ')
    proc = Popen(args, shell=False)
    proc.communicate()


def underscores_to_camelcase(name):
    return ''.join([word.title() for word in name.split('_')])


def camelcase_to_underscores(name):
    s1 = _FIRST_CAP_RE.sub(r'\1_\2', name)
    name = _ALL_CAP_RE.sub(r'\1_\2', s1).lower()
    return name
 

def regex_rules(rules):
    for line in rules:
        pattern, search, replace = line
        yield lambda word: re.search(pattern, word) and \
            re.sub(search, replace, word)


def singularize(noun):
    for rule in regex_rules(SINGULAR_RULES):
        result = rule(noun)
        if result: 
            return result
    return noun


def pluralize(noun):
    for rule in regex_rules(PLURAL_RULES):
        result = rule(noun)
        if result: 
            return result
    return noun


def sanitize_name(name):
    singular = singularize(name)
    plural = name
    if singular == name:
        plural = pluralize(name)

    num = 2
    while os.path.exists(plural + '.py'):
        plural = plural + str(num)
        num = num + 1
    
    return singular, plural


def get_model_fields(args):
    fields = []
    for f in args:
        try:
            fname, ftype = f.split(':')
        except ValueError:
            fname = f
            ftype = 'string'
        ftype = re.sub(r'[^a-z0-9]', '', ftype.lower())
        field = FIELD_TYPES.get(ftype, DEFAULT_FIELD_TYPE)
        field = (fname, field[0], field[1])
        fields.append(field)
    return fields

