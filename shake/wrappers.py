# -*- coding: utf-8 -*-
"""
    # Shake.wrappers

"""
import hashlib

from werkzeug.utils import cached_property
from werkzeug.wrappers import Request as BaseRequest
from werkzeug.wrappers import Response as BaseResponse
from werkzeug.contrib.securecookie import SecureCookie as BaseSecureCookie
from werkzeug.datastructures import ImmutableMultiDict

from .helpers import local, StorageDict
from .serializers import from_json


LOCAL_FLASHES = '_fm'


class SecureCookie(BaseSecureCookie):
    
    hash_method = hashlib.sha256
    
    def invalidate(self):
        for key in self.keys():
            del self[key]


class _NullSession(SecureCookie):
    """Class used to generate nicer error messages if sessions are not
    available.  Will still allow read-only access to the empty session
    but fail on setting.
    """
    
    def _fail(self, *args, **kwargs):
        raise RuntimeError('The session is unavailable because no secret'
            ' key was set.  Set the SECRET_KEY in your settings to something'
            ' unique and secret')
    
    __setitem__ = __delitem__ = _fail
    clear = pop = popitem = update = setdefault = _fail
    del _fail


class Request(BaseRequest):
    """The request object used by default in shake.
    Remembers the route rule, the matched endpoint and the view arguments.
    
    It is what ends up as :class:`~shake.request`.  If you want to replace
    the request object used you can subclass this and set
    :attr:`~shake.Shake.request_class` to your subclass.
    """
    
    # The internal route rule that matched the request.  This can be
    # useful to inspect which methods are allowed for the route from
    # a before/after handler (``request.url_rule.methods``) etc.
    url_rule = None
    
    # The real endpoint that matched the request
    # (request.endpoint could be a string).  This in combination with
    # :attr:`kwargs` can be used to reconstruct the same or a
    # modified URL.  If an exception happened when matching, this will
    # be `None`.
    endpoint = None
    
    # A dict of view arguments that matched the request.  If an exception
    # happened when matching, this will be `None`.
    kwargs = None
    
    # The class to use for `args` and `form`.  The default is an
    # :class:`ImmutableMultiDict` which supports multiple values per key.
    # alternatively it makes sense to use an 
    # :class:`ImmutableOrderedMultiDict` which preserves order or a
    # :class:`ImmutableDict` which is the fastest but only remembers the
    # last key. It is also possible to use mutable structures, but this is
    # not recommended.
    parameter_storage_class = ImmutableMultiDict
    
    # Maximum size for any data.
    # Set by the application
    max_content_length = 0
    
    # The maximum size for regular form data (not files).
    # Set by the application
    max_form_memory_size = 0
    
    @property
    def is_get(self):
        return self.method == 'GET'
    
    @property
    def is_post(self):
        return self.method == 'POST'
    
    @property
    def is_put(self):
        return self.method == 'PUT'
    
    @property
    def is_delete(self):
        return self.method == 'DELETE'
    
    @cached_property
    def json(self):
        """If the mimetype is `application/json` this will contain the
        parsed JSON data.
        """
        if self.mimetype == 'application/json':
            return from_json(self.data)
    
    @cached_property
    def session(self):
        """Creates or opens a new session.
        Default implementation stores all session data in a signed cookie.
        This requires that the :attr:`secret_key` setting is set.
        """
        settings = local.app.settings
        SECRET_KEY = settings.SECRET_KEY
        if not SECRET_KEY:
            return _NullSession(secret_key='')
        
        data = self.cookies.get(settings.SESSION_COOKIE_NAME)
        if not data:
            return SecureCookie(secret_key=SECRET_KEY)
        return SecureCookie.unserialize(data, SECRET_KEY)
    
    def get_language(self, default='en-US'):
        lang = None
        if self.args:
            lang = self.args.get('lang', '')
        if not lang:
            lang = request.accept_languages.best \
                or request.user_agent.language or default
        lang_s = lang.replace('_', '-').split('-')[0]
        return lang_s, lang

    def flash(self, msg, cat='info', extra=None, **kwargs):
        session = self.session
        msg = {'msg': msg, 'cat': cat, 'extra': extra}
        session.setdefault(LOCAL_FLASHES, []).append(msg)


class Response(BaseResponse):
    """The response object that is used by default in shake.
    Works like the response object from Werkzeug but is set to have a plain
    text mimetype by default.
    Quite often you don't have to create this object yourself because
    :meth:`~shake.render` will take care of that for you.
    
    If you want to replace the response object used you can subclass this and
    set :attr:`~shake.Shake.response_class` to your subclass.
    
    """
    default_mimetype = 'text/plain'


class Settings(object):
    """A helper to manage custom and default settings
    """
    
    def __init__(self, default, custom, case_insensitive=False):
        if isinstance(default, dict):
            default = StorageDict(default, _case_insensitive=case_insensitive)
        if isinstance(custom, dict):
            custom = StorageDict(custom, _case_insensitive=case_insensitive)
        self.__dict__['default'] = default
        self.__dict__['custom'] = custom
    
    def __contains__(self, key):
        return hasattr(self.custom, key)
    
    def __getattr__(self, key):
        if hasattr(self.__dict__['custom'], key):
            return getattr(self.__dict__['custom'], key)
        elif hasattr(self.__dict__['default'], key):
            return getattr(self.__dict__['default'], key)
        raise AttributeError(key)
    
    def __setattr__(self, key, value):
        setattr(self.custom, key, value)
    
    __getitem__ = __getattr__
    __setitem__ = __setattr__
    
    def get(self, key, default=None):
        if hasattr(self.custom, key):
            return getattr(self.custom, key)
        return getattr(self.default, key, default)
    
    def setdefault(self, key, value):
        if hasattr(self.custom, key):
            return getattr(self.custom, key)
        setattr(self.custom, key, value)
        return value
    
    def update(self, dict_):
        custom = self.custom
        for key, value in dict_.items():
            setattr(custom, key, value)

