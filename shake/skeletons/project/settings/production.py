# -*- coding: utf-8 -*-
"""
Production environment settings
"""
from mailshake import SMTPMailer

from .base import *


debug = False
reload = False

sqlalchemy_uri = 'postgresql://username:password@127.0.0.1/database'

page_not_found = 'bundles.common.controllers.not_found'
page_error = 'bundles.common.controllers.critical_error'
page_not_allowed = 'bundles.common.controllers.not_allowed'

mailer_class = SMTPMailer
mailer_settings = {
    'host': 'localhost',
    'username': 'xxxxxx',
    'password': 'xxxxx',
    'use_tls': True
}

# You might need to uncomment this line for deploying with FastCGI
# force_script_name = ''
