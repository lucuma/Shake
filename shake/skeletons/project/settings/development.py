# -*- coding: utf-8 -*-
"""
    Development settings
    -------------------------------
    
"""
from mailshake import ToConsoleMailer

from .base import *


DEBUG = True
RELOAD = True

# Optional server name hint
SERVER_NAME = '127.0.0.1'

SQLALCHEMY_URI = 'sqlite:///db.sqlite'

MAILER_CLASS = ToConsoleMailer
# Extra settings for the mailer class
MAILER_SETTINGS = {}

