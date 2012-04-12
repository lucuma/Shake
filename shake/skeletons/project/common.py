# -*- coding: utf-8 -*-
"""
General controllers
"""
import shake

from main import render


def index(request):
    return render('index.html', locals())


def not_found(request, error):
    return render('error_notfound.html', locals())


def critical_error(request, error=None):
    return render('error.html', locals())


def not_allowed(request, error):
    return render('error_notallowed.html', locals())
