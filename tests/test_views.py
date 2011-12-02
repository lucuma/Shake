# -*- coding: utf-8 -*-
"""
# shake.tests.test_views

Copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
MIT License. (http://www.opensource.org/licenses/mit-license.php)
"""
from datetime import datetime, timedelta
import os

import jinja2
import pytest
from shake import (Shake, Rule, Render, ViewNotFound, flash, get_messages,
    get_csrf_secret, new_csrf_secret, local)


HTTP_OK = 200

views_dir = os.path.join(os.path.dirname(__file__), 'res')
static_dir = os.path.join(os.path.dirname(__file__), 'static')


def test_render():
    render = Render(views_dir)
    
    resp = render.to_string('view.html')
    assert resp == '<h1>Hello World</h1>'
    resp = render.to_string('view.txt',
        who='E.T.', action='phone', where='home')
    assert resp == 'E.T. phone home'


def test_view_not_found():
    render = Render(views_dir)
    
    with pytest.raises(ViewNotFound):
        render('x_x')


def test_from_to_string():
    render = Render()
    tmpl = 'Testing, {{ a }} {{ b }} {{ c }}...'
    resp = render.from_string(tmpl, a=1, b='2', c='3')
    assert resp == 'Testing, 1 2 3...'


def test_mimetype():
    render1 = Render(views_dir)
    render2 = Render(views_dir, default_mimetype='foo/bar')
    
    def t1(request):
        resp = render1('view.html')
        assert isinstance(resp, local.app.response_class)
        assert resp.mimetype == 'text/html'
    
    def t2(request):
        resp = render2('view.html')
        assert isinstance(resp, local.app.response_class)
        assert resp.mimetype == 'foo/bar'
    
    urls = [
        Rule('/t1', t1),
        Rule('/t2', t2),
        ]
    app = Shake(urls)
    local.app = app
    c = app.test_client()
    c.get('/t1')
    c.get('/t2')


def test_globals():
    gg = {'who': 'E.T.', 'action': 'phone', 'where': 'home'}
    render = Render(globals=gg)
    tmpl = '{{ who }} {{ action }} {{ where }}'
    resp = render.from_string(tmpl)
    assert resp == 'E.T. phone home'


def test_filters():
    
    def double(val):
        return val * 2
    
    def cut(text):
        return text[:3]
    
    ff = {'double': double, 'cut': cut}
    render = Render(filters=ff)
    tmpl = '{{ 45|double }} {{ "abcytfugj"|cut }}'
    resp = render.from_string(tmpl)
    assert resp == '90 abc'


def test_tests():
    
    def gt_3(val):
        return val > 3
    
    tt = {'gt_3': gt_3}
    render = Render(tests=tt)
    tmpl = '{% if 6 is gt_3 %}ok{% endif %}{% if 1 is gt_3 %} FAIL{% endif %}'
    resp = render.from_string(tmpl)
    assert resp == 'ok'


def test_set_get_globals():
    gg = {'who': 'E.T.', 'action': 'phone', 'where': 'home'}
    render = Render()
    render.set_global('who', 'E.T.')
    render.set_global('action', 'phone')
    render.set_global('where', 'home')
    
    tmpl = '{{ who }} {{ action }} {{ where }}'
    resp = render.from_string(tmpl)
    assert resp == 'E.T. phone home'
    
    assert render.get_global('who') == 'E.T.'
    assert render.get_global('action') == 'phone'
    assert render.get_global('where') == 'home'


def test_set_get_filters():
    
    def double(val):
        return val * 2
    
    def cut(text):
        return text[:3]
    
    render = Render()
    render.set_filter('double', double)
    render.set_filter('cut', cut)
    
    tmpl = '{{ 45|double }} {{ "abcytfugj"|cut }}'
    resp = render.from_string(tmpl)
    assert resp == '90 abc'
    
    assert render.get_filter('double') == double
    assert render.get_filter('cut') == cut


def test_set_get_tests():
    
    def gt_3(val):
        return val > 3
    
    render = Render()
    render.set_test('gt_3', gt_3)
    
    tmpl = '{% if 6 is gt_3 %}ok{% endif %}{% if 1 is gt_3 %} FAIL{% endif %}'
    resp = render.from_string(tmpl)
    assert resp == 'ok'
    
    assert render.get_test('gt_3') == gt_3


def test_default_tests():
    render = Render()
    tmpl = '{% if value is ellipsis %}ok{% endif %}'
    resp = render.from_string(tmpl, value=Ellipsis)
    assert resp == 'ok'


def test_default_globals():
    render = Render()
    
    def foo(request):
        tmpl = '{{ media }}{{ request }}{{ settings }}'
        render.from_string(tmpl)
    
    urls = [
        Rule('/', foo),
        ]
    app = Shake(urls)
    c = app.test_client()
    c.get('/')


