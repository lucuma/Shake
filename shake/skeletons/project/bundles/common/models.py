# -*- coding: utf-8 -*-
"""
    Common models
    -------------------------------
    
"""
from datetime import datetime

import shake

from main import app, db


class BaseMixin(object):
    
    id = db.Column(db.Integer, primary_key=True)
    
    deleted = db.Column(db.Boolean, nullable=False,
        default=False)
    
    def __repr__(self):
        return '<%s %d>' % (self.__class__.__name__, self.id)


class AuditableMixin(object):
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow,
        nullable=False)

    modified_at = db.Column(db.DateTime, default=datetime.utcnow,
        onupdate=datetime.utcnow, nullable=False)


