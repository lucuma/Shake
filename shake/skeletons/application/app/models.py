# -*- coding: utf-8 -*-
from shake_sqlalchemy import SQLAlchemy

from .settings import SQLALCHEMY_URI


db = SQLAlchemy(SQLALCHEMY_URI, echo=False)

