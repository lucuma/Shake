# -*- coding: utf-8 -*-
"""

    :copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
    :license: BSD. See LICENSE for more details.

"""
import os
import unittest
from datetime import datetime

import shake

from shakext.sqlalchemy import SQLAlchemy
from shakext.sqltree import (MPTreeMixin, PathOverflow, PathTooDeep,
    inc_path, dec_path)


class TestIncDecPath(unittest.TestCase):

    def test_inc_path(self):
        assert inc_path('0000', 4) == '0001'
        assert inc_path('3GZU', 4) == '3GZV'
        assert inc_path('337Z', 2) == '3380'
        assert inc_path('GWZZZ', 5) == 'GX000'
        self.assertRaises(PathOverflow, inc_path, 'ZZZZ', 4)

    def test_dec_path(self):
        assert dec_path('0001', 4) == '0000'
        assert dec_path('3GZV', 4) == '3GZU'
        assert dec_path('3380', 2) == '337Z'
        assert dec_path('GX000', 5) == 'GWZZZ'
        self.assertRaises(PathOverflow, dec_path, '0000', 4)


if __name__ == '__main__':
    unittest.main()
