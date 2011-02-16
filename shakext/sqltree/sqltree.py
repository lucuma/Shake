# -*- coding: utf-8 -*-
"""
    Shake-SQLTree
    ----------------------------------------------

    Implements an efficient tree implementation using
    materialized paths.

    :copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
    :license: BSD. See LICENSE for more details.
"""
from __future__ import absolute_import

import sqlalchemy


ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
STEP_LENGTH = 4
PATH_FIELD_LENGTH = 255


class PathOverflow(Exception):
    "Base class for exceptions in calculations of node's path."


class PathTooDeep(PathOverflow):
    "Maximum depth of nesting limit is exceeded."


def inc_path(path, steplen):
    """Returns a new path which is greater than `path` by one.

    :param path: `str`, the path to increment.
    :param steplen: `int`, the number of maximum characters to carry overflow.

    :raises PathOverflow:
        when incrementation of `path` cause to carry overflow by number
        of characters greater than `steplen`.

    >>> inc_path('0000', 4)
    '0001'
    >>> inc_path('3GZU', 4)
    '3GZV'
    >>> inc_path('337Z', 2)
    '3380'
    >>> inc_path('GWZZZ', 5)
    'GX000'
    >>> inc_path('ZZZZ', 4)
    Traceback (most recent call last):
        ...
    PathOverflow

    """
    parent_path, path = path[:-steplen], path[-steplen:]
    path = path.rstrip(ALPHABET[-1])
    if not path:
        raise PathOverflow()
    zeros = steplen - len(path)
    path = path[:-1] + \
           ALPHABET[ALPHABET.index(path[-1]) + 1] + \
           ALPHABET[0] * zeros
    return parent_path + path


def dec_path(path, steplen):
    """Returns a new path which is lesser than `path` by one.

    :param path: `str`, the path to decrement.
    :param steplen: `int`, the number of maximum characters to carry overflow.

    :raises PathOverflow:
        when incrementation of `path` cause to carry overflow by number
        of characters greater than `steplen`.

    >>> dec_path('0001', 4)
    '0000'
    >>> dec_path('3GZV', 4)
    '3GZU'
    >>> dec_path('3380', 2)
    '337Z'
    >>> dec_path('GX000', 5)
    'GWZZZ'
    >>> dec_path('0000', 4)
    Traceback (most recent call last):
        ...
    PathOverflow

    """
    parent_path, path = path[:-steplen], path[-steplen:]
    path = path.rstrip(ALPHABET[0])
    if not path:
        raise PathOverflow()
    zeros = steplen - len(path)
    path = path[:-1] + \
           ALPHABET[ALPHABET.index(path[-1]) - 1] + \
           ALPHABET[-1] * zeros
    return parent_path + path


class MPTreeMixin(object):

    _mp_steplen = STEP_LENGTH
    _mp_pathfieldlen = PATH_FIELD_LENGTH

    path = sqlalchemy.Column(sqlalchemy.types.String(PATH_FIELD_LENGTH),
        nullable=False)

    def __init__(self, db):
        self.db = db
        cls = self.__class__
        parent_id = None
        parent_path = ''
        if self.parent:
            parent_id = self.parent.id
            parent_path = self.parent.path

        last_path = db.session.query(sqlalchemy.func.max(cls.path)) \
            .autoflush(False).filter(cls.parent_id == parent_id).scalar()

        if last_path:
            path = inc_path(last_path, self._mp_steplen)
        else:
            # node is the first child.
            path = parent_path + ALPHABET[0] * self._mp_steplen

        if len(path) > self._mp_pathfieldlen:
            raise PathTooDeep()

        self.path = path

    @property
    def depth(self):
        return len(self.path) / self._mp_steplen

    @property
    def is_first(self):
        return self.path == (ALPHABET[0] * self._mp_steplen)

    @property
    def query_children(self):
        cls = self.__class__
        return cls.query.filter_by(parent_id=self.id)

    @property
    def query_descendants(self):
        cls = self.__class__
        return cls.query.filter(cls.path.like(self.path + '%'))

    def move_to(self, before=None, parent=None):
        cls = self.__class__

        def replace_all_paths(oldpath, newpath, not_this=None):
            query = cls.query.filter(cls.path.like(oldpath + '%'))
            if not_this:
                query = query.filter(cls.id != not_this)

            query.update({
                    cls.path: cls.path.replace(oldpath, newpath)
                }, synchronize_session='fetch')

        if before:
            parent_id = before.parent_id
            new_path = dec_path(before.path, self._mp_steplen)
        elif parent:
            parent_id = parent.id
            last_path = self.db.session.query(sqlalchemy.func.max(cls.path)) \
                .autoflush(False).filter(cls.parent_id == parent_id).scalar()
            new_path = inc_path(last_path, self._mp_steplen)
        else:
            parent_id = None
            new_path = ALPHABET[0] * self._mp_steplen

        self.parent_id = parent_id
        replace_all_paths(self.path, new_path)

        nsibs = cls.query.filter_by(parent_id=parent_id) \
            .filter(cls.id != self.id) \
            .filter(cls.path >= new_path).order_by(cls.path.desc())

        for n in nsibs:
            new_path = inc_path(n.path, self._mp_steplen)
            replace_all_paths(n.path, new_path, not_this=self.id)

    @classmethod
    def query_tree(cls, parent=None):
        query = cls.query
        if not parent:
            return query
        return query.filter(cls.path.like(parent.path + '%'))

    @classmethod
    def query_roots(cls):
        return cls.query.filter(cls.parent_id == None)

    @classmethod
    def update_branch(cls, parent, data, sync='fetch'):
        cls.query.filter(cls.path.like(parent.path + '%')).update(data, sync)
