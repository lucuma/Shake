# -*- coding: utf-8 -*-
"""
    Test view templates
    
    :copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
    :license: BSD. See LICENSE for more details.
"""
import jinja2
import os
import pytest

from shake import Shake, Rule, Render, TemplateNotFound


views_dir = os.path.join(os.path.dirname(__file__), 'views')
loader = jinja2.FileSystemLoader(views_dir)

    
def test_render_view():
    render = Render(__file__, globals={'who': 'E.T.'})
    
    def _home(request):
        return render('view.txt', mimetype='text/plain', action='phone')
        
    urls = [
        Rule('/home', _home),
        ]
    app = Shake(urls)
    render.app = app
    
    c = app.test_client()
    resp = c.get('/home')
    assert resp.status == '200 OK'
    assert resp.data == 'E.T. phone /home'


def test_template_not_found():
    render = Render(__file__)
    
    def _no_template(request):
        return render('x.html')
    
    urls = [
        Rule('/', _no_template),
        ]
    app = Shake(urls)
    render.app = app
    
    c = app.test_client()
    with pytest.raises(TemplateNotFound):
        c.get('/')