def test_default_globals_now():
    render = Render()
    tmpl = '{{ now }}'
    snow = str(datetime.utcnow())[:-10]
    assert render.from_string(tmpl).startswith(snow)


def test_default_globals_flash_messages():
    render = Render()
    
    def foo(request):
        flash(request, 'foo')
        tmpl = '{% for fm in get_messages() %}{{ fm.msg }}{% endfor %}'
        assert render.from_string(tmpl) == 'foo'
    
    urls = [
        Rule('/', foo),
        ]
    settings = {'SECRET_KEY': 'abc'*20}
    app = Shake(urls, settings)
    c = app.test_client()
    c.get('/')


def test_default_globals_url_for():
    render = Render()
    
    def foo(request):
        tmpl = "{{ url_for('foo') }}"
        assert render.from_string(tmpl) == '/'
    
    urls = [
        Rule('/', foo, name='foo'),
        ]
    app = Shake(urls)
    c = app.test_client()
    c.get('/')


def test_flash_messagesech():
    
    def t1(request):
        msgs = get_messages()
        assert msgs == []
    
    def t2(request):
        flash(request, 'foo')
        flash(request, 'bar', 'error', extra='blub')
        msgs = get_messages()
        assert len(msgs) == 2
        assert (msgs[0]['msg'], msgs[0]['cat'], msgs[0]['extra']) == \
            ('foo', 'info', None)
        assert (msgs[1]['msg'], msgs[1]['cat'], msgs[1]['extra']) == \
            ('bar', 'error', 'blub')
        msgs2 = get_messages()
        assert msgs2 == msgs
    
    urls = [
        Rule('/t1', t1),
        Rule('/t2', t2),
        ]
    settings = {'SECRET_KEY': 'abc'*20}
    app = Shake(urls, settings)
    c = app.test_client()
    c.get('/t1')
    c.get('/t2')


def test_csrf_token():
    render = Render()
    
    def t(request):
        csrf1 = get_csrf_secret(request).value
        csrf2 = new_csrf_secret(request).value
        csrf2_ = get_csrf_secret(request).value
        assert csrf2 != csrf1
        assert csrf2_ == csrf2
    
    urls = [
        Rule('/', t),
        ]
    settings = {'SECRET_KEY': 'abc'*20}
    app = Shake(urls, settings)
    c = app.test_client()
    c.get('/')


def test_csrf_token_global():
    render = Render()
    
    def t(request):
        csrf = get_csrf_secret(request)
        tmpl = '{{ csrf_secret.name }} {{ csrf_secret.value }}'
        assert render.from_string(tmpl) == '%s %s' % (csrf.name, csrf.value)
    
    urls = [
        Rule('/', t),
        ]
    settings = {'SECRET_KEY': 'abc'*20}
    app = Shake(urls, settings)
    c = app.test_client()
    c.get('/')


def test_csrf_token_input():
    render = Render()
    
    def t(request):
        csrf = get_csrf_secret(request)
        tmpl = '{{ csrf_secret.input }}'
        expected = '<input type="hidden" name="%s" value="%s">' \
            % (csrf.name, csrf.value)
        assert render.from_string(tmpl) == expected
    
    urls = [
        Rule('/', t),
        ]
    settings = {'SECRET_KEY': 'abc'*20}
    app = Shake(urls, settings)
    c = app.test_client()
    c.get('/t')


def test_csrf_token_query():
    render = Render()
    
    def t(request):
        csrf = get_csrf_secret(request)
        tmpl = '{{ csrf_secret.query }}'
        expected = '%s=%s' % (csrf.name, csrf.value)
        assert render.from_string(tmpl) == expected
    
    urls = [
        Rule('/', t),
        ]
    settings = {'SECRET_KEY': 'abc'*20}
    app = Shake(urls, settings)
    c = app.test_client()
    c.get('/t')


def test_i18n():
    render = Render(i18n=views_dir)
    
    def ok(request):
        return render.from_string('{{ i18n.HELLO }}')
    
    def fail(request):
        return render.from_string('{{ i18n.FOOBAR }}')
    
    urls = [
        Rule('/ok/', ok),
        Rule('/fail/', fail),
    ]
    app = Shake(urls)
    c = app.test_client()

    resp = c.get('/ok/?lang=en-US')
    assert resp.status_code == HTTP_OK
    assert resp.data == 'Hello World'

    resp = c.get('/ok/?lang=en_US')
    assert resp.status_code == HTTP_OK
    assert resp.data == 'Hello World'

    resp = c.get('/ok/?lang=es-AR')
    assert resp.data == 'Hola mundo'

    resp = c.get('/fail/?lang=en-US')
    assert resp.data == ''

