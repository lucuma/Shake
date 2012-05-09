# -*- coding: utf-8 -*-
"""
"""
import os
import sys

import shake
from shake_files import FileStorage, IMAGES
from solution import SQLAlchemy

import settings


# Add the content of `libs` to the PATH, so you can do
# `import something` to everything inside libs, without install it first.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))


app = shake.Shake(settings)

# Used for the local development server.
# In production, you'll have to define the static paths
# in your server config.
app.add_static(app.settings.STATIC_URL, app.settings.STATIC_DIR)
app.add_static(app.settings.MEDIA_URL, app.settings.MEDIA_DIR)

render = shake.Render(app.settings.VIEWS_DIR)
render.set_global('STATIC', app.settings.STATIC_URL)
render.set_global('STYLES', app.settings.STATIC_URL_STYLES)
render.set_global('SCRIPTS', app.settings.STATIC_URL_SCRIPTS)
render.set_global('IMAGES', app.settings.STATIC_URL_IMAGES)
render.set_global('MEDIA', app.settings.MEDIA_URL)

db = SQLAlchemy(app.settings.SQLALCHEMY_URI, app, echo=False)

mailer = app.settings.MAILER_CLASS(app.settings.MAILER_SETTINGS)

uploader = FileStorage(app.settings.MEDIA_DIR, app.settings.MEDIA_URL,
    allowed=IMAGES)

