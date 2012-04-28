# -*- coding: utf-8 -*-
"""
"""
from datetime import datetime

import shake
from shake import cached_property

from main import app, db


ACTIVE_USER = 'A'
SUSPENDED_USER = 'S'


class User(db.Model):

    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)

    login = db.Column(db.String(255), unique=True,
        nullable=False)

    password = db.Column(db.String(300))

    email = db.Column(db.String(300))

    fullname = db.Column(db.Unicode(255),
        default=u'')

    created_at = db.Column(db.DateTime, default=datetime.utcnow,
        nullable=False)

    modified_at = db.Column(db.DateTime, default=datetime.utcnow,
        nullable=False)

    last_sign_in = db.Column(db.DateTime)

    status = db.Column(db.String(1), default=ACTIVE_USER,
        nullable=False)

    perms = db.Column(db.Text, default='')

    def __init__(self, login, password=None, fullname=u'', email=None):
        self.login = login
        self.password = password
        self.fullname = fullname
        self.email = email

    @property
    def is_active(self):
        return self.status == ACTIVE_USER

    @property
    def is_suspended(self):
        return self.status == SUSPENDED_USER

    @cached_property
    def perms_list(self):
        return self.perms.strip().split(' ')

    def has_perm(self, perm):
        return perm in self.perms_list

    def add_perms(self, perms):
        curr_perms = self.perms_list
        curr_perms.extend(perms)
        # Filter duplicates
        curr_perms = list(set(curr_perms))
        self.perms = ' '.join(curr_perms)

    def __repr__(self):
        return '<%s %s (%s)>' % (self.__class__.__name__, self.fullname,
            self.login)


def create_admin():
    """Create the admin user (if it don't already exist)"""
    from pyceo import prompt
    from .manage import create_user
    
    u = db.query(User).filter(User.login=='admin').first()
    if not u:
        print 'Creating `admin` user…'
        email = prompt('>>> Admin email?\n')
        create_user(u'admin', '123456', fullname=u'Admin', email=email)

