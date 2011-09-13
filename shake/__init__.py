# -*- coding: utf-8 -*-
"""
    Shake
    ======
    
    A web framework mixed from the best ingredients.
    
    Coded with love by Juan-Pablo Scaletti.
    
    Portions of code and/or inspiration taken from:
    - Flask <flask.pocoo.org> Copyright 2010, Armin Ronacher.
    - Werkzeug <werkzeug.pocoo.org> Copyright 2010, the Werkzeug Team.
    - Django <djangoproject.com> Copyright 2005, Django Software Foundation.
    
    See AUTHORS for more details
    
    :Copyright © 2010-2011 by Lúcuma labs (http://lucumalabs.com).
    :MIT License. (http://www.opensource.org/licenses/mit-license.php)

"""
try:
    import jinja2
except ImportError:
    raise ImportError('Unable to load the jinja2 package.'
        ' Shake needs the Jinja2 library to run.'
        ' You can get it from http://pypi.python.org/pypi/Jinja2'
        ' If you\'ve already installed Jinja2, then make sure you have '
        ' it in your PYTHONPATH.')
try:
    import werkzeug
except ImportError:
    raise ImportError('Unable to load the werkzeug package.'
        ' Shake needs the Werkzeug library to run.'
        ' You can get it from http://werkzeug.pocoo.org/download\n'
        ' If you\'ve already installed Werkzeug, then make sure you have '
        ' it in your PYTHONPATH.')

# Utilities we import from Werkzeug and Jinja2 that are unused
# in the module but are exported as public interface.
from jinja2 import escape, Markup
from werkzeug.exceptions import (abort, HTTPException, Forbidden,
    MethodNotAllowed, NotFound)
NotAllowed = Forbidden
from werkzeug.urls import url_quote, url_unquote
from werkzeug.utils import cached_property, import_string, redirect

from .app import Shake
from .controllers import (not_found_page, error_page, not_allowed_page,
    render_view, send_file, from_dir)
from .datastructures import StorageDict
from .helpers import (local, json, url_for, execute, to64, from64,
    to36, from36)
from .manager import (Manager, manager, prompt, prompt_pass, prompt_bool,
    prompt_choices)
from .routes import (Rule, RuleFactory, Subdomain, Submount, EndpointPrefix,
    RuleTemplate, Map, MapAdapter, BuildError, RequestRedirect, RequestSlash)
from .views import (Render, TemplateNotFound, flash, get_messages,
    get_csrf_secret, new_csrf_secret)
ViewNotFound = TemplateNotFound
from .wrappers import Request, Response, SecureCookie


__version__ = '0.5.2'
