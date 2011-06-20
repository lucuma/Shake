# -*- coding: utf-8 -*-
"""
    shake.datastructures
    ----------------------------------------------

    :copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
    :license: BSD. See LICENSE for more details.

"""


class StorageDict(dict):
    """A StorageDict object is like a dictionary except ``obj.key`` can be used
    in addition to ``obj['key']`.

    Basic Usage:

    >>> o = StorageDict(a=1)
    >>> o.a
    1
    >>> o['a']
    1
    >>> o.a = 2
    >>> o['a']
    2
    >>> del o.a
    >>> print o.a
    None

    """
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError, error:
            raise AttributeError(error)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError, error:
            raise AttributeError(error)

    def __repr__(self):
        return '<StorageDict ' + dict.__repr__(self) + '>'

    def __getstate__(self):
        return dict(self)

    def __setstate__(self, value):
        for (key, value) in value.items():
            self[key] = value
