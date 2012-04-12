# -*- coding: utf-8 -*-
"""
"""
import shake
from solution import SQLAlchemy

import settings


app = shake.Shake(settings)

# Used for the local development server.
# In production, you'll have to define the static paths
# in your server config.
app.add_static(app.settings.STATIC_URL, app.settings.STATIC_DIR)

render = shake.Render(app.settings.VIEWS_DIR)
render.set_global('STATIC', app.settings.STATIC_URL)
render.set_global('STYLES', app.settings.STATIC_URL_STYLES)
render.set_global('SCRIPTS', app.settings.STATIC_URL_SCRIPTS)
render.set_global('IMAGES', app.settings.STATIC_URL_IMAGES)

mailer = app.settings.MAILER_CLASS(app.settings.MAILER_SETTINGS)

db = SQLAlchemy(app.settings.SQLALCHEMY_URI, app, echo=False)
