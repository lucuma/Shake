# -*- coding: utf-8 -*-
from shake import Shake

from . import settings, controllers
from .models import db, auth
from .urls import urls


app = Shake(urls, settings)
db.init_app(app)
auth.init_app(app)

# Used for the local development server.
# In production, you'll have to define the static paths
# in your server config.
app.add_static('/static', settings.STATIC_ROOT)
