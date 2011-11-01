# -*- coding: utf-8 -*-
"""
    # shake.config
    

    --------
    Copyright © 2010-2011 by Lúcuma labs (http://lucumalabs.com).
    
    MIT License. (http://www.opensource.org/licenses/mit-license.php)

"""
from .helpers import StorageDict


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


class Settings(object):
    
    def __init__(self, custom):
        if isinstance(custom, dict):
            custom = StorageDict(custom)
        self.__dict__['custom'] = custom
    
    def __contains__(self, key):
        return hasattr(self.custom, key)
    
    def __getattr__(self, key):
        if hasattr(self.__dict__['custom'], key):
            return getattr(self.__dict__['custom'], key)
        elif key in DEFAULT_SETTINGS:
            return DEFAULT_SETTINGS[key]
        
        raise AttributeError('No %s was found in the custom or'
            ' default settings' % key)
    
    def __setattr__(self, key, value):
        setattr(self.custom, key, value)
    
    __getitem__ = __getattr__
    __setitem__ = __setattr__
    
    def get(self, key, default=None):
        if hasattr(self.custom, key):
            return getattr(self.custom, key)
        return DEFAULT_SETTINGS.get(key, default)
    
    def setdefault(self, key, value):
        if hasattr(self.custom, key):
            return getattr(self.custom, key)
        setattr(self.custom, key, value)
        return value
    
    def update(self, dict_):
        custom = self.custom
        for key, value in dict_.items():
            setattr(custom, key, value)


QUOTES = [
    ('Shaken, not stirred', 'Bond, James Bond'),
    ('Shake it, baby!', 'Austin Powers'),
    ('Shake your Ruby', 'Anonymous Coward'),
    ('You\'re riding Shake on rails!', 'Former Rails user'),
    ('Shake-it Shake-it Shake-it', 'Ray Charles'),
    ('Shake Shake Shake, Shake your booty', 'KC & The Sunshine Band')
    ]
