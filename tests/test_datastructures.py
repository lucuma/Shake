# -*- coding: utf-8 -*-
"""
    :copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
    :license: BSD. See LICENSE for more details.
"""
import unittest

from shake import ObjDict


class TestObjDict(unittest.TestCase):

    def test_getitems(self):
        o = ObjDict(a=1, b=2, c='3')
        assert o.a == o['a']
        assert o.a == 1
        assert o.b == o['b']
        assert o.b == 2
        assert o.c == o['c']
        assert o.c == '3'
        
        del o.b
        assert o.get('b') == None
        
        o.d = 4
        assert o.d == 4
        
        o.update({'a':10, 'c':12})
        assert o.a == 10
        assert o.c == 12


if __name__ == '__main__':
    unittest.main()

