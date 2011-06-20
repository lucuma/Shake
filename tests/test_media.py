# -*- coding: utf-8 -*-
"""
    :copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
    :license: BSD. See LICENSE for more details.
"""
import pytest

from shake import media
from shake import Shake, local, StorageDict

    
def set_up():
    local.media = {}
    local.app = StorageDict()
    local.app.settings = StorageDict()


def test_add_css():
    set_up()
    media.add_css('t1.css')
    media.add_css('t2.css', title='t2', media='screen')
    media.add_css('t1.css')
    media.add_css('t3.css', alternate=True)
    media.add_css('t4.css', iecon='lte IE6')
    media.add_css('t5.css', iecon='IE7')
    media.add_css('t5.css', iecon='IE7')
    media.add_css('t6.css', iecon='lte IE6')


def test_add_js():
    set_up()
    media.add_js('t1.js')
    media.add_js('t2.js')
    media.add_js('t3.js')
    media.add_js('t3.js')
    media.add_js('t4.js', iecon='lte IE7')
    media.add_js('t4.js', iecon='lte IE7')


def test_add_link():
    set_up()
    media.add_link('/feed.rss', title='test feed', rel='alternate', mtype='rss+xml')
    media.add_link('/page/2', title='next page', rel='next')
    media.add_link('/page/2', title='next page', rel='next')
    media.add_link('/xmlrpc', rel='pingback')


def test_add_feed():
    set_up()
    media.add_feed('/feed.rss', title='rss feed')
    media.add_feed('/atom.xml', title='atom feed', mtype='atom+xml')


def test_add_meta():
    set_up()
    media.add_meta('author', 'milk')
    media.add_meta('author', 'shake')
    media.add_meta('description', 'this is a test')
    media.add_meta('author', 'shake')


def test_render_css():
    set_up()
    media.add_css('/static/t1.css')
    media.add_css('/static/t2.css', media='screen', title='t2', alternate=True)
    media.add_css('/static/ie7.css', iecon='IE7')
    media.add_css('/static/ie6.css', iecon='lte IE6')
    media.add_css('/static/print_ie6.css', media='print', iecon='lte IE6')
    
    expected = (
        '<link href="/static/t1.css" media="all" rel="stylesheet">\n'
        '<link href="/static/t2.css" media="screen" rel="alternate stylesheet" title="t2">\n'
        '<!--[if lte IE6]>\n'
        '<link href="/static/ie6.css" media="all" rel="stylesheet">\n'
        '<link href="/static/print_ie6.css" media="print" rel="stylesheet">\n'
        '<![endif]-->\n'
        '<!--[if IE7]>\n'
        '<link href="/static/ie7.css" media="all" rel="stylesheet">\n'
        '<![endif]-->'
        )
    result = media.render_css()
    assert expected == result


def test_render_js():
    set_up()
    media.add_js('/static/t1.js')
    media.add_js('/static/t2.js')
    media.add_js('/static/html5.js', iecon='IE')
    media.add_js('/static/ie6.js', iecon='lte IE6')
    media.add_js('/static/ie.js', iecon='IE')
    
    expected = (
        '<script src="/static/t1.js"></script>\n'
        '<script src="/static/t2.js"></script>\n'
        '<!--[if lte IE6]>\n'
        '<script src="/static/ie6.js"></script>\n'
        '<![endif]-->\n'
        '<!--[if IE]>\n'
        '<script src="/static/html5.js"></script>\n'
        '<script src="/static/ie.js"></script>\n'
        '<![endif]-->'
        )
    result = media.render_js()
    print result
    assert expected == result


def test_render_links():
    set_up()
    media.add_link('/feed.rss', title='test feed', rel='alternate', mtype='rss+xml')
    media.add_link('page/2', title='next page', rel='next')
    media.add_link('/xmlrpc', rel='pingback')
    media.add_link('/favicon.ico', rel='shortcut icon', mtype='image/x-icon')
    expected = (
        '<link href="/feed.rss" rel="alternate" title="test feed" type="rss+xml">\n'
        '<link href="page/2" rel="next" title="next page">\n'
        '<link href="/xmlrpc" rel="pingback">\n'
        '<link href="/favicon.ico" rel="shortcut icon" type="image/x-icon">'
        )
    result = media.render_links()
    assert expected == result


def test_render_metas():
    set_up()
    media.add_meta('author', 'shake')
    media.add_meta('description', 'this is a test')
    expected = (
        '<meta name="author" content="shake">\n'
        '<meta name="description" content="this is a test">'
        )
    result = media.render_metas()
    assert expected == result

