# -*- coding: utf-8 -*-
"""
# Shake.cli.globals

"""
import os
import re

from pyceo import Manager, format_title
import voodoo


manager = Manager()


ROOTDIR = os.path.realpath(os.path.join(os.path.dirname(__file__),
    '..', 'skeletons'))

ENV_OPTIONS = {
    'autoescape': False,
    'block_start_string': '[%',
    'block_end_string': '%]',
    'variable_start_string': '[[',
    'variable_end_string': ']]',
}

FILTER = ('.pyc', '.DS_Store', '.pyo')

