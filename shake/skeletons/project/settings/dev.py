# -*- coding: utf-8 -*-
"""
    Development settings
    -------------------------------
    
"""
from mailshake import ToConsoleMailer

from .common import *


DEBUG = True
RELOAD = True

SQLALCHEMY_URI = 'sqlite:///db.sqlite'

MAILER_CLASS = ToConsoleMailer
# Extra settings for the mailer class
MAILER_SETTINGS = {}

