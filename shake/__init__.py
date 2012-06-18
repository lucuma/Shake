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


---------------------------------------
Copyright © 2010-2012 by [Lúcuma labs] (http://lucumalabs.com).
See `AUTHORS.md` for more details.
License: [MIT License] (http://www.opensource.org/licenses/mit-license.php).

Portions of code and/or inspiration taken from:
* Flask <flask.pocoo.org> Copyright 2010, Armin Ronacher.
* Werkzeug <werkzeug.pocoo.org> Copyright 2010, the Werkzeug Team.
Used under the modified BSD license. See LEGAL.md for more details

"""
# Utilities we import from Jinja2 and Werkzeug that are unused
# in the module but are exported as public interface.
from jinja2 import escape, Markup
from werkzeug.exceptions import *
from werkzeug.urls import url_quote, url_unquote
from werkzeug.utils import cached_property, import_string, redirect

from .app import *
from .controllers import *
from .helpers import *
from .routes import *
from .serializers import json
from .views import *
from .wrappers import *


## Aliases
NotAllowed = Forbidden
ViewNotFound = TemplateNotFound
redirect_to = redirect

__version__ = '1.1.13'

