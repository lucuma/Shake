# -*- coding: utf-8 -*-
import io
import os
import random
from StringIO import StringIO
import time

import pytest
from shake import Shake, Rule, url_for, NotFound
from shake.helpers import (url_join, path_join, url_join,
    to64, from64, to36, from36, StorageDict, send_file, safe_join)
from werkzeug.http import parse_options_header


def endpoint(request, name=None):
    msg = 'hello'
    if name:
        msg = 'hello ' + name
    return msg


def test_url_for():
    app = Shake(__file__)
    c = app.test_client()

    def index(request):
        expected = '/hello/world/'
        url = url_for(endpoint, name='world')
        assert url == expected

        expected = 'http://0.0.0.0:5000/hello/world/'
        url = url_for(endpoint, name='world', external=True)
        assert url == expected

        expected = '/hello/world/#awesome'
        url = url_for(endpoint, name='world', anchor='awesome')
        assert url == expected

        expected = 'http://0.0.0.0:5000/hello/world/#awesome'
        url = url_for(endpoint, name='world', anchor='awesome', external=True)
        assert url == expected
    
    app.add_urls([
        Rule('/', index),
        Rule('/hello/<name>/', endpoint),
    ])
     
    resp = c.get('/')


def test_url_for_server_name():
    settings = {
        'SERVER_NAME': 'example.com',
        'DEFAULT_SUBDOMAIN': 'www',
    }
    app = Shake(__file__, settings)
    c = app.test_client()

    @app.route('/hello/<name>/')
    def index(request):
        expected = 'http://www.example.com/hello/world/'
        url = url_for(endpoint, name='world', external=True)
        assert url == expected
    
    resp = c.get('/')


def test_url_for_method():
    app = Shake(__file__)
    c = app.test_client()
    
    def index(request):
        expected = '/get/resource/'
        url = url_for(endpoint, name='resource')
        assert url == expected

        expected = '/get/resource/'
        url = url_for(endpoint, name='resource', method='GET')
        assert url == expected

        expected = '/update/resource/'
        url = url_for(endpoint, name='resource', method='POST')
        assert url == expected
    
    app.add_urls([
        Rule('/', index),
        Rule('/get/<name>/', endpoint, methods=['GET']),
        Rule('/update/<name>/', endpoint, methods=['POST']),
    ])
    
    resp = c.get('/')


def test_named_url_for():
    app = Shake(__file__)
    c = app.test_client()

    def test(request):
        result = [url_for('a'), url_for('b'), url_for('c')]
        return ' '.join(result)
    
    app.add_urls([
        Rule('/', test),
        Rule('/home1/', endpoint, name='a'),
        Rule('/home2/', endpoint, name='b'),
        Rule('/home3/', endpoint, name='c'),
    ])
    
    resp = c.get('/')
    assert resp.status_code == 200
    assert resp.data == '/home1/ /home2/ /home3/'
 

def test_url_join():
    expected = '/path/dir'
    assert url_join('/path', 'dir') == expected
    assert url_join('/path/', '/dir') == expected
    assert url_join('/path/', 'dir1/', '//dir2/', '/dir3/') == \
        '/path/dir1/dir2/dir3'
    assert url_join('/path/', 'dir1/', '/dir2//', '../dir3/') == \
        '/path/dir1/dir3'


def test_to64():
    assert to64(0) == '0'
    assert to64(10) == 'a'
    assert to64(125) == '1Z'
    assert to64(126) == '1='
    assert to64(127) == '1_'
    assert to64(128) == '20'
    assert len(to64(pow(3, 1979))) == 523
    with pytest.raises(AssertionError):
        to64(-1)
    with pytest.raises(AssertionError):
        to64('a')


def test_from64():
    assert from64('0') == 0
    assert from64('a') == 10
    assert from64('1Z') == 125
    assert from64('1=') == 126
    assert from64('1_') == 127
    assert from64('20') == 128
    with pytest.raises(ValueError):
        from64('!')


def test_custom_alphabet64():
    CUSTOM = 'abcdefghijklmnopqrstuvwxyz0123456789.:,;*@#$%&/()[]{}=_-ABCDEFGH'
    
    assert to64(555, CUSTOM) == 'i$'
    assert from64('AA', CUSTOM) == 3640
    
    RANDOM = [c for c in
        '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ=_']
    random.shuffle(RANDOM)
    RANDOM = ''.join(RANDOM)
    
    RCUSTOM = [c for c in CUSTOM]
    random.shuffle(RCUSTOM)
    RCUSTOM = ''.join(RCUSTOM)
    
    rnum = random.randint(0, 5555)
    
    assert from64(to64(rnum, CUSTOM), CUSTOM) == rnum
    assert from64(to64(rnum, RANDOM), RANDOM) == rnum
    assert from64(to64(rnum, RCUSTOM), RCUSTOM) == rnum


