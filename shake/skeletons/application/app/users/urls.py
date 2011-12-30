# -*- coding: utf-8 -*-
from shake import Rule, EndpointPrefix, Submount

from .models import auth


user_urls = [
    Submount('', auth.get_urls()),
]
