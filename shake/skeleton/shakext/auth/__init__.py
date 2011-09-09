# -*- coding: utf-8 -*-
"""
    Shake-Auth
    --------------------

    Shake's awesome authentication extension.


    :copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
    :license: BSD. See LICENSE for more details.

"""
from .auth import (Auth, CREDENTIAL_LOGIN, CREDENTIAL_PASSWORD,
    CREDENTIAL_TOKEN, UserExistsError, UserDoesNotExistsError,
    PasswordTooShortError)
from .perms import protected, invalid_csrf_secret
from .utils import get_user_model
