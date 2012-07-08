# -*- coding: utf-8 -*-
"""
    Project settings
    -------------------------------
    
"""
import shake


if shake.env_is('production'):
    import settings.production as settings
elif shake.env_is('testing'):
    import settings.testing as settings
else:
    import settings.development as settings


# # Import local settings
# try:
#     import settings.local as settings
# except ImportError:
#     pass
