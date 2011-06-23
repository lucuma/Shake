# -*- coding: utf-8 -*-
"""
    Test view templates
    
    :copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
    :license: BSD. See LICENSE for more details.
"""
import jinja2
import os
import pytest

from shake import Shake, Rule, Render, ViewNotFound


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


def test_default_globals():
    g = {'who':'E.T.', 'action':'phone', 'where':'home'}
    render = Render(views_dir, globals=g)

    resp = render.to_string('view.html')
    assert resp == '<h1>Hello World</h1>'
    resp = render.to_string('view.txt')
    assert resp == 'E.T. phone home'
    

#TODO
def test_default_tests():
    pass


def test_globals():
    pass


#TODO
def test_filters():
    pass


#TODO
def test_tests():
    pass


#TODO
def test_alt_loader():
    alt_loader = jinja2.FileSystemLoader(static_dir)
    pass


#TODO
def test_csrf_token():
    pass

#TODO
def test_flash_messagesech():
    pass

