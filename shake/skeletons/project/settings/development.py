# -*- coding: utf-8 -*-
"""
Development environment settings
"""
from mailshake import ToConsoleMailer

from .common import Common


class Development(Common):

    debug = True
    reload = True

    # Optional server name hint
    server_name = '127.0.0.1'

    sqlalchemy_uri = 'sqlite:///db.sqlite'
    
    mailer_class = ToConsoleMailer
    # Extra settings for the mailer class
    mailer_settings = {}

