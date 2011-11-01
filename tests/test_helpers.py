# -*- coding: utf-8 -*-
"""
    Copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
    MIT License. (http://www.opensource.org/licenses/mit-license.php)
"""
import os
import pytest
import random
import time

from shake import Shake, Rule, url_for
from shake.helpers import (url_join, execute, to64, from64, to36, from36,
    StorageDict)


def endpoint(request, name=None):
    msg = 'hello'
    if name:
        msg = 'hello ' + name
    return msg


def test_url_for():
    
    def index(request):
        return url_for(endpoint, name='world')
    
    urls = [
        Rule('/', index),
        Rule('/home/', endpoint),
        Rule('/hello/<name>/', endpoint),
        ]
    app = Shake(urls)
    c = app.test_client()
    
    resp = c.get('/')
    assert resp.data == '/hello/world/'


def test_named_url_for():
    
    def test(request):
        result = [url_for('a'), url_for('b'), url_for('c')]
        return ' '.join(result)
    
    urls = [
        Rule('/', test),
        Rule('/home1/', endpoint, name='a'),
        Rule('/home2/', endpoint, name='b'),
        Rule('/home3/', endpoint, name='c'),
        ]
    app = Shake(urls)
    c = app.test_client()
    
    resp = c.get('/')
    assert resp.status_code == 200
    assert resp.data == '/home1/ /home2/ /home3/'


def test_named_url_for_dup():
    
    def test(request):
        return url_for('a')
    
    urls = [
        Rule('/', test),
        Rule('/home1/', endpoint, name='a'),
        Rule('/home2/', endpoint, name='a'),
        Rule('/home3/', endpoint, name='a'),
        ]
    app = Shake(urls)
    c = app.test_client()
    
    resp = c.get('/')
    assert resp.status_code == 200
    assert resp.data == '/home3/'
 

def test_url_join():
    expected = '/path/dir'
    assert url_join('/path', 'dir') == expected
    assert url_join('/path/', '/dir') == expected
    assert url_join('/path/', 'dir1/', '//dir2/', '/dir3/') == \
        '/path/dir1/dir2/dir3'
    assert url_join('/path/', 'dir1/', '/dir2//', '../dir3/') == \
        '/path/dir1/dir3'


def test_execute():
    with pytest.raises(OSError):
        execute('qwerty99933654321x')
    
    result1 = execute('stat', [__file__])
    result2 = execute('stat', __file__)
    assert result1 == result2


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

