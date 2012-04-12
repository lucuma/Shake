# -*- coding: utf-8 -*-
"""
The priority is based upon order of creation:
first created -> highest priority.
"""
from shake_auth import Auth

from main import app, render, mailer
from . import manage
from .models import User


auth = Auth(User, app,
    render=render, mailer=mailer,
    **app.settings.AUTH_SETTINGS
)

urls = auth.get_urls()
