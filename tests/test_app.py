# -*- coding: utf-8 -*-
"""
    :copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
    :license: BSD. See LICENSE for more details.
"""
import os
import pytest

from shake import (Shake, abort, redirect, Response, Rule, json, url_for,
    Paginator)


#### Views

def index(request):
    return 'hello'


def no_pass(request):
    abort(401)


# Custom "not found" view
def not_found(request, error):
    return 'not found'


# Custom error view
def error(request, error):
    return 'error'


# Custom access "not allowed" view
def not_allowed(request, error):
    return 'access denied'


# View that always fail
def fail(request):
    assert False


##### Tests

def test_callable_endpoint():
    urls = [
        Rule('/', index),
        ]
    app = Shake(urls)

    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == 200
    assert resp.data == 'hello'


def test_string_endpoint():
    urls = [
        Rule('/', 'tests.test_app.index'),
        ]
    app = Shake(urls)

    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == 200
    assert resp.data == 'hello'


def test_default_response():
    def index(request):
        pass

    urls = [
        Rule('/', index),
        ]
    app = Shake(urls)

    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == 200
    assert resp.data == ''


def test_default_not_found():
    urls = [
        Rule('/', index),
        ]
    app = Shake(urls)

    c = app.test_client()
    resp = c.get('/bla')
    assert resp.status_code == 404
    assert '<title>Page not found</title>' in resp.data


def test_default_error():
    urls = [
        Rule('/', fail),
        ]
    app = Shake(urls)

    c = app.test_client()
    with pytest.raises(AssertionError):
        c.get('/')


def test_default_not_allowed():
    urls = [
        Rule('/', no_pass),
        ]
    app = Shake(urls)

    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == 401
    assert '<title>Access Denied</title>' in resp.data


def test_redirect():
    def redir(request):
        return redirect('/bla')

    urls = [
        Rule('/', redir),
        ]
    app = Shake(urls)

    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == 302


def test_custom_not_found():
    urls = [
        Rule('/', index),
        ]
    settings = {'PAGE_NOT_FOUND': not_found}
    app = Shake(urls, settings)

    c = app.test_client()
    resp = c.get('/bla')
    assert resp.status_code == 404
    assert resp.data == 'not found'


def test_custom_error():
    urls = [
        Rule('/', fail),
        ]
    settings = {'PAGE_ERROR': error, 'DEBUG': False}
    app = Shake(urls, settings)

    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == 500
    assert resp.data == 'error'


def test_custom_not_allowed():
    urls = [
        Rule('/', no_pass),
        ]
    settings = {'PAGE_NOT_ALLOWED': not_allowed}
    app = Shake(urls, settings)

    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == 401
    assert resp.data == 'access denied'


def test_response_response():
    def index(request):
        return Response('hello world')

    urls = [
        Rule('/', index),
        ]
    app = Shake(urls)

    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == 200
    assert resp.mimetype == 'text/plain'
    assert resp.data == 'hello world'


def test_response_string():
    def index(request):
        return 'hello world'

    urls = [
        Rule('/', index),
        ]
    app = Shake(urls)

    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == 200
    assert resp.mimetype == 'text/plain'
    assert resp.data == 'hello world'


def test_response_none():
    def index(request):
        return None

    urls = [
        Rule('/', index),
        ]
    app = Shake(urls)

    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == 200
    assert resp.mimetype == 'text/plain'
    assert resp.data == ''


def test_response_json():
    data = {'foo': 'bar', 'num': 3}

    def index(request):
        return data

    urls = [
        Rule('/', index),
        ]
    app = Shake(urls)

    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == 200
    assert resp.mimetype == 'application/json'
    assert eval(resp.data) == data


def test_is_get():
    def index(request):
        return str(request.is_get)

    urls = [
        Rule('/', index),
        ]
    app = Shake(urls)
    c = app.test_client()

    resp = c.get('/')
    assert resp.data == 'True'

    resp = c.post('/')
    assert resp.data == 'False'


def test_is_post():
    def index(request):
        return str(request.is_post)

    urls = [
        Rule('/', index),
        ]
    app = Shake(urls)
    c = app.test_client()

    resp = c.get('/')
    assert resp.data == 'False'

    resp = c.post('/')
    assert resp.data == 'True'


def test_is_json():
    data = {'foo': 'bar', 'num': 3}

    def index(request):
        return str(request.json)

    urls = [
        Rule('/', index),
        ]
    app = Shake(urls)
    c = app.test_client()

    resp = c.post('/', content_type='application/json', 
        data=json.dumps(data))
    assert eval(resp.data) == data

    resp = c.post('/', data=json.dumps(data))
    assert resp.data == 'None'


