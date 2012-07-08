# -*- coding: utf-8 -*-
"""
    Common controllers
    -------------------------------
    
"""
import shake

from main import app, render, db
from . import models as m


def index(request):
    return render('index.html', locals())


def not_found(request, error):
    return render('common/error_notfound.html', locals())


def critical_error(request, error=None):
    return render('common/error.html', locals())


def not_allowed(request, error):
    return render('common/error_notallowed.html', locals())
