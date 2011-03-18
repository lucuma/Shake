# -*- coding: utf-8 -*-
"""
    :copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
    :license: BSD. See LICENSE for more details.
"""
import os
from unittest import TestCase

from shake import (Shake, abort, redirect, Response, Rule, json, url_for,
    Paginator)


################################################################################

def index(request, name=None):
    msg = 'hello'
    if hasattr(request, 'foo'):
        msg = 'foo bar'
    return msg

def index2(request, what=''):
    return 'hello ' + what

def no_pass(request):
    abort(401)

# Custom "not found" view
def not_found(request, error):
    return 'not found'

# Custom error view
def error(request, error):
    return 'error'

# Custom access denied view
def denied(request, error):
    return 'access denied'

# View designed to fail
def fail(request):
    assert False

################################################################################


class TestApplication(TestCase):
    
    def test_callable_endpoint(self):
        urls = [
            Rule('/', index),
            ]
        app = Shake(urls)
        
        c = app.test_client()
        resp = c.get('/')
        assert resp.status_code == 200
        assert resp.data == 'hello'
    
    def test_string_endpoint(self):
        urls = [
            Rule('/', 'tests.test_app.index'),
            ]
        app = Shake(urls)
        
        c = app.test_client()
        resp = c.get('/')
        assert resp.status_code == 200
        assert resp.data == 'hello'
    
    def test_default_response(self):
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
    
    def test_custom_not_found(self):
        urls = [
            Rule('/', index),
            ]
        settings = {'PAGE_NOT_FOUND': not_found}
        app = Shake(urls, settings)
        
        c = app.test_client()
        resp = c.get('/bla')
        assert resp.status_code == 404
        assert resp.data == 'not found'
    
    def test_custom_error(self):
        urls = [
            Rule('/', fail),
            ]
        settings = {'PAGE_ERROR': error, 'DEBUG': False}
        app = Shake(urls, settings)
        
        c = app.test_client()
        resp = c.get('/')
        assert resp.status_code == 500
        assert resp.data == 'error'
    
    def test_custom_denied(self):
        urls = [
            Rule('/', no_pass),
            ]
        settings = {'PAGE_FORBIDDEN': denied}
        app = Shake(urls, settings)
        
        c = app.test_client()
        resp = c.get('/')
        assert resp.status_code == 401
        assert resp.data == 'access denied'
    
    def test_default_not_found(self):
        urls = [
            Rule('/', index),
            ]
        app = Shake(urls)
        
        c = app.test_client()
        resp = c.get('/bla')
        assert resp.status_code == 404
        assert '<title>Page not found</title>' in resp.data
    
    def test_default_error(self):
        urls = [
            Rule('/', fail),
            ]
        app = Shake(urls)
        
        c = app.test_client()
        self.assertRaises(AssertionError, c.get, '/')
    
    def test_default_denied(self):
        urls = [
            Rule('/', no_pass),
            ]
        app = Shake(urls)
        
        c = app.test_client()
        resp = c.get('/')
        assert resp.status_code == 401
        assert '<title>Access Denied</title>' in resp.data
    
    def test_named_urls(self):
        urls = [
            Rule('/', index, name='home'),
            ]
        app = Shake(urls)
        
        c = app.test_client()
        resp = c.get('/')
        assert resp.status_code == 200
        assert resp.data == 'hello'
    
    def test_redirect(self):
        def redir(request):
            return redirect('/bla')
        
        urls = [
            Rule('/', redir),
            ]
        app = Shake(urls)
        
        c = app.test_client()
        resp = c.get('/')
        assert resp.status_code == 302


class TestProcessors(TestCase):
    
    def test_order(self):
        r = []
        
        def index(request):
            r.append('view')
        
        def rq1(request):
            r.append('a')
        
        def rq2(request):
            r.append('b')
        
        def rs1(response):
            r.append(1)
            return response
        
        def rs2(response):
            r.append(2)
            return response
        
        urls = [Rule('/', index)]
        app = Shake(urls)
        
        app.before_request(rq1)
        app.before_request(rq2)
        app.before_response(rs1)
        app.before_response(rs2)
        
        c = app.test_client()
        c.get('/')
        
        expected= ['a', 'b', 'view', 1, 2]
        self.assertEqual(r, expected)
    
    def test_norepeat(self):
        r = []
        
        def index(request):
            r.append('view')
        
        def brq(request):
            r.append('a')
        
        def brs(response):
            r.append(1)
            return response
        
        urls = [Rule('/', index)]
        app = Shake(urls)
        
        app.before_request(brq)
        app.before_request(brq)
        app.before_response(brs)
        app.before_response(brs)
        app.before_request(brq)
        
        c = app.test_client()
        c.get('/')
        
        expected= ['a', 'view', 1]
        self.assertEqual(r, expected)
    
    def test_before_response_return(self):
        def index(request):
            return 'ok'
        
        def brs(response):
            pass
        
        urls = [Rule('/', index)]
        app = Shake(urls)
        app.before_response(brs)
        
        c = app.test_client()
        self.assertRaises(Exception, c, 'get', '/')


class TestRequest(TestCase):
    
    def test_is_method(self):
        def index(request):
            return '%s %s' % (request.is_get, request.is_post)
        
        urls = [
            Rule('/', index),
            ]
        app = Shake(urls)
        c = app.test_client()
        
        resp = c.get('/')
        assert resp.data == 'True False'
        
        resp = c.post('/')
        assert resp.data == 'False True'
    
    
    def test_is_json(self):
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
        self.assertEqual(eval(resp.data), data)
        
        resp = c.post('/', data=json.dumps(data))
        assert resp.data == 'None'


class TestSession(TestCase):
    
    def test_session(self):
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
    
    def test_session_nosecret(self):
        def p1(request):
            request.session['foo'] = 'bar'
        
        urls = [
            Rule('/', p1),
            ]
        app = Shake(urls)
        c = app.test_client()
        self.assertRaises(RuntimeError, c.get, '/')


class PaginationTestCase(TestCase):

    def test_basic_pagination(self):
        p = Paginator(None, 1, 20, 500)
        self.assertEqual(p.page, 1)
        self.assertFalse(p.has_prev)
        self.assert_(p.has_next)
        self.assertEqual(p.total, 500)
        self.assertEqual(p.num_pages, 25)
        self.assertEqual(p.next_num, 2)
        self.assertEqual(list(p.iter_pages()),
            [1, 2, 3, 4, 5, None, 24, 25])
        p.page = 10
        self.assertEqual(list(p.iter_pages()),
            [1, 2, None, 8, 9, 10, 11, 12, 13, 14, None, 24, 25])


if __name__ == '__main__':
    unittest.main()

