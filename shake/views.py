# -*- coding: utf-8 -*-
"""
    # Shake.views

    Implements the bridge to Jinja2.

"""
from datetime import datetime
import hashlib
import io
import os

import jinja2
from jinja2.exceptions import TemplateNotFound
from werkzeug.local import LocalProxy
import yaml

from .helpers import local, url_for, to64, plural, StorageDict
from .wrappers import Response, LOCAL_FLASHES


VIEWS_DIR = 'views'
LOCAL_I18N_STRINGS = '_i18ns'


def flash(request, msg, cat='info', extra=None, **kwargs):
    """Flashes a message to the next request.  In order to remove the
    flashed message from the session and to display it to the user,
    the view has to call :func:`get_flashed_messages`.
    
    :param message: the message to be flashed.
    :param category: optional classification of the message.
    """
    request.flash(msg=msg, cat=cat, extra=extra, kwargs=kwargs)


def get_messages(request=None):
    """Pulls all flashed messages from the session and returns them.
    Further calls in the same request to the function will return
    the same messages.
    """
    flashes = getattr(local, LOCAL_FLASHES, None)
    if not flashes:
        request = request or local.request
        flashes = request.session.get(LOCAL_FLASHES) or []
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
        return jinja2.safe('<input type="hidden" name="%s" value="%s">'
            % (self.name, self.value))
    
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


class BaseRender(object):
    
    default_globals = {
        'ellipsis': Ellipsis, # Easter egg?
        'plural': plural,
        'now': LocalProxy(datetime.utcnow),

        'url_for': url_for,
        'flash_messages': LocalProxy(get_messages),
        'csrf_secret': LocalProxy(lambda: get_csrf_secret(local.request)), # Deprecated
        'csrf': LocalProxy(lambda: get_csrf_secret(local.request)),

        'request': local('request'),
        'settings': LocalProxy(lambda: local.app.settings),

        'get_messages': get_messages,
        }
    
    # The class that is used for response objects.
    response_class = Response

    def __init__(self, default_mimetype='text/html', i18n=None,
            default_language='es-US'):
        self.default_mimetype = default_mimetype
        self.i18n_dir = i18n
        self.default_language = default_language
        self.default_globals['i18n'] = LocalProxy(self.get_18n_strings)
    
    def _get_template(self, filename):
        raise NotImplementedError
    
    def _render(self, tmpl, context):
        raise NotImplementedError
    
    def __call__(self, filename, dcontext=None, mimetype=None,
            headers=None, **context):
        tmpl = self._get_template(filename)
        if not context and isinstance(dcontext, dict):
            context = dcontext
        result = self._render(tmpl, context)
        mimetype = mimetype or self.default_mimetype
        response_class = self.response_class
        resp = response_class(result, mimetype=mimetype)
        headers = headers or {}
        for key, val in headers.items():
            resp.headers[key] = val
        return resp
    
    def load_i18n_strings(self, lang_s, lang):
        if not self.i18n_dir:
            return None
        lang = lang.replace('-', '_')
        filename = os.path.join(self.i18n_dir, lang + '.yml')
        if not os.path.isfile(filename):
            if lang == lang_s:
                return
            filename = os.path.join(self.i18n_dir, lang_s + '.yml')
        
        try:
            with io.open(filename) as f:
                strings = yaml.safe_load(f)
            return StorageDict(strings, _default_value=u'',
                _case_insensitive=True)
        except (IOError, AttributeError):
            return
    
    def get_18n_strings(self):
        lang_s, lang = local.request.get_language(self.default_language)
        strings = getattr(local, LOCAL_I18N_STRINGS, None)
        if not strings:
            strings = self.load_i18n_strings(lang_s, lang)
            if strings:
                setattr(local, LOCAL_I18N_STRINGS, strings)
        return strings


class Render(BaseRender):
    
    default_tests = {
        # Test for the mysterious Ellipsis object.
        # whose mystery is only exceeded by its power :P
        'ellipsis': (lambda obj: obj == Ellipsis),
        }
    
    default_filters = {}
    
    def __init__(self, views_path=None, loader=None,
            default_mimetype='text/html',
            i18n=None, default_language='es-US', **kwargs):
        
        BaseRender.__init__(self, default_mimetype=default_mimetype,
            i18n=i18n, default_language=default_language)
        filters = kwargs.pop('filters', {})
        tests = kwargs.pop('tests', {})
        tglobals = kwargs.pop('globals', {})
        
        if views_path:
            views_path = os.path.normpath(os.path.realpath(views_path))
            # Instead of a path, we've probably recieved the value of __file__
            if not os.path.isdir(views_path):
                views_path = os.path.join(os.path.dirname(views_path), 
                    VIEWS_DIR)
        
        if views_path and not loader:
            loader = jinja2.FileSystemLoader(views_path)
        
        kwargs.setdefault('autoescape', True)
        
        env = jinja2.Environment(loader=loader, **kwargs)
        
        env.globals.update(self.default_globals)
        env.globals.update(tglobals)
        
        env.globals.update(self.default_filters)
        env.filters.update(filters)
        
        env.tests.update(self.default_tests)
        env.tests.update(tests)
        
        self.env = env
        self._loader = None
    
    def _get_template(self, filename):
        return self.env.get_template(filename)
    
    def _render(self, tmpl, context):
        return tmpl.render(context)
    
    def to_string(self, filename, dcontext=None, **context):
        if not context and isinstance(dcontext, dict):
            context = dcontext
        tmpl = self._get_template(filename)
        return self._render(tmpl, context)
    
    def from_string(self, source, dcontext=None, **context):
        if not context and isinstance(dcontext, dict):
            context = dcontext
        tmpl = self.env.from_string(source)
        return self._render(tmpl, context)
    
    def to_stream(self, filename, dcontext=None, **context):
        if not context and isinstance(dcontext, dict):
            context = dcontext
        tmpl = self._get_template(filename)
        return tmpl.stream(context)
    
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
    
    def add_extension(self, ext):
        self.env.add_extension(ext)


default_loader = jinja2.PackageLoader('shake', 'default_views')
default_render = Render(loader=default_loader)
