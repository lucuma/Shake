# -*- coding: utf-8 -*-
"""
    Users URLs.
    -------------------------------

    The priority is based upon order of creation:
    first created -> highest priority.

"""
from shake import Rule
from shake_auth import Auth

from main import app, mailer
from .models import User


auth = Auth(User, app, mailer=mailer, **app.settings.AUTH_SETTINGS)

urls = [
    Rule('/sign-in/', auth.sign_in_view,
        name='auth.sign_in'),

    Rule('/sign-out/', auth.sign_out_view,
        name='auth.sign_out'),

    Rule('/reset-password/', auth.reset_password_view,
        name='auth.reset_password'),

    Rule('/reset-password/<token>/',auth.reset_password_view,
        name='auth.check_token'),

    Rule('/change-password/', auth.change_password_view,
        name='auth.change_password'),
]

