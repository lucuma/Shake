# -*- coding: utf-8 -*-
"""
    Shake.session
    --------------------------

"""
from datetime import datetime
import hashlib
import os
from time import time

from jinja2 import Markup
from itsdangerous import URLSafeTimedSerializer, BadSignature
from werkzeug.datastructures import CallbackDict

from .helpers import local, to64


__all__ = (
    'Session', 'NullSession', 'SessionInterface', 'ItsdangerousSessionInterface',
    'generate_key', 'CSRFToken', 'get_csrf', 'new_csrf', 'flash', 'get_messages',
)


CSRF_FORM_NAME = '_csrf'
CSRF_SESSION_NAME = '_c'
LOCAL_FLASHES = '_fm'


class Session(CallbackDict):

    def __init__(self, initial=None):
        def on_update(self):
            self._modified = True
        CallbackDict.__init__(self, initial, on_update)
        self._modified = False


class NullSession(CallbackDict):
    """Class used to generate nicer error messages if sessions are not
    available.  Will still allow read-only access to the empty session
    but fail on setting.

    """

    def _fail(self, *args, **kwargs):
        raise RuntimeError('The session is unavailable because no secret '
            'key was set.  Set the SECRET_KEY on the application to something '
            'unique and secret.')

    __setitem__ = __delitem__ = clear = pop = popitem = update = setdefault = _fail
    del _fail


class SessionInterface(object):
    """The basic interface you have to implement in order to replace the
    default session interface which uses werkzeug's securecookie
    implementation.  The only methods you have to implement are
    :meth:`open_session` and :meth:`save_session`, the others have
    useful defaults which you don't need to change.

    The session object returned by the :meth:`open_session` method has to
    provide a dictionary like interface .

    If :meth:`open_session` returns `None` Shake will call into
    :meth:`make_null_session` to create a session that acts as replacement
    if the session support cannot work because some requirement is not
    fulfilled.  The default :class:`NullSession` class that is created
    will complain that the secret key was not set.

    To replace the session interface on an application all you have to do
    is to assign :attr:`shake.Shake.session_interface`::

        app = Shake(__name__)
        app.session_interface = MySessionInterface(app)

    """
    # :meth:`make_null_session` will look here for the class that should
    # be created when a null session is requested.  Likewise the
    # :meth:`is_null_session` method will perform a typecheck against
    # this type.
    null_session_class = NullSession

    def __init__(self, app):
        self.app = app

    def make_null_session(self):
        """Creates a null session which acts as a replacement object if the
        real session support could not be loaded due to a configuration
        error.  This mainly aids the user experience because the job of the
        null session is to still support lookup without complaining but
        modifications are answered with a helpful error message of what
        failed.

        This creates an instance of :attr:`null_session_class` by default.

        """
        return self.null_session_class()

    def is_null_session(self, obj):
        """Checks if a given object is a null session.  Null sessions are
        not asked to be saved.

        This checks if the object is an instance of :attr:`null_session_class`
        by default.

        """
        return isinstance(obj, self.null_session_class)

    def get_cookie_domain(self):
        """Helpful helper method that returns the cookie domain that should
        be used for the session cookie if session cookies are used.

        """
        cookie_domain = self.app.settings.get('SESSION_COOKIE_DOMAIN')
        if cookie_domain is not None:
            return cookie_domain
        cookie_domain = self.app.settings.get('SERVER_NAME')
        if cookie_domain is None:
            return None
        # a port number *could* be included, so try to remove it, because
        # it's usually not supported by browsers
        cookie_domain = cookie_domain.rsplit(':', 1)[0]
        if cookie_domain in ('localhost', '127.0.0.1', '0.0.0.0',):
            return None
        return '.' + cookie_domain

    def get_cookie_path(self):
        """Returns the path for which the cookie should be valid.  The
        default implementation uses the value from the SESSION_COOKIE_PATH``
        config var if it's set, and falls back to ``/`` if it's `None`.

        """
        return self.app.settings.get('SESSION_COOKIE_PATH', '/')

    def get_cookie_httponly(self):
        """Returns True if the session cookie should be httponly.  This
        currently just returns the value of the ``SESSION_COOKIE_HTTPONLY``
        config var.

        """
        return self.app.settings.get('SESSION_COOKIE_HTTPONLY', True)

    def get_cookie_secure(self):
        """Returns True if the cookie should be secure.  This currently
        just returns the value of the ``SESSION_COOKIE_SECURE`` setting.

        """
        return self.app.settings.get('SESSION_COOKIE_SECURE', False)

    def get_expiration_time(self, session):
        """A helper method that returns an expiration date for the session
        or `None` if the session is linked to the browser session.  The
        default implementation returns now + the permanent session
        lifetime configured on the application.

        """
        return datetime.utcnow() + self.app.session_lifetime

    def open_session(self, request):
        """This method has to be implemented and must either return `None`
        in case the loading failed because of a configuration error or an
        instance of a session object which implements a dictionary like
        interface.

        """
        raise NotImplementedError()

    def save_session(self, session, response):
        """This is called for actual sessions returned by :meth:`open_session`
        at the end of the request.  This is still called during a request
        context so if you absolutely need access to the request you can do
        that.

        """
        raise NotImplementedError()

    def invalidate(self, request):
        """Reset the current session.

        """
        secret_key = self.app.settings.get('SECRET_KEY')
        if not secret_key:
            request.session = self.make_null_session()
        request.session = self.session_class()


