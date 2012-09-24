# -*- coding: utf-8 -*-
"""
    Common URLs
    -------------------------------

    The priority is based upon order of creation:
    first created -> highest priority.

"""
from shake import Rule, EndpointPrefix, Submount

from . import views


urls = [
    EndpointPrefix('bundles.common.views', [
        Rule('/', 'index',
            name='index'), 
    ]),
]