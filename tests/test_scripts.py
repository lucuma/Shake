# -*- coding: utf-8 -*-
"""
    Copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
    MIT License. (http://www.opensource.org/licenses/mit-license.php)
"""
import pytest

from shake.scripts import make_secret


def test_secret_uniqueness():
    for i in range(1000):
        assert make_secret() != make_secret()
