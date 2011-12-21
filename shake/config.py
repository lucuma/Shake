# -*- coding: utf-8 -*-
"""
    # Shake.config

"""
from .wrappers import Settings


DEFAULT_SETTINGS = {
    'SERVER_NAME': '127.0.0.1',
    'SERVER_PORT': 5000,
    
    'FORCE_SCRIPT_NAME': False,
    
    'DEBUG': True,
    
    'SECRET_KEY': None,
    'SESSION_COOKIE_NAME': 'shake_session',
    'SESSION_EXPIRES': 24 * 120,
    
    'MAX_CONTENT_LENGTH': 1024 * 1024 * 16,  # 16 MB
    # The maximum size for regular form data (not files)
    'MAX_FORM_MEMORY_SIZE': 1024 * 1024 * 2,  # 2 MB
    
    'TIMEZONE': 'utc',
    'LOCALE': 'en_US',
    
    'PAGE_NOT_FOUND': 'shake.controllers.not_found_page',
    'PAGE_ERROR': 'shake.controllers.error_page',
    'PAGE_NOT_ALLOWED': 'shake.controllers.not_allowed_page',
}


class ShakeSettings(Settings):
    
    def __init__(self, custom):
        Settings.__init__(self, DEFAULT_SETTINGS, custom)


QUOTES = [
    ('Shaken, not stirred', 'Bond, James Bond'),
    ('Shake it, baby!', 'Austin Powers'),
    ('Shake your Ruby', 'Anonymous Coward'),
    ('You\'re riding Shake on rails!', 'Former Rails user'),
    ('Shake-it Shake-it Shake-it', 'Ray Charles'),
    ('Shake Shake Shake, Shake your booty', 'KC & The Sunshine Band')
    ]
