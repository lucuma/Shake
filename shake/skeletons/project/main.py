# -*- coding: utf-8 -*-
"""
"""
import os
import sys

import shake
from shake_files import FileStorage, IMAGES
from solution import SQLAlchemy

from settings import settings


# Add the content of `libs` to the PATH, so you can do
# `import something` to everything inside libs, without install it first.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))


app = shake.Shake(settings)

# Used for the local development server.
# In production, you'll have to define the static paths
# in your server config.
app.add_static(app.settings.static_url, app.settings.static_dir)
app.add_static(app.settings.media_url, app.settings.media_dir)

render = shake.Render(app.settings.views_dir)
render.set_global('STATIC', app.settings.static_url)
render.set_global('STYLES', app.settings.static_url_styles)
render.set_global('SCRIPTS', app.settings.static_url_scripts)
render.set_global('IMAGES', app.settings.static_url_images)
render.set_global('MEDIA', app.settings.media_url)

db = SQLAlchemy(app.settings.sqlalchemy_uri, app, echo=False)

mailer = app.settings.mailer_class(**app.settings.mailer_settings)

uploader = FileStorage(app.settings.media_dir, app.settings.media_url,
    allowed=IMAGES)

