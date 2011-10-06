# -*- coding: utf-8 -*-
from shake import Rule, EndpointPrefix, Submount

from .models import auth


urls = [
    # Submount('', auth.get_urls()),
    # EndpointPrefix('app.controllers.', [
    #     Rule('/', 'index'),
    # ]),
]
