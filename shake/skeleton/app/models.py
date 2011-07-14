# -*- coding: utf-8 -*-
from datetime import datetime

# from shake import cached_property
# from shakext.sqlalchemy import SQLAlchemy

from . import settings


db = SQLAlchemy(settings.SQLALCHEMY_URI, echo=False)


# ACTIVE_USER = 'A'
# SUSPENDED_USER = 'S'
# 
# 
# class User(db.Model):
# 
#     id = db.Column(db.Integer, primary_key=True)
#     login = db.Column(db.Unicode(255), unique=True, nullable=False)
#     password = db.Column(db.Unicode(140), nullable=True)
#     fullname = db.Column(db.Unicode(255), nullable=False, default='')
#     date_joined = db.Column(db.DateTime, default=datetime.utcnow,
#         nullable=False)
#     last_sign_in = db.Column(db.DateTime, nullable=True)
#     status = db.Column(db.String(1), default=ACTIVE_USER, nullable=False)
#     perms = db.Column(db.Text, nullable=False, default='')
# 
#     def __init__(self, login, password=None, fullname=''):
#         self.login = login
#         self.password = password
#         self.fullname = fullname
# 
#     @property
#     def is_active(self):
#         return self.status == ACTIVE_USER
# 
#     @property
#     def is_suspended(self):
#         return self.status == SUSPENDED_USER
# 
#     @cached_property
#     def perms_list(self):
#         return self.perms.strip().split(' ')
# 
#     def has_perm(self, perm):
#         return perm in self.perms_list
# 
#     def add_perms(self, perms):
#         curr_perms = self.perms_list
#         curr_perms.extend(perms)
#         # Filter duplicates
#         curr_perms = list(set(curr_perms))
#         self.perms = ' '.join(curr_perms)
# 
#     def __repr__(self):
#         return '<%s %s (%s)>' % (self.__class__.__name__, self.fullname,
#             self.login)
# 
# 
# auth = Auth(settings.AUTH_SETTINGS, db, User)
