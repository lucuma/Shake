# -*- coding: utf-8 -*-
import os

import pytest
import shake
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

#### Views #####

def index(request):
    return 'hello'


def no_pass(request):
    raise NotAllowed


def not_found(request, error):
    """Custom "not found" view."""
    return 'not found'


def error(request, error):
    """Custom error view."""
    return 'error'


def not_allowed(request, error):
    """Custom access "not allowed" view."""
    return 'access denied'


def fail(request):
    assert False


##### Tests #####

def test_callable_endpoint():
    app = Shake(__file__)
    app.add_url('/', index)
    
    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == HTTP_OK
    assert resp.data == 'hello'


def test_string_endpoint():
    app = Shake(__file__)
    app.add_url('/', 'tests.test_app.index')

    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == HTTP_OK
    assert resp.data == 'hello'


def test_default_response():
    app = Shake(__file__)
    
    @app.route('/')
    def index(request):
        pass
    
    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == HTTP_OK
    assert resp.data == ''


def test_default_not_found():
    app = Shake(__file__)
    app.add_url('/', index)
    
    c = app.test_client()
    resp = c.get('/bla')
    assert resp.status_code == HTTP_NOT_FOUND
    assert '<title>Page not found</title>' in resp.data


def test_default_error():
    app = Shake(__file__)
    app.add_url('/', fail)
    
    c = app.test_client()
    with pytest.raises(AssertionError):
        c.get('/')


def test_default_not_allowed():
    app = Shake(__file__)
    app.add_url('/', no_pass)
    
    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == HTTP_FORBIDDEN
    assert '<title>Access Denied</title>' in resp.data


def test_redirect():
    app = Shake(__file__)

    @app.route('/')
    def redir(request):
        return redirect('/bla')
    
    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == HTTP_FOUND


def test_custom_not_found():
    settings = {'PAGE_NOT_FOUND': not_found, 'DEBUG': True}
    app = Shake(__file__, settings)
    app.add_url('/', index)
    
    c = app.test_client()
    resp = c.get('/bla')
    assert resp.status_code == HTTP_NOT_FOUND
    assert resp.data == 'not found'


def test_custom_error():
    settings = {'PAGE_ERROR': error, 'DEBUG': False}
    app = Shake(__file__, settings)
    app.add_url('/', fail)
    
    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == HTTP_ERROR
    assert resp.data == 'error'


def test_custom_not_allowed():
    settings = {'PAGE_NOT_ALLOWED': not_allowed}
    app = Shake(__file__, settings)
    app.add_url('/', no_pass)
    
    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == HTTP_FORBIDDEN
    assert resp.data == 'access denied'


def test_data_not_found():
    settings = {'DEBUG': True}
    app = Shake(__file__, settings)

    @app.route('/')
    def data_not_found(request):
        raise NotFound
    
    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == HTTP_NOT_FOUND
    assert resp.data


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
    settings = {'DEBUG': False}
    app = Shake(__file__, settings)
    
    @app.route('/<int:code>/')
    def index(request, code):
        print code
        raise errors[code]

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
    app = Shake(__file__, settings)

    @app.route('/<int:code>/')
    def index(request, code):
        print code
        raise errors[code]

    c = app.test_client()
    for code in errors:
        if code in app.error_handlers:
            continue
        resp = c.get('/%i/' % code)
        assert resp.status_code == code
        assert resp.data == 'error'


def test_is_get():
    app = Shake(__file__)

    @app.route('/')
    def index(request):
        return str(request.is_get)
    
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
    app = Shake(__file__)

    @app.route('/')
    def index(request):
        return str(request.is_post)
    
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
    app = Shake(__file__)

    @app.route('/')
    def index(request):
        return str(request.is_put)
    
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
    app = Shake(__file__)

    @app.route('/')
    def index(request):
        return str(request.is_delete)

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
    app = Shake(__file__)
    data = {'foo': 'bar', 'num': 3}

    @app.route('/')
    def index(request):
        return str(request.json)
    
    c = app.test_client()
    resp = c.post('/', content_type='application/json',
        data=json.dumps(data))
    assert eval(resp.data) == data
    
    resp = c.post('/', data=json.dumps(data))
    assert resp.data == 'None'


