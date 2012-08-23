# -*- coding: utf-8 -*-
"""
    Common views
    -------------------------------
    
"""
import shake

from main import app, db
from . import models as m


def index(request):
    return app.render('index.html', locals())


def not_found(request, error):
    return app.render('common/error_notfound.html', locals())


def server_error(request, error=None):
    return app.render('common/error.html', locals())


def not_allowed(request, error):
    return app.render('common/error_notallowed.html', locals())
