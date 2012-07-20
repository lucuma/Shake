# -*- coding: utf-8 -*-
import os

import pytest
from shake import Shake, Rule, Render, Forbidden
from shake.views import (not_found_page, error_page, not_allowed_page,
    render_template)


HTTP_OK = 200
HTTP_FOUND = 302
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_ERROR = 500


templates_dir = os.path.join(os.path.dirname(__file__), 'res')
render = Render(templates_dir)


def index(request):
    return 'hello'


def fail(request):
    """View designed to fail. """
    assert False


def no_pass(request):
    raise Forbidden
    

def test_default_not_found():
    settings = {
        'PAGE_NOT_FOUND': not_found_page,
    }
    app = Shake(__file__, settings)
    app.add_url('/', index)
    c = app.test_client()
    
    resp = c.get('/bla')
    assert resp.status_code == HTTP_NOT_FOUND
    assert '<title>Page not found</title>' in resp.data


def test_default_error():
    settings = {
        'DEBUG': False,
        'PAGE_ERROR': error_page,
    }
    app = Shake(__file__, settings)
    app.add_url('/', fail)
    c = app.test_client()
    
    resp = c.get('/')
    assert resp.status_code == HTTP_ERROR
    assert '<title>Error</title>' in resp.data


def test_default_not_allowed():
    settings = {
        'PAGE_NOT_ALLOWED': not_allowed_page,
    }
    app = Shake(__file__, settings)
    app.add_url('/', no_pass)
    c = app.test_client()

    resp = c.get('/')
    assert resp.status_code == HTTP_FORBIDDEN
    assert '<title>Access Denied</title>' in resp.data


def test_render_template_view():
    app = Shake(__file__)
    c = app.test_client()
    app.add_url('/', render_template, 
        defaults={'template': 'tmpl.html', 'render': render})
    
    resp = c.get('/')
    assert resp.data == '<h1>Hello World</h1>'
    assert resp.mimetype == 'text/html'


def test_render_template_view_args():
    app = Shake(__file__)
    app.add_url('/', render_template,
        defaults={
            'render': render,
            'template': 'tmpl.txt',
            'context': {
                'who': 'You',
                'action': 'are',
                'where': 'here',
            },
            'mimetype': 'foo/bar',
        }
    )
    c = app.test_client()

    resp = c.get('/')
    assert resp.data == 'You are here'
    assert resp.mimetype == 'foo/bar'

