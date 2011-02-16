# -*- coding: utf-8 -*-
"""
    :copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
    :license: BSD. See LICENSE for more details.
"""
import os
import random
import time
import unittest

from shake import Shake, Rule, url_for
from shake.helpers import url_join, execute, to64, from64, to36, from36 


def index(request, name=None):
    msg = 'hello'
    if hasattr(request, 'foo'):
        msg = 'foo bar'
    return msg


class TestUrlFor(unittest.TestCase):

    def test_url_for(self):
        def home(request, name=None):
            msg = 'hello'
            if name:
                msg += ' ' + name
            return msg
        
        def index(request):
            return url_for(home, name='world')
        
        urls = [
            Rule('/', index),
            Rule('/home/', home),
            Rule('/hello/<name>/', home),
            ]
        app = Shake(urls)
        c = app.test_client()
        resp = c.get('/')
        assert resp.data == '/hello/world/'
    
    def test_named_url_for(self):
        def myview(request):
            result = [url_for('a'), url_for('b'), url_for('c')]
            return ' '.join(result)
        
        urls = [
            Rule('/', myview),
            Rule('/home1/', index, name='a'),
            Rule('/home2/', index, name='b'),
            Rule('/home3/', index, name='c'),
            ]
        app = Shake(urls)
        c = app.test_client()
        resp = c.get('/')
        assert resp.status_code == 200
        assert resp.data == '/home1/ /home2/ /home3/'
    
    def test_named_url_for_dup(self):
        def myview(request):
            return url_for('a')
        
        urls = [
            Rule('/', myview),
            Rule('/home1/', index, name='a'),
            Rule('/home2/', index, name='a'),
            Rule('/home3/', index, name='a'),
            ]
        app = Shake(urls)
        c = app.test_client()
        resp = c.get('/')
        assert resp.status_code == 200
        assert resp.data == '/home3/'


class TestUtils(unittest.TestCase):
    
    def test_url_join(self):
        expected = '/path/dir'
        assert url_join('/path', 'dir') == expected
        assert url_join('/path/', '/dir') == expected
        assert url_join('/path/', 'dir1/', '//dir2/', '/dir3/') == \
            '/path/dir1/dir2/dir3'
        assert url_join('/path/', 'dir1/', '/dir2//', '../dir3/') == \
            '/path/dir1/dir3'
    
    def test_execute(self):
        self.assertRaises(OSError, execute, 'qwerty999654321x')
        result1 = execute('stat', [__file__])
        result2 = execute('stat', __file__)
        assert result1 == result2


class TestToFrom64(unittest.TestCase):

    def test_to64(self):
        assert to64(0) == '0'
        assert to64(10) == 'a'
        assert to64(125) == '1Z'
        assert to64(126) == '1='
        assert to64(127) == '1_'
        assert to64(128) == '20'
        self.assertRaises(AssertionError, to64, -1)
        self.assertRaises(AssertionError, to64, 'a')
        assert len(to64(pow(3, 1979))) == 523
    
    def test_from64(self):
        assert from64('0') == 0
        assert from64('a') == 10
        assert from64('1Z') == 125
        assert from64('1=') == 126
        assert from64('1_') == 127
        assert from64('20') == 128
        self.assertRaises(ValueError, from64, '!')
    
    def test_custom_alphabet64(self):
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
        
        self.assertEqual(from64(to64(rnum, CUSTOM), CUSTOM), rnum)
        self.assertEqual(from64(to64(rnum, RANDOM), RANDOM), rnum)
        self.assertEqual(from64(to64(rnum, RCUSTOM), RCUSTOM), rnum)
        
    def test_custom_alphabet64_invalid(self):
        CUSTOM = 'abcdefghijklmnopqrstuvwxyz0123456789.:,;*@#$%&/()[]{}=_-ABCDEFGH'
        
        # bad custom alphabet
        self.assertRaises(AssertionError, to64, 1, 'bad')
        self.assertRaises(AssertionError, to64, 1, CUSTOM + '!-')
        
        # values not in custom alphabet
        self.assertRaises(ValueError, from64, 'J', CUSTOM)
        self.assertRaises(ValueError, from64, '!', CUSTOM)


class TestToFrom36(unittest.TestCase):

    def test_to36(self):
        assert to36(0) == '0'
        assert to36(10) == 'a'
        assert to36(125) == '3h'
        assert to36(143) == '3z'
        assert to36(144) == '40'
        self.assertRaises(AssertionError, to36, -1)
        self.assertRaises(AssertionError, to36, 'a')
        assert len(to36(pow(3, 1979))) == 607
    
    def test_from36(self):
        assert from36('0') == 0
        assert from36('a') == 10
        assert from36('3h') == 125
        assert from36('3z') == 143
        assert from36('40') == 144
        self.assertRaises(ValueError, from36, '!')
    
    def test_custom_alphabet36(self):
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
        
        self.assertEqual(from36(to36(rnum, CUSTOM), CUSTOM), rnum)
        self.assertEqual(from36(to36(rnum, RANDOM), RANDOM), rnum)
        self.assertEqual(from36(to36(rnum, RCUSTOM), RCUSTOM), rnum)
    
    def test_custom_alphabet36_invalid(self):
        CUSTOM = '9876543210ZYXWVUTSRQPONMLKJIHGFEDCBA'
        
        # bad custom alphabet
        self.assertRaises(AssertionError, to36, 1, 'bad')
        self.assertRaises(AssertionError, to36, 1, CUSTOM + 'abc')
        
        # values not in custom alphabet
        self.assertRaises(ValueError, from36, 'ab', CUSTOM)
        self.assertRaises(ValueError, from36, '!', CUSTOM)


if __name__ == '__main__':
    unittest.main()

