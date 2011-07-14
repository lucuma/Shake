# -*- coding: utf-8 -*-
from shake import redirect, url_for, flash, NotFound

# from shakext.auth import protected

from . import settings
# from .models import db
from .settings import render


def index(request):
    return render('index.html', **locals())


def not_found(request, error):
    return render('not_found.html', **locals())


def critical_error(request, error=None):
    return render('error.html', **locals())
