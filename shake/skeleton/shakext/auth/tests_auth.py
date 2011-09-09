# -*- coding: utf-8 -*-
"""
"""
import os
import unittest

from shake import (Shake, Response, Rule)

from shakext.auth.utils import hash_sha256, hash_sha512, hash_bcrypt
