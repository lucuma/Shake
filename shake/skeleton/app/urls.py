# -*- coding: utf-8 -*-
from shake import Rule, EndpointPrefix, Submount

from .models.users import auth


urls = [
    # Submount('', auth.get_urls()),
    # EndpointPrefix('app.controllers.main.', [
    #     Rule('/', 'index'),
    # ]),
]
