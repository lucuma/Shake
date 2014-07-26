# -*- coding: utf-8 -*-
"""
    Shake.wrappers
    --------------------------

"""
from werkzeug.utils import cached_property
from werkzeug.wrappers import Request as BaseRequest
from werkzeug.wrappers import Response as BaseResponse
from werkzeug.datastructures import ImmutableMultiDict

from .helpers import local, StorageDict, to_unicode
from .serializers import from_json, to_json


__all__ = (
    'Request', 'Response', 'Settings', 'make_response',
)


class Request(BaseRequest):
    """The request object used by default in shake.
    Remembers the route rule, the matched endpoint and the view arguments.
    
    It is what ends up passed to the view as the `request` argument.
    If you want to replace this class set `shake.Shake.request_class`
    to your own subclass.

    """
    
    # The internal route rule that matched the request.  This can be
    # useful to inspect which methods are allowed for the route from
    # a before/after handler (`request.url_rule.methods`) etc.
    url_rule = None
    
    # The real endpoint that matched the request
    # (request.endpoint could be a string).  This in combination with
    # `kwargs` can be used to reconstruct the same or a
    # modified URL.  If an exception happened when matching, this will
    # be `None`.
    endpoint = None
    
    # A dict of view arguments that matched the request.  If an exception
    # happened when matching, this will be `None`.
    kwargs = None
    
    # The class to use for `args` and `form`.  The default is an
    # `ImmutableMultiDict` which supports multiple values per key.
    # alternatively it makes sense to use an 
    # `ImmutableOrderedMultiDict` which preserves order or a
    # `ImmutableDict` which is the fastest but only remembers the
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


class Response(BaseResponse):
    """The response object that is used by default in shake.
    Works like the response object from Werkzeug but is set to have a plain
    text mimetype by default.
    Quite often you don't have to create this object yourself because
    `shake.render` will take care of that for you.
    
    If you want to replace the response object used you can subclass this and
    set `shake.Shake.response_class` to your subclass.
    
    """
    default_mimetype = 'text/plain'


class Settings(object):
    """A helper to manage custom and default settings
    """
    
    def __init__(self, custom, default):
        if isinstance(custom, dict):
            custom = StorageDict(custom)
        if isinstance(default, dict):
            default = StorageDict(default)
        self.__dict__['custom'] = custom
        self.__dict__['default'] = default
    
    def __contains__(self, key):
        return hasattr(self.__dict__['custom'], key)
    
    def __getattr__(self, key):
        dcustom = self.__dict__['custom']
        ddefault = self.__dict__['default']
        if hasattr(dcustom, key):
            return getattr(dcustom, key)
        if hasattr(ddefault, key):
            return getattr(ddefault, key)
        # Deprecated: Case-insensitive search
        if hasattr(ddefault, key.lower()):
            return getattr(ddefault, key.lower())
        raise AttributeError(key)
    
    def __setattr__(self, key, value):
        setattr(self.__dict__['custom'], key, value)
    
    def __delattr__(self, key):
        delattr(self.__dict__['custom'], key)

    __getitem__ = __getattr__
    __setitem__ = __setattr__
    __delitem__ = __delattr__
    
    def get(self, key, default=None):
        dcustom = self.__dict__['custom']
        ddefault = self.__dict__['default']
        if hasattr(dcustom, key):
            return getattr(dcustom, key)
        if hasattr(ddefault, key):
            return getattr(ddefault, key)
        # Deprecated: Case-insensitive search
        if hasattr(ddefault, key.lower()):
            return getattr(ddefault, key.lower())
        return default
    
    def setdefault(self, key, value):
        dcustom = self.__dict__['custom']
        if hasattr(dcustom, key):
            return getattr(dcustom, key)
        setattr(dcustom, key, value)
        return value
    
    def update(self, dict_):
        dcustom = self.__dict__['custom']
        for key, value in dict_.items():
            setattr(dcustom, key, value)


def make_response(resp='', status=None, headers=None,
        response_class=Response, **kwargs):
    """Converts the return value from a view function to a real
    response object that is an instance of `response_class`.
    
    The following types are allowed for `resp_value`:
        
    `None`
    :   an empty response object is created.
    `response`
    :   the object is returned unchanged.
    `str`
    :   a response object is created with the string as body.
    `unicode`
    :   a response object is created with the string encoded to utf-8
        as body.
    `dict`
    :   creates a response object with the JSON representation of the
        dictionary and the mimetype of `application/json`.
    WSGI function
    :   the function is called as WSGI application and buffered as
        response object.
    
    Parameters:

    resp_value
    :   the return value from the view function.
    status
    :   An optional status code.
    headers
    :   A dictionary with custom headers.
    
    return: an instance of `response_class`
    
    """
    if resp is None:
        resp = ''

    if isinstance(resp, dict):
        kwargs['mimetype'] = 'application/json'
        resp = to_json(resp, indent=None)

    if not isinstance(resp, BaseResponse):
        if isinstance(resp, basestring):
            resp = response_class(resp, status=status, headers=headers,
                **kwargs)
            headers = status = None
        elif not callable(resp):
            resp = to_unicode(resp)
            resp = response_class(resp, status=status, headers=headers,
                **kwargs)
            headers = status = None
        else:
            resp = response_class.force_type(resp, local.request.environ)

    if status is not None:
        if isinstance(status, basestring):
            resp.status = status
        else:
            resp.status_code = status
    if headers:
        resp.headers.extend(headers)

    return resp