def test_custom_alphabet64_invalid():
    CUSTOM = 'abcdefghijklmnopqrstuvwxyz0123456789.:,;*@#$%&/()[]{}=_-ABCDEFGH'
    
    # bad custom alphabet
    with pytest.raises(AssertionError):
        to64(1, 'bad')
    with pytest.raises(AssertionError):
        to64(1, CUSTOM + '!-')
    
    # values not in custom alphabet
    with pytest.raises(ValueError):
        from64('J', CUSTOM)
    with pytest.raises(ValueError):
        from64('!', CUSTOM)


def test_to36():
    assert to36(0) == '0'
    assert to36(10) == 'a'
    assert to36(125) == '3h'
    assert to36(143) == '3z'
    assert to36(144) == '40'
    assert len(to36(pow(3, 1979))) == 607
    with pytest.raises(AssertionError):
        to36(-1)
    with pytest.raises(AssertionError):
        to36('a')


def test_from36():
    assert from36('0') == 0
    assert from36('a') == 10
    assert from36('3h') == 125
    assert from36('3z') == 143
    assert from36('40') == 144
    with pytest.raises(ValueError):
        from36('!')


def test_custom_alphabet36():
    CUSTOM = '9876543210ZYXWVUTSRQPONMLKJIHGFEDCBA'
    
    assert to36(555, CUSTOM) == 'UU'
    assert from36('ZZ', CUSTOM) == 370
    
    RANDOM = [c for c in '0123456789abcdefghijklmnopqrstuvwxyz']
    random.shuffle(RANDOM)
    RANDOM = ''.join(RANDOM)
    
    RCUSTOM = [c for c in CUSTOM]
    random.shuffle(RCUSTOM)
    RCUSTOM = ''.join(RCUSTOM)
    
    rnum = random.randint(0, 5555)
    
    assert from36(to36(rnum, CUSTOM), CUSTOM) == rnum
    assert from36(to36(rnum, RANDOM), RANDOM) == rnum
    assert from36(to36(rnum, RCUSTOM), RCUSTOM) == rnum


def test_custom_alphabet36_invalid():
    CUSTOM = '9876543210ZYXWVUTSRQPONMLKJIHGFEDCBA'
    
    # bad custom alphabet
    with pytest.raises(AssertionError):
        to36(1, 'bad')
    with pytest.raises(AssertionError):
        to36(1, CUSTOM + 'abc')
    
    # values not in custom alphabet
    with pytest.raises(ValueError):
        from36('ab', CUSTOM)
    with pytest.raises(ValueError):
        from36('!', CUSTOM)


def test_storagedict_creation():
    st1 = StorageDict(a=1)
    st2 = StorageDict({'a': 1})
    assert st1.a == st2.a


def test_storagedict_basic():
    st = StorageDict(a=1, b=2, c='3')
    assert st.a == st['a']
    assert st.a == 1
    assert st.b == st['b']
    assert st.b == 2
    assert st.c == st['c']
    assert st.c == '3'


def test_storagedict_get():
    st = StorageDict(a=1, b=2, c='3')
    
    assert st.get('b') == 2
    del st.b
    assert st.get('b') == None
    assert st.get('b', 3) == 3
    with pytest.raises(KeyError):
        st['b']
    with pytest.raises(AttributeError):
        st.b


def test_storagedict_update():
    st = StorageDict(a=1, b=2, c='3')
    
    st.d = 4
    assert st.d == 4
    assert st['d'] == 4
    assert st.get('d') == 4
    
    st.update({'a': 10, 'c': 12})
    assert st.a == 10
    assert st['a'] == 10
    assert st.get('a') == 10
    assert st.c == 12
    assert st['c'] == 12
    assert st.get('c') == 12


def test_send_file_regular():
    app = Shake(__file__)
    c = app.test_client()

    @app.route('/')
    def index(request):
        filename = path_join(__file__, 'static/index.html')
        resp = send_file(request, filename)
        assert resp.direct_passthrough
        assert resp.mimetype == 'text/html'
        with io.open(filename) as f:
            assert resp.data == f.read()
        
        filename = path_join(__file__, 'static/favicon.ico')
        resp = send_file(request, filename)
        assert resp.direct_passthrough
        assert resp.mimetype == 'image/x-icon'

    resp = c.get('/')


