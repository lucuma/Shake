# -*- coding: utf-8 -*-
"""
# shake.tests.test_app

Copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
MIT License. (http://www.opensource.org/licenses/mit-license.php)
"""
import os

import pytest
from shake import (Shake, redirect, Response, Rule, json,
    NotAllowed, BadRequest,
    Unauthorized, Forbidden, NotFound, MethodNotAllowed,
    NotAcceptable, RequestTimeout, Gone,
    LengthRequired, PreconditionFailed, RequestEntityTooLarge,
    RequestURITooLarge, UnsupportedMediaType, InternalServerError,
    NotImplemented, BadGateway, ServiceUnavailable)


HTTP_OK = 200
HTTP_FOUND = 302
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_ERROR = 500

#### Views

def index(request):
    return 'hello'


def no_pass(request):
    raise NotAllowed


def not_found(request, error):
    """Custom "not found" controller."""
    return 'not found'


def error(request, error):
    """Custom error controller."""
    return 'error'


def not_allowed(request, error):
    """Custom access "not allowed" controller."""
    return 'access denied'


def fail(request):
    assert False


##### Tests

def test_add_url():
    
    def number(request, num):
        return str(num)
    
    app = Shake()
    app.add_url('/', index)
    app.add_url('/<int:num>/', number)
    c = app.test_client()
    
    resp = c.get('/')
    assert resp.status_code == HTTP_OK
    assert resp.data == 'hello'
    
    resp = c.get('/3/')
    assert resp.status_code == HTTP_OK
    assert resp.data == '3'


def test_add_urls():
    
    def number(request, num):
        return str(num)
    
    urls = [
        Rule('/', index),
        Rule('/<int:num>/', number),
        ]
    app = Shake()
    app.add_urls(urls)
    c = app.test_client()
    
    resp = c.get('/')
    assert resp.status_code == HTTP_OK
    assert resp.data == 'hello'
    
    resp = c.get('/3/')
    assert resp.status_code == HTTP_OK
    assert resp.data == '3'


def test_callable_endpoint():
    urls = [
        Rule('/', index),
        ]
    app = Shake(urls)
    
    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == HTTP_OK
    assert resp.data == 'hello'


def test_string_endpoint():
    urls = [
        Rule('/', 'tests.test_app.index'),
        ]
    app = Shake(urls)
    
    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == HTTP_OK
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
    assert resp.status_code == HTTP_OK
    assert resp.data == ''


def test_default_not_found():
    urls = [
        Rule('/', index),
        ]
    app = Shake(urls)
    
    c = app.test_client()
    resp = c.get('/bla')
    assert resp.status_code == HTTP_NOT_FOUND
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
    assert resp.status_code == HTTP_FORBIDDEN
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
    assert resp.status_code == HTTP_FOUND


def test_custom_not_found():
    urls = [
        Rule('/', index),
        ]
    settings = {'PAGE_NOT_FOUND': not_found}
    app = Shake(urls, settings)
    
    c = app.test_client()
    resp = c.get('/bla')
    assert resp.status_code == HTTP_NOT_FOUND
    assert resp.data == 'not found'


def test_custom_error():
    urls = [
        Rule('/', fail),
        ]
    settings = {'PAGE_ERROR': error, 'DEBUG': False}
    app = Shake(urls, settings)
    
    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == HTTP_ERROR
    assert resp.data == 'error'


def test_custom_not_allowed():
    urls = [
        Rule('/', no_pass),
        ]
    settings = {'PAGE_NOT_ALLOWED': not_allowed}
    app = Shake(urls, settings)
    
    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == HTTP_FORBIDDEN
    assert resp.data == 'access denied'


def test_error_codes():
    errors = {
        400: BadRequest,
        401: Unauthorized,
        403: Forbidden,
        404: NotFound,
        405: MethodNotAllowed,
        406: NotAcceptable,
        408: RequestTimeout,
        410: Gone,
        411: LengthRequired,
        412: PreconditionFailed,
        413: RequestEntityTooLarge,
        414: RequestURITooLarge,
        415: UnsupportedMediaType,
        500: InternalServerError,
        501: NotImplemented,
        502: BadGateway,
        503: ServiceUnavailable,
        }
    settings = {'DEBUG': True}
    
    def index(request, code):
        print code
        raise errors[code]
    
    urls = [
        Rule('/<int:code>/', index),
        ]
    app = Shake(urls, settings)
    c = app.test_client()
    
    for code in errors:
        if code in app.error_handlers:
            continue
        resp = c.get('/%i/' % code)
        assert resp.status_code == code
        assert resp.data != 'error'


