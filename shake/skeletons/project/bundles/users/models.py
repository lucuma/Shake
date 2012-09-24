# -*- coding: utf-8 -*-
"""
    Users models
    -------------------------------

"""
from datetime import datetime

import shake
from shake import cached_property, to_unicode

from main import app, db
from bundles.common.models import AuditableMixin


ACTIVE_USER = 'A'
SUSPENDED_USER = 'S'


class Role(db.Model):
    
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.Unicode(64), unique=True)

    def __init__(self, name, **kwargs):
        self.name = to_unicode(name)
        db.Model.__init__(self, **kwargs)

    @classmethod
    def by_name(cls, name):
        name = to_unicode(name)
        return db.query(cls).filter(cls.name == name).first()

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.name.encode('utf8'))


class User(db.Model, AuditableMixin):

    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)

    login = db.Column(db.String(255), unique=True,
        nullable=False)

    password = db.Column(db.String(300))

    email = db.Column(db.Unicode(300))

    fullname = db.Column(db.Unicode(255),
        default=u'')

    last_sign_in = db.Column(db.DateTime)

    status = db.Column(db.String(1), default=ACTIVE_USER,
        nullable=False)

    roles = db.relationship(Role, secondary='users_roles', lazy='joined',
        backref=db.backref('users', lazy='dynamic'))

    def __init__(self, login, password=None, **kwargs):
        self.login = to_unicode(login)
        self.password = password
        kwargs.setdefault('fullname', u'')
        db.Model.__init__(self, **kwargs)

    @classmethod
    def by_login(cls, login):
        login = to_unicode(login)
        return db.query(cls).filter(cls.login == login).first()

    @property
    def is_active(self):
        """Returns `True` if the user is active."""
        return self.status == ACTIVE_USER

    def add_role(self, name):
        """Adds a role (by name) to the user."""
        role = Role.by_name(name)
        if not role:
            role = Role(name)
            db.add(role)
        if not role in self.roles:
            self.roles.append(role)

    def remove_role(self, name):
        """Remove a role (by name) from the user."""
        role = Role.by_name(name)
        if not role:
            return
        if role in self.roles:
            self.roles.remove(role)

    def __repr__(self):
        return '<%s %s (%s)>' % (self.__class__.__name__,
            self.fullname.encode('utf8') or '?', self.login.encode('utf8'))


UsersRolesTable = db.Table('users_roles', db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey(User.id)),
    db.Column('role_id', db.Integer, db.ForeignKey(Role.id))
)


def create_admin():
    """Create the admin user (if it doesn't already exist)"""
    from pyceo import prompt
    from .manage import create_user
    
    u = User.by_login(u'admin')
    if not u:
        print 'Creating the `admin` user…'
        email = prompt('>>> `admin` email?\n')
        create_user(u'admin', 'admin', fullname=u'Admin', email=email)
        u = User.by_login(u'admin')

    u.add_role(u'admin')
    db.commit()
    return u

