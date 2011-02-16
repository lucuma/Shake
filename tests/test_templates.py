# -*- coding: utf-8 -*-
"""
    :copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
    :license: BSD. See LICENSE for more details.
"""
import os
import unittest

import jinja2

from shake import Shake, Rule, Render, TemplateNotFound


templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
loader = jinja2.FileSystemLoader(templates_dir)


class TestRender(unittest.TestCase):
    
    def test_templates(self):
        render = Render(__file__, globals={'who': 'E.T.'})
        
        def _home(request):
            return render('template.txt', mimetype='text/plain', action='phone')
            
        urls = [
            Rule('/home', _home),
            ]
        app = Shake(urls)
        render.app = app
        
        c = app.test_client()
        resp = c.get('/home')
        self.assertEqual(resp.status, '200 OK')
        self.assertEqual(resp.data, 'E.T. phone /home')
    
    def test_no_template(self):
        render = Render(__file__)
        
        def _no_template(request):
            return render('x.html')
        
        urls = [
            Rule('/', _no_template),
            ]
        app = Shake(urls)
        render.app = app
        
        c = app.test_client()
        self.assertRaises(TemplateNotFound, c.get, '/')


if __name__ == '__main__':
    unittest.main()

