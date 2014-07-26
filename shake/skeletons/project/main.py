# -*- coding: utf-8 -*-
"""

"""
from os.path import join, dirname
import sys
# Add the content of `libs` to the PATH, so you can do
# `import something` to everything inside libs, without install it first.
sys.path.insert(0, join(dirname(__file__), 'libs'))

# from moar import Thumbnailer
import shake
from shake_files import FileStorage, IMAGES
from solution import SQLAlchemy

from settings import settings


app = shake.Shake(__file__, settings)

# Used for the local development server.
# In production, you'll have to define the static paths in your server config.
app.add_static(app.settings.STATIC_URL, app.settings.STATIC_DIR)
app.add_static(app.settings.MEDIA_URL, app.settings.MEDIA_DIR)

db = SQLAlchemy(app.settings.SQLALCHEMY_URI, app, echo=False)

mailer = app.settings.MAILER_CLASS(**app.settings.MAILER_SETTINGS)

uploader = FileStorage(app.settings.MEDIA_DIR, app.settings.MEDIA_URL,
    allowed=IMAGES)

# thumbnail = Thumbnailer()

app.render.env.globals.update({
    'STATIC': app.settings.STATIC_URL,
    'STYLES': app.settings.STATIC_URL_STYLES,
    'SCRIPTS': app.settings.STATIC_URL_SCRIPTS,
    'IMAGES': app.settings.STATIC_URL_IMAGES,
    'MEDIA': app.settings.MEDIA_URL,
    # 'thumbnail': thumbnail,
})
