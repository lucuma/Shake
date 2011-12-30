# -*- coding: utf-8 -*-
"""
# Shake.cli.utils

"""
import os
import re


_FIRST_CAP_RE = re.compile('(.)([A-Z][a-z]+)')
_ALL_CAP_RE = re.compile('([a-z0-9])([A-Z])')


def underscores_to_camelcase(name):
    return ''.join([word.title() for word in name.split('_')])


def camelcase_to_underscores(name):
    s1 = _FIRST_CAP_RE.sub(r'\1_\2', name)
    name = _ALL_CAP_RE.sub(r'\1_\2', s1).lower()
    return name


PLURAL_RULES = [
    ('[ml]ouse$', '([ml])ouse$', '\\1ice'), 
    ('child$', 'child$', 'children'), 
    ('booth$', 'booth$', 'booths'), 
    ('foot$', 'foot$', 'feet'), 
    ('ooth$', 'ooth$', 'eeth'), 
    ('l[eo]af$', 'l([eo])af$', 'l\\1aves'), 
    ('sis$', 'sis$', 'ses'), 
    ('man$', 'man$', 'men'), 
    ('ife$', 'ife$', 'ives'), 
    ('eau$', 'eau$', 'eaux'), 
    ('lf$', 'lf$', 'lves'), 
    ('[sxz]$', '$', 'es'), 
    ('[^aeioudgkprt]h$', '$', 'es'), 
    ('(qu|[^aeiou])y$', 'y$', 'ies'), 
    ('$', '$', 's')
]
 

def regex_rules(rules=PLURAL_RULES):
    for line in rules:
        pattern, search, replace = line
        yield lambda word: re.search(pattern, word) and \
            re.sub(search, replace, word)


def pluralize(noun):
    for rule in regex_rules():
        result = rule(noun)
        if result: 
            return result
    return noun


def sanitize_name(base, name):
    plural = pluralize(name)
    f1 = os.path.join(base, name) + '.py'
    f2 = os.path.join(base, plural) + '.py'

    if os.path.exists(f1) or os.path.exists(f2):
        return '_' + name
    return name

