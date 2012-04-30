# -*- coding: utf-8 -*-
"""
Production settings
"""
from mailshake import SMTPMailer


DEBUG = False

# SQLALCHEMY_URI = 'postgresql://username:password@127.0.0.1/database'

PAGE_NOT_FOUND = 'bundles.common.controllers.not_found'
PAGE_ERROR = 'bundles.common.controllers.critical_error'
# PAGE_NOT_ALLOWED = 'bundles.common.controllers.not_allowed'


# MAILER_CLASS = SMTPMailer
# MAILER_SETTINGS = {
#     'host': 'localhost',
#     'username': 'xxxxxx',
#     'password': 'xxxxx',
#     'use_tls': True
# }


# You might need to uncomment this line for deploying with FastCGI
# FORCE_SCRIPT_NAME = ''
