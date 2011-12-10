# -*- coding: utf-8 -*-
"""
    # Shake

    A web framework mixed from the best ingredients:

        from shake import Shake, Rule

        def hello(request):
            return 'Hello World!'

        urls = [Rule('/', hello),]

        app = Shake(urls)

        if __name__ == "__main__":
            app.run()


    --------------------------------
    Copyright © 2010-2011 by Lúcuma labs (http://lucumalabs.com).
    See AUTHORS for more details
    MIT License. (http://www.opensource.org/licenses/mit-license.php)

    Portions of code and/or inspiration taken from:
    * Flask <flask.pocoo.org> Copyright 2010, Armin Ronacher.
    * Werkzeug <werkzeug.pocoo.org> Copyright 2010, the Werkzeug Team.
    Used under the modified BSD license. See LEGAL.md for more details

"""
# Utilities we import from Jinja2 and Werkzeug that are unused
# in the module but are exported as public interface.
from jinja2 import escape, Markup
from werkzeug.exceptions import (abort, HTTPException, Forbidden,
    MethodNotAllowed, NotFound, RequestEntityTooLarge, UnsupportedMediaType)
NotAllowed = Forbidden
from werkzeug.urls import url_quote, url_unquote
from werkzeug.utils import cached_property, import_string, redirect

from . import pyceo, voodoo
from .app import Shake
from .controllers import (not_found_page, error_page, not_allowed_page,
    render_view)
from .helpers import (local, Local, LocalProxy, json, url_for,
    path_join, url_join, to64, from64, to36, from36,
    StorageDict, safe_join, send_file, to_unicode, to_bytestring)
from .routes import (Rule, RuleFactory, Subdomain, Submount, EndpointPrefix,
    RuleTemplate, Map, MapAdapter, BuildError, RequestRedirect, RequestSlash)
from .views import (BaseRender, Render, TemplateNotFound,
    flash, get_messages, get_csrf_secret, new_csrf_secret)
ViewNotFound = TemplateNotFound
from .wrappers import Request, Response, SecureCookie, Settings


manager = pyceo.Manager()

__version__ = '0.29'