def test_fallback_error_code():
    errors = {
        400: BadRequest,
        401: Unauthorized,
        403: Forbidden,
        404: NotFound,
        405: MethodNotAllowed,
        406: NotAcceptable,
        408: RequestTimeout,
        410: Gone,
        411: LengthRequired,
        412: PreconditionFailed,
        413: RequestEntityTooLarge,
        414: RequestURITooLarge,
        415: UnsupportedMediaType,
        500: InternalServerError,
        501: NotImplemented,
        502: BadGateway,
        503: ServiceUnavailable,
        }
    settings = {'PAGE_ERROR': error, 'DEBUG': False}
    
    def index(request, code):
        print code
        raise errors[code]
    
    urls = [
        Rule('/<int:code>/', index),
        ]
    app = Shake(urls, settings)
    c = app.test_client()
    
    for code in errors:
        if code in app.error_handlers:
            continue
        resp = c.get('/%i/' % code)
        assert resp.status_code == code
        assert resp.data == 'error'


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
    resp = c.put('/')
    assert resp.data == 'False'
    resp = c.delete('/')
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
    resp = c.put('/')
    assert resp.data == 'False'
    resp = c.delete('/')
    assert resp.data == 'False'


def test_is_put():
    
    def index(request):
        return str(request.is_put)
    
    urls = [
        Rule('/', index),
        ]
    app = Shake(urls)
    c = app.test_client()
    
    resp = c.get('/')
    assert resp.data == 'False'
    resp = c.post('/')
    assert resp.data == 'False'
    resp = c.put('/')
    assert resp.data == 'True'
    resp = c.delete('/')
    assert resp.data == 'False'


def test_is_delete():
    
    def index(request):
        return str(request.is_delete)
    
    urls = [
        Rule('/', index),
        ]
    app = Shake(urls)
    c = app.test_client()
    
    resp = c.get('/')
    assert resp.data == 'False'
    resp = c.post('/')
    assert resp.data == 'False'
    resp = c.put('/')
    assert resp.data == 'False'
    resp = c.delete('/')
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


def test_response_response():
    
    def index(request):
        return Response('hello world')
    
    urls = [
        Rule('/', index),
        ]
    app = Shake(urls)
    
    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == HTTP_OK
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
    assert resp.status_code == HTTP_OK
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
    assert resp.status_code == HTTP_OK
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
    assert resp.status_code == HTTP_OK
    assert resp.mimetype == 'application/json'
    assert eval(resp.data) == data


def test_response_invalid():
    
    class A:
        pass
    
    invalid_responses = [
        42,
        [], (),
        [1, 2, 3],
        ('a', 'b', 'c'),
        lambda x: 2 * x,
        os.path,
        Ellipsis,
        A,
        A(),
        ]
    
    for r in invalid_responses:
        urls = [Rule('/', lambda request: r)]
        app = Shake(urls)
        
        c = app.test_client()
        with pytest.raises(Exception):
            c.get('/')


def test_response_mimetype():
    
    def index(request):
        return Response('hello world', mimetype='foo/bar')
    
    urls = [
        Rule('/', index),
        ]
    app = Shake(urls)
    
    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == HTTP_OK
    assert resp.mimetype == 'foo/bar'
    assert resp.data == 'hello world'


def test_processors_order():
    r = []
    
    def index(request):
        r.append('controller')
    
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
    
    assert r == ['rq1', 'rq2', 'controller', 'rs1', 'rs2']


def test_processors_order_exception():
    r = []
    
    def index(request):
        r.append('controller')
        assert False
    
    def econtroller(request, error):
        r.append('econtroller')
    
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
    settings = {'PAGE_ERROR': econtroller, 'DEBUG': False}
    app = Shake(urls, settings)
    
    app.before_request(rq1)
    app.before_request(rq2)
    app.before_response(rs1)
    app.before_response(rs2)
    app.on_exception(on_error)
    
    c = app.test_client()
    c.get('/')
    
    assert r == ['rq1', 'rq2', 'controller', 'error', 'econtroller']


def test_repeated_processors():
    r = []
    
    def index(request):
        r.append('controller')
    
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
    assert r == ['rq1', 'controller', 'rs1']


def test_repeated_processors_exception():
    r = []
    
    def index(request):
        r.append('controller')
        assert False
    
    def econtroller(request, error):
        r.append('econtroller')
    
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
    settings = {'PAGE_ERROR': econtroller, 'DEBUG': False}
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
    assert r == ['rq1', 'controller', 'error', 'econtroller']


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
    assert resp.status_code == HTTP_OK


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


def test_postdata_keyerror():
    """Bugfix v0.5.14 Test than the main application handles correctly a
    `KeyError` raised in a controller when doing `request.form['foo']` and
    `foo` isn't in request.form.
    """

    def p1(request):
        foo = request.form['bar']
    
    urls = [
        Rule('/', p1),
        ]
    app = Shake(urls)
    c = app.test_client()

    with pytest.raises(KeyError):
        resp = c.get('/')
    
    with pytest.raises(KeyError):
        resp = c.post('/', data={'a':123})


