# -*- coding: utf-8 -*-
"""
Application's URLs.

The priority is based upon order of creation:
first created -> highest priority.
"""
from shake import Rule, Submount

from main import app
import common


app.add_urls([

    Rule('/', common.index, name='index'),
    Submount('/', 'users.urls'),

    # Mount your bundle's urls like this
    # Submount('/where_to_mount/', 'bundle.urls'),
    # Example:
    # Submount('/blog/', 'posts.urls'),
    
])