def test_response_mimetype():
    def index(request):
        return Response('hello world', mimetype='foo/bar')

    urls = [
        Rule('/', index),
        ]
    app = Shake(urls)

    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == 200
    assert resp.mimetype == 'foo/bar'
    assert resp.data == 'hello world'


def test_processors_order():
    r = []

    def index(request):
        r.append('view')

    def rq1(request):
        r.append('rq1')

    def rq2(request):
        r.append('rq2')

    def rs1(response):
        r.append('rs1')
        return response

    def rs2(response):
        r.append('rs2')
        return response
    
    def error(e):
        r.append('error')

    urls = [
        Rule('/', index),
        ]
    app = Shake(urls)

    app.before_request(rq1)
    app.before_request(rq2)
    app.before_response(rs1)
    app.before_response(rs2)
    app.on_exception(error)

    c = app.test_client()
    c.get('/')

    assert r == ['rq1', 'rq2', 'view', 'rs1', 'rs2']


def test_processors_order_exception():
    r = []

    def index(request):
        r.append('view')
        assert False
    
    def eview(request, error):
        r.append('eview')

    def rq1(request):
        r.append('rq1')

    def rq2(request):
        r.append('rq2')

    def rs1(response):
        r.append('rs1')
        return response

    def rs2(response):
        r.append('rs2')
        return response
    
    def on_error(e):
        r.append('error')

    urls = [
        Rule('/', index),
        ]
    settings = {'PAGE_ERROR': eview, 'DEBUG': False}
    app = Shake(urls, settings)

    app.before_request(rq1)
    app.before_request(rq2)
    app.before_response(rs1)
    app.before_response(rs2)
    app.on_exception(on_error)

    c = app.test_client()
    c.get('/')

    assert r == ['rq1', 'rq2', 'view', 'error', 'eview']


def test_repeated_processors():
    r = []
    
    def index(request):
        r.append('view')
    
    def rq1(request):
        r.append('rq1')

    def rs1(response):
        r.append('rs1')
        return response
    
    def on_error(e):
        r.append('error')
    
    urls = [
        Rule('/', index),
        ]
    app = Shake(urls)
    
    app.before_request(rq1)
    app.before_request(rq1)
    app.before_response(rs1)
    app.before_response(rs1)
    app.on_exception(on_error)
    app.before_request(rq1)
    app.before_response(rs1)
    app.before_request(rq1)
    app.on_exception(on_error)
    c = app.test_client()
    
    c.get('/')
    assert r == ['rq1', 'view', 'rs1']


def test_repeated_processors_exception():
    r = []
    
    def index(request):
        r.append('view')
        assert False

    def eview(request, error):
        r.append('eview')
    
    def rq1(request):
        r.append('rq1')

    def rs1(response):
        r.append('rs1')
        return response
    
    def on_error(e):
        r.append('error')
    
    urls = [
        Rule('/', index),
        ]
    settings = {'PAGE_ERROR': eview, 'DEBUG': False}
    app = Shake(urls, settings)
    
    app.before_request(rq1)
    app.before_request(rq1)
    app.before_response(rs1)
    app.before_response(rs1)
    app.on_exception(on_error)
    app.before_request(rq1)
    app.before_response(rs1)
    app.before_request(rq1)
    app.on_exception(on_error)
    c = app.test_client()

    c.get('/')
    assert r == ['rq1', 'view', 'error', 'eview']


def test_before_response_return():
    def index(request):
        return 'ok'
    
    def brs(response):
        pass
    
    urls = [Rule('/', index)]
    app = Shake(urls)
    app.before_response(brs)
    
    c = app.test_client()
    with pytest.raises(Exception):
        c.get('/')


def test_session():
    def p1(request):
        request.session['foo'] = 'bar'

    def p2(request):
        assert 'bar' == request.session['foo']

    urls = [
        Rule('/p1/', p1),
        Rule('/p2/', p2),
        ]
    settings = {'SECRET_KEY': 'q'*22}
    app = Shake(urls, settings)
    c = app.test_client()

    resp = c.get('/p1/')
    resp = c.get('/p2/')
    assert resp.status_code == 200


def test_session_nosecret():
    def p1(request):
        request.session['foo'] = 'bar'

    urls = [
        Rule('/', p1),
        ]
    app = Shake(urls)
    c = app.test_client()

    with pytest.raises(RuntimeError):
        c.get('/')

