# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from os.path import join, dirname

import jinja2
import pytest
from shake import (Shake, Request, Response, Render, local, ViewNotFound)
from shake import (flash, get_messages, get_csrf, new_csrf, link_to)
from werkzeug.test import EnvironBuilder


HTTP_OK = 200

views_dir = join(dirname(__file__), 'res')
static_dir = join(dirname(__file__), 'static')


def test_render():
    render = Render(views_dir)
    local.app = Shake()
    
    resp = render('view.html')
    assert isinstance(resp, Response)
    assert resp.data == '<h1>Hello World</h1>'


def test_to_string():
    render = Render(views_dir)

    resp = render('view.txt',
        {'who': 'E.T.', 'action': 'phone', 'where':'home'},
        to_string=True
    )
    assert resp == 'E.T. phone home'


def test_from_string():
    render = Render()

    resp = render.from_string(
        'Testing, {{ a }} {{ b }} {{ c }}...',
        {'a': 1, 'b': '2', 'c': '3'},
        to_string=True
    )
    assert resp == 'Testing, 1 2 3...'


def test_view_not_found():
    render = Render(views_dir)
    
    with pytest.raises(ViewNotFound):
        render('x_x')


def test_default_mimetype():
    render1 = Render(views_dir)
    render2 = Render(views_dir, default_mimetype='foo/bar')
    local.app = Shake()
    
    resp = render1('view.html')
    assert resp.mimetype == 'text/html'

    resp = render2('view.html')
    assert resp.mimetype == 'foo/bar'


def test_globals():
    gg = {'who': 'E.T.', 'action': 'phone', 'where': 'home'}
    render = Render(globals=gg)

    tmpl = '{{ who }} {{ action }} {{ where }}'
    resp = render.from_string(tmpl, to_string=True)
    assert resp == 'E.T. phone home'


def test_filters():
    
    def double(val):
        return val * 2
    
    def cut(text):
        return text[:3]
    
    ff = {'double': double, 'cut': cut}
    render = Render(filters=ff)

    tmpl = '{{ 45|double }} {{ "abcytfugj"|cut }}'
    resp = render.from_string(tmpl, to_string=True)
    assert resp == '90 abc'


def test_tests():
    
    def gt_3(val):
        return val > 3
    
    tt = {'gt_3': gt_3}
    render = Render(tests=tt)

    tmpl = '{% if 6 is gt_3 %}ok{% endif %}{% if 1 is gt_3 %} FAIL{% endif %}'
    resp = render.from_string(tmpl, to_string=True)
    assert resp == 'ok'


def test_csrf_token():
    render = Render()
    settings = {'SECRET_KEY': 'abc'*20}
    local.app = Shake(settings)
    request = get_test_request()

    csrf1 = get_csrf(request).value
    csrf2 = new_csrf(request).value
    csrf2_ = get_csrf(request).value
    assert csrf2 != csrf1
    assert csrf2_ == csrf2


def test_csrf_token_global():
    render = Render()
    settings = {'SECRET_KEY': 'abc'*20}
    local.app = Shake(settings)
    local.request = get_test_request()
    
    csrf = get_csrf()
    tmpl = '{{ csrf.name }} {{ csrf.value }}'
    resp = render.from_string(tmpl, to_string=True)
    expected = '%s %s' % (csrf.name, csrf.value)
    assert resp == expected


def test_csrf_token_input():
    render = Render()
    settings = {'SECRET_KEY': 'abc'*20}
    local.app = Shake(settings)
    local.request = get_test_request()
    
    csrf = get_csrf()
    tmpl = '{{ csrf.input }}'
    resp = render.from_string(tmpl, to_string=True)
    expected = '<input type="hidden" name="%s" value="%s">' \
            % (csrf.name, csrf.value)
    assert resp == expected


def test_csrf_token_query():
    render = Render()
    settings = {'SECRET_KEY': 'abc'*20}
    local.app = Shake(settings)
    local.request = get_test_request()
    
    csrf = get_csrf()
    tmpl = '{{ csrf.query }}'
    resp = render.from_string(tmpl, to_string=True)
    expected = '%s=%s' % (csrf.name, csrf.value)
    assert resp == expected


def test_render_load_strings():
    render = Render(strings=views_dir)
    
    s = render.load_strings('en')
    assert s['HELLO'] == 'Hello World'

    s = render.load_strings('en-US')
    assert s['HELLO'] == 'Hi'

    s = render.load_strings('es-AR')
    assert s['HELLO'] == 'Hola mundo'
    s2 = render.load_strings('es')
    assert s == s2

    s = render.load_strings('en')
    assert s['FOOBAR'] == ''


def test_link_to():
    path = '/foo/bar/'
    local.request = get_test_request(path)

    html = link_to('Hello', '/hello/', title='click me')
    expected = u'<a href="/hello/" title="click me">Hello</a>'
    assert expected == html

    html = link_to('Bar', path)
    expected = u'<a href="/foo/bar/" class="active">Bar</a>'
    assert expected == html

    html = link_to('Bar', '/foo/')
    expected = u'<a href="/foo/" class="active">Bar</a>'
    assert expected == html


# -----------------------------------------------------------------------------

def get_test_env(path, **kwargs):
    builder = EnvironBuilder(path=path, **kwargs)
    return builder.get_environ()


def get_test_request(path='/', **kwargs):
    env = get_test_env(path, **kwargs)
    return Request(env)


# def pytest_funcarg__render(request):


