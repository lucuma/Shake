# -*- coding: utf-8 -*-
"""
Application's URLs.

The priority is based upon order of creation:
first created -> highest priority.
"""
from shake import Rule, Submount

from main import app


app.add_urls([

    # Index and other common pages like not-found
    Submount('/', 'common.urls'),

    # Login, logout, password reset and related pages
    Submount('/', 'users.urls'),

    # Mount your bundle's urls like this
    # Submount('/where_to_mount/', 'bundle.urls'),
    # Example:
    # Submount('/blog/', 'posts.urls'),

])
