# -*- coding: utf-8 -*-
"""
The priority is based upon order of creation:
first created -> highest priority.
"""
from shake import Rule, EndpointPrefix, Submount

from . import controllers


urls = [

    EndpointPrefix('common.controllers', [

        Rule('/', 'index', name='index'),
        
    ]),

]