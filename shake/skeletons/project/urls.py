# -*- coding: utf-8 -*-
"""
    Application's URLs.
    --------------------------

    The priority is based upon order of creation:
    first created -> highest priority.
    
"""
from shake import Rule, Submount

from main import app

# Import all your bundles here, even if they doesn't have URLs
from bundles import common
from bundles import users


app.add_urls([
    # Import your bundle and mount its urls like this:
    # Submount('/where_to_mount/', bundle.urls),
    # Example:  Submount('/blog/', posts.urls),

    # Index and other common pages like not-found
    Submount('/', common.urls),

    # Login, logout, password reset and related pages
    Submount('/', users.urls),

])
