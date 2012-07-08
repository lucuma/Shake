# -*- coding: utf-8 -*-
"""
    Shake.views
    --------------------------

    Implements the bridge to Jinja2.

"""
from collections import defaultdict
from datetime import datetime
import io
import os

import jinja2
from werkzeug.local import LocalProxy

from .babel import (get_translations,
    format_datetime, format_date, format_time, format_timedelta,
    format_number, format_decimal, format_currency, format_percent,
    format_scientific)
from .helpers import local, url_for
from .session import get_csrf, get_messages
from .templates import plural, link_to


__all__ = (
    'Render',
)


VIEWS_DIR = 'views'


class Render(object):
    """A thin wrapper arround Jinja2.

    """

    default_globals = {
        'request': local('request'),
        'settings': local('app.settings'),
        'now': LocalProxy(datetime.utcnow),
        'csrf': LocalProxy(get_csrf),
        'url_for': url_for,
        'get_messages': get_messages,
        'plural': plural,
        'link_to': link_to,
    }

    default_filters = {
        'datetimeformat': format_datetime,
        'dateformat': format_date,
        'timeformat': format_time,
        'timedeltaformat': format_timedelta,
        'numberformat': format_number,
        'decimalformat': format_decimal,
        'currencyformat': format_currency,
        'percentformat': format_percent,
        'scientificformat': format_scientific,
    }
    
    default_tests = {
        'ellipsis': (lambda obj: obj == Ellipsis),
    }

    default_extensions = [
        'jinja2.ext.i18n',
    ]
    
    def __init__(self, views_path=None, loader=None,
            default_mimetype='text/html', **kwargs):
        """

        views_path
        :   Optional path to the folder from where the templates will be loaded.
            Internally a `jinja2.FileSystemLoader` will be constructed.
            You can ignore this parameter and provide a `loader` instead.
        loader
        :   Optional replacement loader for the templates.  If provided,
            `views_path` will be ignored.
        default_mimetype
        ;   Used when making a response, if a `mimetype` parameter is not used
            when rendering.
        kwargs
        :   Extra parameters passed directly to the `jinja2.Environment`
            constructor.

        """
        
        self.default_mimetype = default_mimetype

        if not loader:
            views_path = views_path or '.'
            views_path = os.path.normpath(os.path.realpath(views_path))
            # Instead of a path, we've probably recieved the value of __file__
            if not os.path.isdir(views_path):
                views_path = os.path.join(os.path.dirname(views_path), 
                    VIEWS_DIR)
            loader = jinja2.FileSystemLoader(views_path)
        
        tglobals = kwargs.pop('globals', {})
        tfilters = kwargs.pop('filters', {})
        ttests = kwargs.pop('tests', {})
        
        kwargs.setdefault('extensions', self.default_extensions)
        kwargs.setdefault('autoescape', True)

        self.env = env = jinja2.Environment(loader=loader, **kwargs)
        
        env.globals.update(self.default_globals)
        env.globals.update(tglobals)
        env.globals.update(self.default_filters)
        env.filters.update(tfilters)
        env.tests.update(self.default_tests)
        env.tests.update(ttests)
        
        env.install_gettext_callables(
            lambda x: get_translations().ugettext(x),
            lambda s, p, n: get_translations().ungettext(s, p, n),
            newstyle=True
        )

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
        return local.app.make_response(result, **kwargs)

    def __call__(self, filename, context=None, to_string=False, **kwargs):
        """Load a template from `<views_path>/<filename>` and passes it to
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


default_loader = jinja2.PackageLoader('shake', 'default_views')
default_render = Render(loader=default_loader)

