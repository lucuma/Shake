# -*- coding: utf-8 -*-
"""
"""
import os
import unittest

cwd = os.getcwd()
settings = {
    'SECRET_KEY': 'q' * 20,
    'EXTENSIONS': ['auth'],
    }
