# -*- coding: utf-8 -*-
"""
Production settings
"""
from mailshake import SMTPMailer


DEBUG = False

# SQLALCHEMY_URI = 'postgresql://username:password@127.0.0.1/database'

PAGE_NOT_FOUND = 'web.controllers.not_found'
PAGE_ERROR = 'web.controllers.critical_error'
# PAGE_NOT_ALLOWED = 'web.controllers.not_allowed'

# MAILER_CLASS = SMTPMailer
# MAILER_SETTINGS = {
#     'host': 'localhost',
#     'username': 'xxxxxx',
#     'password': 'xxxxx',
#     'use_tls': True
# }

# FORCE_SCRIPT_NAME = ''
