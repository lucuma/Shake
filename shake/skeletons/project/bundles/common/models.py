# -*- coding: utf-8 -*-
from datetime import datetime

import shake
from shake import url_for, get_csrf, to_unicode
from slugify import slugify # from libs
from sqlalchemy.orm import validates

from main import db


class BaseMixin(object):
    
    id = db.Column(db.Integer, primary_key=True)
    deleted = db.Column(db.Boolean, default=False, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow,
        nullable=False)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow,
        onupdate=datetime.utcnow, nullable=False)

    @classmethod
    def by_id(cls, item_id, deleted=False):
        item = db.query(cls).get(item_id)
        if not item or (item.deleted and not deleted):
            raise shake.NotFound
        return item

    @classmethod
    def get_all(cls, deleted=False):
        query = db.query(cls)
        if deleted is not None:
            query = query.filter(cls.deleted == deleted)
        return query

    @classmethod
    def get_all_in(cls, ids, deleted=False):
        query = db.query(cls).filter(cls.id.in_(ids))
        if deleted is not None:
            query = query.filter(cls.deleted == deleted)
        return query

    @classmethod
    def delete_all(cls, ids):
        ids = list(ids)
        if not ids:
            return
        db.query(cls).filter(cls.id.in_(ids)).delete(synchronize_session='fetch')

    def get_show_url(self, external=False):
        return url_for(self.__tablename__ + '.show', item_id=self.id, external=external)

    def get_edit_url(self):
        return url_for(self.__tablename__ + '.edit', item_id=self.id)

    def get_delete_url(self):
        csfr = get_csrf()
        data = {
            'item_id': self.id,
            csfr.name: csfr.value,
        }
        return url_for(self.__tablename__ + '.delete', **data)

    def get_restore_url(self):
        csfr = get_csrf()
        data = {
            'item_id': self.id,
            csfr.name: csfr.value,
        }
        return url_for(self.__tablename__ + '.restore', **data)

    def delete(self):
        self.deleted = True
        db.commit()

    def restore(self):
        self.deleted = False
        db.commit()


class SluggableMixin(object):

    name = db.Column(db.Unicode(220), default=u'')
    slug = db.Column(db.String(220), default='')

    def __init__(self, name, *args, **kwargs):
        self.name = to_unicode(name)
        db.Model.__init__(self, *args, **kwargs)

    @validates('name')
    def _set_slug(self, key, value):
        """Update the slug when the name change."""
        self.slug = slugify(value)
        return value

    @classmethod
    def by_slug(cls, slug):
        return db.query(cls).filter(cls.slug == slug).first()

