# -*- coding: utf-8 -*-
import pytest
from shake.cli.helpers import make_secret


def test_secret_uniqueness():
    for i in range(1000):
        assert make_secret() != make_secret()
