# -*- coding: utf-8 -*-
from datetime import datetime

from shake import cached_property
from shake_auth import Auth
from sqlalchemy import *

from ..settings import AUTH_SETTINGS
from ..models import db


ACTIVE_USER = 'A'
SUSPENDED_USER = 'S'


class User(db.Model):

    id = Column(Integer, primary_key=True)
    login = Column(String(255), unique=True, nullable=False)
    password = Column(String(300))
    fullname = Column(Unicode(255), default=u'')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_sign_in = Column(DateTime)
    status = Column(String(1), default=ACTIVE_USER, nullable=False)
    perms = Column(Text, default='')

    def __init__(self, login, password=None, fullname=u''):
        self.login = login
        self.password = password
        self.fullname = fullname

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


auth = Auth(AUTH_SETTINGS, db, User)