class ItsdangerousSessionInterface(SessionInterface):

    session_class = Session
    digest_method = staticmethod(hashlib.sha256)

    def __init__(self, app, salt='shake-session'):
        super(ItsdangerousSessionInterface, self).__init__(app)
        self.salt = salt

    def get_serializer(self):
        secret_key = self.app.settings.get('SECRET_KEY')
        if not secret_key:
            return None
        s = URLSafeTimedSerializer(secret_key, salt=self.salt)
        s.digest_method = self.digest_method
        return s

    def open_session(self, request):
        s = self.get_serializer()
        if s is None:
            request.session = self.make_null_session()
            return
        cookie_name = self.app.settings['SESSION_COOKIE_NAME']
        val = request.cookies.get(cookie_name)
        if not val:
            request.session = self.session_class()
            return
        max_age = self.app.session_lifetime.total_seconds()
        try:
            data = s.loads(val, max_age=max_age)
            request.session = self.session_class(data)
            return
        except BadSignature:
            request.session = self.session_class()
            return

    def save_session(self, session, response):
        if not session:
            # response.delete_cookie(cookie_name, domain=domain)
            return response
        domain = self.get_cookie_domain()
        cookie_name = self.app.settings['SESSION_COOKIE_NAME']
        expires = self.get_expiration_time(session)
        s = self.get_serializer()
        if s is None:
            return response
        session_data = s.dumps(dict(session))
        httponly = self.get_cookie_httponly()
        response.set_cookie(cookie_name, session_data, expires=expires,
            httponly=httponly, domain=domain)
        return response

    def invalidate(self, request):
        s = self.get_serializer()
        if s is None:
            request.session = self.make_null_session()
        request.session = self.session_class()


def generate_key(salt=None):
    value = hashlib.sha1('%s%s%s' % (time(), os.urandom(32), salt)).hexdigest()[:32]
    return to64(int(value, 16))


class CSRFToken(object):
    
    name = CSRF_FORM_NAME
    
    def __init__(self, value=None):
        self.value = value or generate_key('csrf-token')

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
    csrf_value = request.session.get(CSRF_SESSION_NAME)
    if csrf_value:
        csrf = CSRFToken(csrf_value)
    else:
        csrf = new_csrf(request)
    return csrf


def new_csrf(request=None):
    request = request or local.request
    csrf = CSRFToken()
    request.session[CSRF_SESSION_NAME] = csrf.value
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

