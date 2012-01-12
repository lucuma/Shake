# -*- coding: utf-8 -*-
from datetime import datetime

from shake_sqlalchemy import SQLAlchemy

from .settings import SQLALCHEMY_URI


db = SQLAlchemy(SQLALCHEMY_URI, echo=False)


class BaseMixin(object):

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow,
        nullable=False)
    modified = db.Column(db.DateTime, default=datetime.utcnow,
        nullable=False)
    
    def __repr__(self):
        return '<%s %d>' % (self.__class__.__name__, self.id)