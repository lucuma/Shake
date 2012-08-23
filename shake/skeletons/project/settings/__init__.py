# -*- coding: utf-8 -*-
"""
    Project settings
    -------------------------------
    
"""
import shake


if shake.env_is('production'):
    import settings.prod as settings
elif shake.env_is('testing'):
    import settings.test as settings
else:
    import settings.dev as settings


# # Import local settings
# try:
#     import settings.local as settings
# except ImportError:
#     pass
