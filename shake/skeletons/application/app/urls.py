# -*- coding: utf-8 -*-
"""
Application's URLs.

The priority is based upon order of creation:
first created -> highest priority.
"""
from shake import Rule, EndpointPrefix, Submount

from .users.urls import user_urls


urls = [
    
    EndpointPrefix('app.controllers', [
        Rule('/', 'index'),
    ]),

    Submount('/users/', user_urls),
]