def test_send_file_xsendfile():
    app = Shake(__file__)
    c = app.test_client()

    @app.route('/')
    def index(request):
        filename = path_join(__file__, 'static/index.html')
        resp = send_file(request, filename, use_x_sendfile=True)
        assert resp.direct_passthrough
        assert 'x-sendfile' in resp.headers
        assert resp.headers['x-sendfile'] == filename
        assert resp.mimetype == 'text/html'
    
    resp = c.get('/')


def test_send_file_object():
    app = Shake(__file__)
    c = app.test_client()

    @app.route('/')
    def index(request):
        filename = path_join(__file__, 'static/index.html')

        with io.open(filename) as f:
            data = f.read()

        with io.open(filename) as f:
            with pytest.raises(AssertionError):
                resp = send_file(request, f)
        
        with io.open(filename) as f:
            resp = send_file(request, f, mimetype='text/html')
            assert resp.direct_passthrough
            assert resp.mimetype == 'text/html'
            assert resp.data == data
        
        with io.open(filename) as f:
            resp = send_file(request, f, attachment_filename='foo.html')
            assert resp.direct_passthrough
            assert resp.mimetype == 'text/html'
            assert resp.data == data
        
        f = StringIO('Test')
        resp = send_file(request, f, attachment_filename='test')
        assert resp.mimetype == 'application/octet-stream'
        assert resp.data == 'Test'

        f = StringIO('Test')
        resp = send_file(request, f, mimetype='text/plain')
        assert resp.mimetype == 'text/plain'
        assert resp.data == 'Test'
    
    resp = c.get('/')


def test_send_file_object_xsendfile():
    app = Shake(__file__)
    c = app.test_client()

    @app.route('/')
    def index(request):
        filename = path_join(__file__, 'static/index.html')
        
        with io.open(filename) as f:
            resp = send_file(request, f, mimetype='text/html',
                use_x_sendfile=True)
            assert 'x-sendfile' in resp.headers
            assert resp.headers['x-sendfile'] == filename
            assert resp.mimetype == 'text/html'
        
        f = StringIO('Test')
        resp = send_file(request, f, mimetype='text/plain',
            use_x_sendfile=True)
        assert 'x-sendfile' not in resp.headers

    resp = c.get('/')


def test_send_file_attachment():
    app = Shake(__file__)
    c = app.test_client()

    @app.route('/')
    def index(request):
        filename = path_join(__file__, 'static/index.html')
        
        with io.open(filename) as f:
            resp = send_file(request, f, mimetype='text/html',
                as_attachment=True)
            cd_header = resp.headers['Content-Disposition']
            value, options = parse_options_header(cd_header)
            assert value == 'attachment'
        
        resp = send_file(request, filename, as_attachment=True)
        cd_header = resp.headers['Content-Disposition']
        value, options = parse_options_header(cd_header)
        assert value == 'attachment'
        assert options['filename'] == 'index.html'

        f = StringIO('Test')
        resp = send_file(request, f, attachment_filename='readme.txt',
            as_attachment=True)
        assert resp.mimetype == 'text/plain'
        cd_header = resp.headers['Content-Disposition']
        value, options = parse_options_header(cd_header)
        assert value == 'attachment'
        assert options['filename'] == 'readme.txt'

    resp = c.get('/')


def test_safe_join_safe():
    assert safe_join('', '') == '.'
    assert safe_join('/static', 'foo/') == '/static/foo'
    assert safe_join('/static', 'foo/bar') == '/static/foo/bar'
    assert safe_join('/static/', 'foo/bar') == '/static/foo/bar'


def test_safe_join_unsafe():
    with pytest.raises(NotFound):
        safe_join('/static', '/foo/bar')
        safe_join('/static', '//foo/bar')
        safe_join('/static', '../etc/passwords')
        safe_join('/static', 'foo/../../etc/passwords')


def test_storage_dict():
    st = StorageDict({'a': 3, 'c': 'meh', 'd': 0})
    assert st.a == st['a']
    assert st.a == 3
    st.b = 5
    assert st.b == st['b']
    assert st.b == 5
    assert st.c
    del st['b']
    del st['c']
    del st.d
    assert st.keys() == ['a']

