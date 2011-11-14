# -*- coding: utf-8 -*-
"""
# shake.controllers

Generic controllers


--------------------------------
Copyright © 2010-2011 by Lúcuma labs (http://lucumalabs.com).

MIT License. (http://www.opensource.org/licenses/mit-license.php)

"""
from random import choice

from .config import QUOTES
from .helpers import local
from .views import default_render


def not_found_page(request, error):
    """Default "Not Found" page.
    """
    rules = local.urls.map._rules
    return default_render('not_found.html', rules=rules)


def error_page(request, error):
    """A generic error page.
    """
    return default_render('error.html')


def not_allowed_page(request, error):
    """A default "access denied" page.
    """
    return default_render('not_allowed.html')


def welcome_page(request, *args, **kwargs):
    """A default "welcome to shake" page.
    """
    tmpl = 'welcome.html'
    quote = choice(QUOTES)
    lang = request.args.get('lang', '')
    if not lang:
        lang = request.accept_languages.best \
            or request.user_agent.language or ''
        lang = lang.split('-')[0]
    if lang == 'es':
        tmpl = 'welcome-es.html'
    return default_render(tmpl, quote=quote)


def render_view(request, render, view, **kwargs):
    """A really simple controller who render directly a view.
    
    :param render: The view renderer to use.
    :param kwargs: Values to add to the view context.
    """
    return render(view, **kwargs)

