# -*- coding: utf-8 -*-
import inspect

from .wrappers import Settings


class DefaultSettings(object):

    SERVER_NAME = '0.0.0.0'
    SERVER_PORT = 5000
    DEFAULT_SUBDOMAIN = None

    FORCE_SCRIPT_NAME = False

    DEBUG = True
    RELOADER = True

    SECRET_KEY = None
    SESSION_COOKIE_NAME = '_session'
    SESSION_COOKIE_DOMAIN = None
    SESSION_COOKIE_PATH = None
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = None
    SESSION_LIFETIME = 24 * 365  # 365 days

    # The maximum size for uploade files
    MAX_CONTENT_LENGTH = 1024 * 1024 * 50  # 50 MB
    # The maximum size for regular form data (not files)
    MAX_FORM_MEMORY_SIZE = 1024 * 1024 * 50  # 5 MB

    DEFAULT_MIMETYPE = 'text/html'

    DEFAULT_LOCALE = 'en'
    DEFAULT_TIMEZONE = 'UTC'

    PAGE_NOT_FOUND = 'shake.views.not_found_page'
    PAGE_ERROR = 'shake.views.error_page'
    PAGE_NOT_ALLOWED = 'shake.views.not_allowed_page'

    EASTER_EGG = u'Shaken, not stirred'


def get_settings_object(custom):
    if inspect.isclass(custom):
        custom = custom()
    default = DefaultSettings()
    return Settings(custom, default)