def test_response_response():
    app = Shake(__file__)

    @app.route('/')
    def index(request):
        return Response('hello world')

    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == HTTP_OK
    assert resp.mimetype == 'text/plain'
    assert resp.data == 'hello world'


def test_response_string():
    app = Shake(__file__)

    @app.route('/')
    def index(request):
        return 'hello world'
    
    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == HTTP_OK
    assert resp.mimetype == 'text/plain'
    assert resp.data == 'hello world'


def test_response_none():
    app = Shake(__file__)

    @app.route('/')
    def index(request):
        return None
    
    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == HTTP_OK
    assert resp.mimetype == 'text/plain'
    assert resp.data == ''


def test_response_json():
    app = Shake(__file__)
    data = {'foo': 'bar', 'num': 3}

    @app.route('/')
    def index(request):
        return data
    
    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == HTTP_OK
    assert resp.mimetype == 'application/json'
    assert eval(resp.data) == data


def test_bad_responses():
    
    bad_responses = [
        42,
        [], (),
        [1, 2, 3],
        ('a', 'b', 'c'),
        os.path,
        Ellipsis,
    ]
    
    for r in bad_responses:
        app = Shake(__file__)
        app.add_url('/', lambda request: r)
        c = app.test_client()
        print '\nr is:', r
        resp = c.get('/')


def test_response_mimetype():
    app = Shake(__file__)

    @app.route('/')
    def index(request):
        return Response('hello world', mimetype='foo/bar')
        
    c = app.test_client()
    resp = c.get('/')
    assert resp.status_code == HTTP_OK
    assert resp.mimetype == 'foo/bar'
    assert resp.data == 'hello world'


def test_processors_order():
    app = Shake(__file__)
    r = []
    
    @app.route('/')
    def index(request):
        r.append('view')
    
    @app.before_request
    def br1(request):
        r.append('br1')
    
    @app.before_request
    def br2(request):
        r.append('br2')
    
    @app.after_request
    def ar1(response):
        r.append('ar1')
        return response
    
    @app.after_request
    def ar2(response):
        r.append('ar2')
        return response
    
    @app.on_exception
    def error(e):
        r.append('error')
    
    c = app.test_client()
    c.get('/')
    assert r == 'br1 br2 view ar1 ar2'.split()


def test_processors_order_exception():
    
    def eview(request, error):
        r.append('eview')

    settings = {'PAGE_ERROR': eview, 'DEBUG': False}
    app = Shake(__file__, settings)
    r = []
    
    @app.route('/')
    def index(request):
        r.append('view')
        assert False
    
    @app.before_request
    def br1(request):
        r.append('br1')
    
    @app.before_request
    def br2(request):
        r.append('br2')
    
    @app.after_request
    def ar1(response):
        r.append('ar1')
        return response
    
    @app.after_request
    def ar2(response):
        r.append('ar2')
        return response
    
    @app.on_exception
    def on_error(e):
        r.append('error')
    
    c = app.test_client()
    c.get('/')
    assert r == 'br1 br2 view error eview ar1 ar2'.split()


def test_after_request_return():
    app = Shake(__file__)

    @app.route('/')
    def index(request):
        return 'ok'
    
    @app.after_request
    def brs(response):
        pass
    
    c = app.test_client()
    with pytest.raises(Exception):
        print c.get('/')


def test_session():
    settings = {'SECRET_KEY': 'abc'*20}
    app = Shake(__file__, settings)

    @app.route('/write/')
    def write(request):
        request.session['foo'] = 'bar'

    @app.route('/read/')
    def read(request):
        assert request.session['foo'] == 'bar'
    
    c = app.test_client()
    c.get('/write/')
    print c.cookie_jar
    c.get('/read/')


def test_session_nosecret():
    app = Shake(__file__)

    @app.route('/')
    def p1(request):
        request.session['foo'] = 'bar'
    
    c = app.test_client()
    with pytest.raises(RuntimeError):
        print c.get('/')


def test_postdata_keyerror():
    """Bugfix v0.5.14 Test than the main application handles correctly a
    `KeyError` raised in a view when doing `request.form['foo']` and
    `foo` isn't in request.form.
    """
    app = Shake(__file__)

    @app.route('/')
    def p1(request):
        foo = request.form['bar']

    c = app.test_client()

    with pytest.raises(KeyError):
        print c.get('/')

    with pytest.raises(KeyError):
        print c.post('/', data={'a':123})

