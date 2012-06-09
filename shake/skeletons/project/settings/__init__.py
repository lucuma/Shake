# -*- coding: utf-8 -*-
"""
Project settings
"""
import shake


if shake.env_is('production'):
    from production import Production
    settings = Production()

elif shake.env_is('testing'):
    from testing import Testing
    settings = Testing()

else:
    from development import Development
    settings = Development()

# # Import local settings
# try:
#     from local import Settings
#     settings = Settings()
# except ImportError:
#     pass
