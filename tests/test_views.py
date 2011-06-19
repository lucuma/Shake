# -*- coding: utf-8 -*-
"""
    :copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
    :license: BSD. See LICENSE for more details.
"""
import os
import unittest

from shake import Shake, abort, Rule, Render
from shake.views import not_found_page, error_page, not_allowed_page
from shake.views import show_template, send_file, send_file


def index(request):
    return 'hello'


def fail(request):
    """View designed to fail. """
    assert False


def no_pass(request):
    abort(401)


class TestDefaultViews(unittest.TestCase):
    
    def test_default_not_found(self):
        urls = [
            Rule('/', index),
            ]
        settings = {
            'PAGE_NOT_FOUND': not_found_page
            }
        app = Shake(urls, settings)
        c = app.test_client()
        resp = c.get('/bla')
        self.assertEqual(resp.status_code, 404)
        assert '<title>Page not found</title>' in resp.data
    
    def test_default_error(self):
        urls = [
            Rule('/', fail),
            ]
        settings = {
            'DEBUG': False,
            'PAGE_ERROR': error_page
            }
        app = Shake(urls, settings)
        c = app.test_client()
        resp = c.get('/')
        self.assertEqual(resp.status_code, 500)
        assert '<title>Error</title>' in resp.data
    
    def test_default_denied(self):
        urls = [
            Rule('/', no_pass),
            ]
        settings = {
            'PAGE_NOT_ALLOWED': not_allowed_page
            }
        app = Shake(urls, settings)
        c = app.test_client()
        resp = c.get('/')
        self.assertEqual(resp.status_code, 401)
        assert '<title>Access Denied</title>' in resp.data


class TestShowTemplate(unittest.TestCase):
    
    def test_render(self):
        render = Render(__file__)
        urls = [
            Rule('/', show_template, 
                defaults={'render': render, 'template': 'template.html'}),
            ]
        app = Shake(urls)
        
        c = app.test_client()
        resp = c.get('/')
        self.assertEqual(resp.data, '<h1>Hello World</h1>')
        self.assertEqual(resp.mimetype, 'text/html')
    
    def test_args(self):
        render = Render(__file__)
        urls = [
            Rule('/', show_template, 
                defaults={
                    'render': render,
                    'template': 'template.txt',
                    'mimetype': 'text/plain',
                    'who': 'You',
                    'action': 'are here:',
                }),
            ]
        app = Shake(urls)
        
        c = app.test_client()
        resp = c.get('/')
        self.assertEqual(resp.data, 'You are here: /')
        self.assertEqual(resp.mimetype, 'text/plain')


if __name__ == '__main__':
    unittest.main()

