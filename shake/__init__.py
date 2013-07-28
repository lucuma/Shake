# -*- coding: utf-8 -*-
"""
--------------------------
Shake
--------------------------

Shake is a lightweight web framework based on Werkzeug and Jinja2.
It can be considered a simpler alternative to Flask.

:
    from shake import Shake

    app = Shake(__file__)

    app.route('/', hello)
    def hello(request):
        return 'Hello World!'

    if __name__ == "__main__":
        app.run()

The most important differences from Flask are:

* The `request` object is passed explicity
* Any template can be rendered whitout an active request (unless you're trying to use the request object in the template.)
* The URLs are declared separately from the views, instead of using decorators.
* No blueprints. Instead:
    - The URL submonting are done by using the Werkzeug routing functions directly (`Submount`, `EndpointPrefix`, etc.)
    - Any static folder must be defined explicity.
* No `abort(code)`. The Werkzeug exceptions are used instead.

---------------------------------------
© 2010 by [Lúcuma] (http://lucumalabs.com).
See `AUTHORS.md` for more details.
License: [MIT License] (http://www.opensource.org/licenses/mit-license.php).
See LICENSE.md for more details

"""
# Utilities we import from Werkzeug that are unused
# in the module but are exported as public interface.
from werkzeug.exceptions import *
from werkzeug.utils import redirect

from .app import *
from .helpers import *
from .render import *
from .serializers import *
from .session import *
from .templates import *
from .views import *
from .wrappers import *


__version__ = '2.0'
