# -*- coding: utf-8 -*-
"""
# Shake.cli.globals

"""
import os


ROOTDIR = os.path.realpath(os.path.join(os.path.dirname(__file__),
    '..', 'skeletons'))

APP_SKELETON = os.path.join(ROOTDIR, 'project')
RESOURCE_SKELETON = os.path.join(ROOTDIR, 'resource')


ENV_OPTIONS = {
    'autoescape': False,
    'block_start_string': '[%',
    'block_end_string': '%]',
    'variable_start_string': '[[',
    'variable_end_string': ']]',
}

FILTER = ('.pyc', '.DS_Store', '.pyo')


PLURAL_RULES = [
    ('[ml]ouse$', 'ouse$', 'ice'),
    ('child$', '$', 'ren'),
    ('foot$', 'foot$', 'feet'),
    ('booth$', '$', 's'),
    ('ooth$', 'ooth$', 'eeth'),
    ('octopus$', 'us$', 'i'),
    ('l[eo]af$', 'f$', 'ves'),
    ('ife$', 'fe$', 'ves'),
    ('sis$', 'is$', 'es'),
    ('man$', 'an$', 'en'),
    ('eau$', '$', 'x'),
    ('lf$', 'f$', 'ves'),
    ('[sxz]$', '$', 'es'),
    ('[^aeioudgkprt]h$', '$', 'es'),
    ('(qu|[^aeiou])y$', 'y$', 'ies'),
    ('[^s]$', '$', 's'),
]

SINGULAR_RULES = [
    ('[ml]ice$', 'ice$', 'ouse'),
    ('children$', 'ren$', ''),
    ('feet$', 'eet$', 'oot'),
    ('booths$', 's$', ''),
    ('eeth$', 'eeth$', 'ooth'),
    ('octopi$', 'i$', 'us'),
    ('l[eo]aves$', 'ves$', 'f'),
    ('ives$', 'ves$', 'fe'),
    ('ses$', 'es$', 'is'),
    ('men$', 'en$', 'an'),
    ('eaux$', 'x$', ''),
    ('lves$', 'ves$', 'f'),
    ('[sxz]es$', 'es$', ''),
    ('[^aeioudgkprt]hes$', 'es$', ''),
    ('(qu|[^aeiou])ies$', 'ies$', 'y'),
    ('s$', 's$', ''),
]

