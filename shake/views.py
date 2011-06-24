# -*- coding: utf-8 -*-
"""
    shake.views
    ----------------------------------------------

    Implements the bridge to Jinja2.

    :copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
    :license: BSD. See LICENSE for more details.

"""
from datetime import datetime
import hashlib
import os

import jinja2
from jinja2.exceptions import TemplateNotFound
from werkzeug.local import LocalProxy

from .helpers import local, url_for, to64
from . import media


LOCAL_FLASHES = '_fm'


def flash(request, message, category='info', extra=None):
    """Flashes a message to the next request.  In order to remove the
    flashed message from the session and to display it to the user,
    the view has to call :func:`get_flashed_messages`.

    :param message: the message to be flashed.
    :param category: optional classification of the message.
    """
    session = request.session
    msg = {'msg': message, 'cat': category, 'extra': extra}
    session.setdefault(LOCAL_FLASHES, []).append(msg)


def get_messages():
    """Pulls all flashed messages from the session and returns them.
    Further calls in the same request to the function will return
    the same messages.
    """
    flashes = getattr(local, LOCAL_FLASHES, None)
    if flashes is None:
        request = local.request
        flashes = request.session.get(LOCAL_FLASHES, [])
        setattr(local, LOCAL_FLASHES, flashes)
        if flashes:
            del request.session[LOCAL_FLASHES]
    return flashes or []


CSRF_FORM_NAME = '_csrf'
CSRF_SESSION_NAME = '_c'


class CSRFToken(object):

    name = CSRF_FORM_NAME

    def __init__(self):
        value = hashlib.md5(os.urandom(32)).hexdigest()[:16]
        self.value = to64(int(value, 16))

    @property
    def input(self):
        return '<input type="hidden" name="%s" value="%s">' \
            % (self.name, self.value)
    
    @property
    def query(self):
        return '%s=%s' % (self.name, self.value)

    def __repr__(self):
        return '<CSRFToken %s = "%s">' % (self.name, self.value)


def get_csrf_secret(request):
    """Use it to prevent Cross Site Request Forgery (CSRF) attacks."""
    csrf_secret = request.session.get(CSRF_SESSION_NAME)
    if not csrf_secret:
        csrf_secret = new_csrf_secret(request)
    return csrf_secret


def new_csrf_secret(request):
    csrf_secret = CSRFToken()

    request.session[CSRF_SESSION_NAME] = csrf_secret
    return csrf_secret


class Render(object):

    default_globals = {
        'ellipsis': Ellipsis,
        'now': LocalProxy(datetime.utcnow),
        'media': media,
        'get_messages': get_messages,
        'flash_messages': LocalProxy(get_messages),
        'request': local('request'),
        'settings': LocalProxy(lambda: local.app.settings),
        'url_for': url_for,
        'csrf_secret': LocalProxy(lambda: get_csrf_secret(local.request)),
        }

    default_tests = {
        # Test for the mysterious Ellipsis object :P
        'ellipsis': (lambda obj: obj == Ellipsis),
        }
    
    default_filters = {}

    def __init__(self, views_path=None, loader=None, default='text/html',
            **kwargs):
        filters = kwargs.pop('filters', {})
        tests = kwargs.pop('tests', {})
        tglobals = kwargs.pop('globals', {})
        self.default = default

        if views_path and not loader:
            loader = jinja2.FileSystemLoader(views_path)

        kwargs.setdefault('autoescape', False)

        env = jinja2.Environment(loader=loader, **kwargs)

        env.globals.update(self.default_globals)
        env.globals.update(tglobals)
        
        env.globals.update(self.default_filters)
        env.filters.update(filters)

        env.tests.update(self.default_tests)
        env.tests.update(tests)

        self.env = env
        self._loader = None

    def load_alt_loader(self, alt_loader):
        if alt_loader:
            self._loader = loader = self.env.loader
            self.env.loader = jinja2.ChoiceLoader([loader, alt_loader])
    
    def unload_alt_loader(self):
        if self._loader:
            self.env.loader = self._loader
            self._loader = None

    def to_string(self, view_template, dcontext=None, alt_loader=None, **context):
        if not context and isinstance(dcontext, dict):
            context = dcontext
        self.load_alt_loader(alt_loader)
        tmpl = self.env.get_template(view_template)
        result = tmpl.render(context)
        self.unload_alt_loader()
        return result

    def from_string(self, source, dcontext=None, **context):
        if not context and isinstance(dcontext, dict):
            context = dcontext
        tmpl = self.env.from_string(source)
        return tmpl.render(context)

    def to_stream(self, view_template, dcontext=None, alt_loader=None, **context):
        if not context and isinstance(dcontext, dict):
            context = dcontext
        self.load_alt_loader(alt_loader)
        tmpl = self.env.get_template(view_template)
        result = tmpl.stream(context)
        self.unload_alt_loader()
        return result

    def __call__(self, view_template, dcontext=None, alt_loader=None, **context):
        self.load_alt_loader(alt_loader)
        tmpl = self.env.get_template(view_template)
        if not context and isinstance(dcontext, dict):
            context = dcontext
        result = tmpl.render(context)
        self.unload_alt_loader()
        mimetype = context.pop('mimetype', self.default)        
        response_class = local.app.response_class
        return response_class(result, mimetype=mimetype)

    def get_global(self, name):
        return self.env.globals[name]

    def set_global(self, name, value):
        self.env.globals[name] = value

    def get_filter(self, name):
        return self.env.filters[name]

    def set_filter(self, name, value):
        self.env.filters[name] = value

    def get_test(self, name):
        return self.env.tests[name]

    def set_test(self, name, value):
        self.env.tests[name] = value


default_loader = jinja2.PackageLoader('shake', 'default_views')
default_render = Render(loader=default_loader)
