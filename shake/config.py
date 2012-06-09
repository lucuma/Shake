# -*- coding: utf-8 -*-
"""
    # Shake.config

"""
import inspect

from .wrappers import Settings


class DefaultSettings(object):

    server_name = '127.0.0.1'
    server_port = 5000
    default_subdomain = ''
    
    force_script_name = False
    
    debug = True
    reload = True
    
    secret_key = None
    session_cookie_name = 'shake_session'
    session_expires = 24 * 120
    
    # The maximum size for uploade files
    max_content_length = 1024 * 1024 * 16  # 16 MB
    # The maximum size for regular form data (not files)
    max_form_memory_size = 1024 * 1024 * 2  # 2 MB
    
    locale = 'en_US'

    # URL prefix for static files.
    # Examples: "http://media.lucumalabs.com/static/", "http://abc.org/static/"
    static_url = '/static'
    
    page_not_found = 'shake.controllers.not_found_page'
    page_error = 'shake.controllers.error_page'
    page_not_allowed = 'shake.controllers.not_allowed_page'


def get_settings_object(custom):
    if inspect.isclass(custom):
        custom = custom()
    default = DefaultSettings()
    return Settings(custom, default)


QUOTES = [
    ('Shaken, not stirred', 'Bond, James Bond'),
    ('Shake it, baby!', 'Austin Powers'),
    ('You\'re riding Shake on rails!', 'Anonymous Coward'),
    ('Shake-it Shake-it Shake-it', 'Ray Charles'),
    ('Shake Shake Shake, Shake your booty', 'KC & The Sunshine Band')
]
