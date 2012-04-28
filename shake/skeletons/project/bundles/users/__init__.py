# -*- coding: utf-8 -*-
"""
The priority is based upon order of creation:
first created -> highest priority.
"""
from shake import Rule
from shake_auth import Auth

from main import app, render, mailer
from .models import User


auth = Auth(User, app,
    render=render, mailer=mailer,
    **app.settings.AUTH_SETTINGS
)


urls = [

    Rule('/sign-in/', auth.sign_in_controller,
        name='auth.sign_in'),

    Rule('/sign-out/', auth.sign_out_controller,
        name='auth.sign_out'),

    Rule('/change-password/', auth.change_password_controller,
        name='auth.change_password'),

    Rule('/reset-password/', auth.reset_password_controller,
        name='auth.reset_password'),

    Rule('/reset-password/<token>/',auth.reset_password_controller,
        name='auth.check_token'),

]

