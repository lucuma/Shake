# -*- coding: utf-8 -*-
"""
    --------------------------
    Shake
    --------------------------

    A web framework mixed from the best ingredients.
    It can be minimal like this:

        from shake import Shake

        app = Shake(__file__)

        app.route('/', hello)
        def hello(request):
            return 'Hello World!'        

        if __name__ == "__main__":
            app.run()

    Or a full featured (yet configurable if you need it) framework.

    ---------------------------------------
    © 2010 by [Lúcuma] (http://lucumalabs.com).
    See `AUTHORS.md` for more details.
    License: [MIT License] (http://www.opensource.org/licenses/mit-license.php).

    Portions of code and/or inspiration taken from:
    * Werkzeug <werkzeug.pocoo.org> Copyright 2010, the Werkzeug Team.
    * Flask <flask.pocoo.org> Copyright 2010, Armin Ronacher.
    Used under the modified BSD license. See LEGAL.md for more details

"""
# Utilities we import from Werkzeug that are unused
# in the module but are exported as public interface.
from jinja2.exceptions import TemplateNotFound
from werkzeug.exceptions import *
from werkzeug.urls import url_quote, url_unquote
from werkzeug.utils import cached_property, import_string, redirect

from .app import *
from .helpers import *
from .render import *
from .routes import *
from .serializers import json
from .session import *
from .templates import *
from .views import *
from .wrappers import *


## Aliases
NotAllowed = Forbidden
redirect_to = redirect

__version__ = '1.5.4'

