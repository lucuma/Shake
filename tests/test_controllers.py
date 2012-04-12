# -*- coding: utf-8 -*-
"""
# shake.tests.test_controllers

Copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
MIT License. (http://www.opensource.org/licenses/mit-license.php)
"""
import os

import pytest
from shake import Shake, Rule, Render, Forbidden
from shake.controllers import (not_found_page, error_page, not_allowed_page,
    render_view)


HTTP_OK = 200
HTTP_FOUND = 302
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_ERROR = 500


views_dir = os.path.join(os.path.dirname(__file__), 'res')
render = Render(views_dir)


def index(request):
    return 'hello'


def fail(request):
    """Controller designed to fail. """
    assert False


def no_pass(request):
    raise Forbidden
    

def test_default_not_found():
    urls = [
        Rule('/', index),
        ]
    settings = {
        'PAGE_NOT_FOUND': not_found_page,
        }
    app = Shake(urls, settings)
    c = app.test_client()
    
    resp = c.get('/bla')
    assert resp.status_code == HTTP_NOT_FOUND
    assert '<title>Page not found</title>' in resp.data


def test_default_error():
    urls = [
        Rule('/', fail),
        ]
    settings = {
        'DEBUG': False,
        'PAGE_ERROR': error_page,
        }
    app = Shake(urls, settings)
    c = app.test_client()
    
    resp = c.get('/')
    assert resp.status_code == HTTP_ERROR
    assert '<title>Error</title>' in resp.data


def test_default_not_allowed():
    urls = [
        Rule('/', no_pass),
        ]
    settings = {
        'PAGE_NOT_ALLOWED': not_allowed_page,
        }
    app = Shake(urls, settings)
    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == HTTP_FORBIDDEN
    assert '<title>Access Denied</title>' in resp.data


def test_render_view_controller():
    urls = [
        Rule('/', render_view,
            defaults={'render': render, 'view': 'view.html'}),
        ]
    app = Shake(urls)
    
    c = app.test_client()
    resp = c.get('/')
    assert resp.data == '<h1>Hello World</h1>'
    assert resp.mimetype == 'text/html'


def test_render_view_controller_args():
    urls = [
        Rule('/', render_view,
            defaults={
                'render': render,
                'view': 'view.txt',
                'mimetype': 'foo/bar',
                'who': 'You',
                'action': 'are',
                'where': 'here',
            }),
        ]
    app = Shake(urls)
    
    c = app.test_client()
    resp = c.get('/')
    assert resp.data == 'You are here'
    assert resp.mimetype == 'foo/bar'
