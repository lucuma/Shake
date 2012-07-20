# -*- coding: utf-8 -*-
"""
    Shake.session
    --------------------------

"""
import hashlib
import os

from jinja2 import Markup
from werkzeug.contrib.securecookie import SecureCookie as BaseSecureCookie

from .helpers import local, to64


__all__ = (
    'SecureCookie', 'CSRFToken',
    'get_csrf', 'new_csrf', 'flash', 'get_messages',
)


CSRF_FORM_NAME = '_csrf'
CSRF_SESSION_NAME = '_c'
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


class CSRFToken(object):
    
    name = CSRF_FORM_NAME
    
    def __init__(self):
        value = hashlib.md5(os.urandom(32)).hexdigest()[:16]
        self.value = to64(int(value, 16))

    def get_input(self):
        return Markup(u'<input type="hidden" name="%s" value="%s">' %
            (self.name, self.value))
    
    def get_query(self):
        return Markup(u'%s=%s') % (self.name, self.value)

    @property
    def input(self):
        return self.get_input()
    
    @property
    def query(self):
        return self.get_query()
    
    def __repr__(self):
        return '<CSRFToken %s = "%s">' % (self.name, self.value)


def get_csrf(request=None):
    """Use it to prevent Cross Site Request Forgery (CSRF) attacks."""
    request = request or local.request
    csrf = request.session.get(CSRF_SESSION_NAME)
    if not csrf:
        csrf = new_csrf(request)
    return csrf


def new_csrf(request=None):
    request = request or local.request
    csrf = CSRFToken()
    request.session[CSRF_SESSION_NAME] = csrf
    return csrf


def flash(msg, cat='info', **kwargs):
    """Flashes a message to the next session.  In order to remove the
    flashed message from the session and to display it to the user,
    the view has to call `shake.get_messages`.
    
    msg
    :   the message to be flashed.
    cat
    :   optional classification of the message. By default is 'info'.
    kwargs
    :   extra data passed along the message

    """
    kwargs['msg'] = msg
    kwargs['cat'] = cat
    session = local.request.session
    session.setdefault(LOCAL_FLASHES, []).append(kwargs)


def get_messages():
    """Pulls all flashed messages from the session and returns them.
    Further calls in the same request to the function will return
    the same messages.
    """
    flashes = getattr(local, LOCAL_FLASHES, None)
    if not flashes:
        session = local.request.session
        flashes = session.get(LOCAL_FLASHES) or []
        setattr(local, LOCAL_FLASHES, flashes)
        if flashes:
            del session[LOCAL_FLASHES]
    return flashes or []

