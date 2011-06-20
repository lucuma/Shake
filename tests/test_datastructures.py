# -*- coding: utf-8 -*-
"""
    :copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
    :license: BSD. See LICENSE for more details.
"""
import pytest

from shake import StorageDict


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

