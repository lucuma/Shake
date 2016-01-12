# coding=utf-8
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

    :copyright: `Lúcuma labs S.A.C. <http://lucumalabs.com>`_.
    :license: MIT, see LICENSE for more details.

"""
# Utilities we import from Werkzeug that are unused
# in the module but are exported as public interface.
from jinja2.exceptions import TemplateNotFound # noqa
from werkzeug.exceptions import *
from werkzeug.urls import url_quote, url_unquote # noqa
from werkzeug.utils import cached_property, import_string, redirect # noqa

from .app import *
from .helpers import *
from .render import *
from .routes import *
from .serializers import json  # noqa
from .session import *
from .templates import *
from .views import *
from .wrappers import *


## Aliases
NotAllowed = Forbidden
redirect_to = redirect

__version__ = '1.6.5'
