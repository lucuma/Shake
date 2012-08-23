# -*- coding: utf-8 -*-
"""
    Shake.render
    --------------------------

    Implements the bridge to Jinja2.

"""
from collections import defaultdict
from datetime import datetime
import io
from os.path import isdir, dirname, join, abspath, normpath, realpath

import jinja2
from werkzeug.local import LocalProxy

from .helpers import url_for, local
from .session import get_csrf, get_messages
from .templates import link_to, dumb_plural
from .wrappers import Response, make_response


__all__ = (
    'Render',
)


TEMPLATES_DIR = 'templates'


class Render(object):
    """A thin wrapper arround Jinja2.
    """

    default_globals = {
        'now': LocalProxy(datetime.utcnow),
        'ellipsis': Ellipsis,
        'enumerate': enumerate,

        'request': local('request'),
        'settings': LocalProxy(lambda: local.app.settings),
        'csrf': LocalProxy(get_csrf),
        'url_for': url_for,
        'get_messages': get_messages,

        'link_to': link_to,
        'plural': dumb_plural,

        # Deprecated. Will go away in v1.3
        'csrf_secret': LocalProxy(get_csrf),
    }

    default_extensions = []

    default_filters = {}
    
    default_tests = {
        'ellipsis': (lambda obj: obj == Ellipsis),
    }
    

    def __init__(self, templates_path=None, loader=None,
            default_mimetype='text/html', response_class=Response, **kwargs):
        """

        templates_path
        :   optional path to the folder from where the templates will be loaded.
            Internally a `jinja2.FileSystemLoader` will be constructed.
            You can ignore this parameter and provide a `loader` instead.
        loader
        :   optional replacement loader for the templates.  If provided,
            `templates_path` is ignored.
        default_mimetype
        :   the default MIMETYPE of the response.
        response_class
        :   the `Response` class used by `render`.
        kwargs
        :   extra parameters passed directly to the `jinja2.Environment`
            constructor.

        """
        if not loader:
            templates_path = templates_path or TEMPLATES_DIR
            templates_path = normpath(abspath(realpath(templates_path)))
            # Instead of a path, we've probably recieved the value of __file__
            if not isdir(templates_path):
                templates_path = join(dirname(templates_path), TEMPLATES_DIR)
            loader = jinja2.FileSystemLoader(templates_path)
        
        tglobals = kwargs.pop('globals', {})
        tfilters = kwargs.pop('filters', {})
        ttests = kwargs.pop('tests', {})
        kwargs.setdefault('extensions', self.default_extensions)
        kwargs.setdefault('autoescape', True)

        env = jinja2.Environment(loader=loader, **kwargs)

        env.globals.update(self.default_globals)
        env.globals.update(tglobals)
        env.globals.update(self.default_filters)
        env.filters.update(tfilters)
        env.tests.update(self.default_tests)
        env.tests.update(ttests)

        self.env = env
        self.default_mimetype = default_mimetype
        self.response_class = response_class
    

    def render(self, tmpl, context=None, to_string=False, **kwargs):
        """Render a template `tmpl` using the given `context`.
        If `to_string` is True, the result is returned as is.
        If not, is used to build a response along with the other parameters.

        """
        context = context or {}
        result = tmpl.render(context)
        if to_string:
            return result
        kwargs.setdefault('mimetype', self.default_mimetype)
        return make_response(result, response_class=self.response_class, **kwargs)


    def __call__(self, filename, context=None, to_string=False, **kwargs):
        """Load a template from `<templates_path>/<filename>` and passes it to
        `render` along with the other parameters.

        Depending of the value of `to_string`, returns the rendered template as
        a string or as a response_class instance.

        """
        tmpl = self.env.get_template(filename)
        return self.render(tmpl, context=context, to_string=to_string, **kwargs)

    
    def from_string(self, source, context=None, to_string=False, **kwargs):
        """Parses the `source` given and build a Template from it.
        The template and the other parameters are passed to `Render.render`
        along with the other parameters.

        Depending of the value of `to_string`, returns the rendered template as
        a string or as a response_class instance.

        """
        tmpl = self.env.from_string(source)
        return self.render(tmpl, context=context, to_string=to_string, **kwargs)


default_loader = jinja2.PackageLoader('shake', 'default_templates')
default_render = Render(loader=default_loader)

