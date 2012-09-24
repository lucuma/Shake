# -*- coding: utf-8 -*-
"""
    Shake.app
    --------------------------

    This module implements the central WSGI application object.

"""
from datetime import datetime, timedelta
import io
import os
from os.path import isdir, dirname, join, abspath, normpath, realpath
import socket

from allspeak import I18n, LOCALES_DIR
from pyceo import Manager
from werkzeug.exceptions import HTTPException, NotFound, BadRequest
from werkzeug.local import LocalManager
from werkzeug.serving import run_simple
from werkzeug.utils import import_string

from .config import get_settings_object
from .helpers import local, to_unicode
from .render import Render, TEMPLATES_DIR
from .routes import Map, Rule
from .session import ItsdangerousSessionInterface
from .wrappers import Request, Response, make_response


__all__ = (
   'DataNotFound', 'Shake', 'set_env', 'get_env', 'env_is', 'manager'
)

local_manager = LocalManager([local])

SECRET_KEY_MINLEN = 20
STATIC_DIR = 'static'
WELCOME_MESSAGE = "Welcome aboard. You're now using Shake!"

ENV_FILE = '.SHAKE_ENV'
ENV_NAME = 'SHAKE_ENV'
DEFAULT_ENV = 'development'


class DataNotFound(NotFound):
    """A "data not found" exception, to differentiate it from a real
    `HTTP 404: NOT FOUND` while debugging.
    """
    pass

NotFound = DataNotFound


class Shake(object):
    """Implements a WSGI application and acts as the central
    object.
    
    root_path
    :   the root path of the application.  The `locales` and `templates` dirs
        will be based on this value.
    settings
    :   a module or dict with the custom settings.
    
    Usually you create a `Shake` instance in your main module or
    in the `__init__.py` file of your package like this:
        
        from shake import Shake
        app = Shake(__file__, settings)
    
    """
    
    # The class that is used for request objects.
    request_class = Request
    
    # The class that is used for response objects.
    response_class = Response

    
    def __init__(self, root_path=None, settings=None):
        # Functions to run before each request and response
        self.before_request_funcs = []
        # Functions to run before each response
        self.after_request_funcs = []
        # Functions to run if an exception occurs
        self.on_exception_funcs = []
        # A dict of static `url, path` pairs to be used during development.
        self.static_dirs = {}
        
        root_path = root_path or '.'
        root_path = normpath(abspath(realpath(root_path)))
        # Instead of a path, we've probably recieved the value of __file__
        if not isdir(root_path):
            root_path = dirname(root_path)
        self.root_path = root_path

        settings = get_settings_object(settings or {})
        self.settings = settings
        self.assert_secret_key()

        self.url_map = Map([], default_subdomain=settings.DEFAULT_SUBDOMAIN)
        self.error_handlers = {
            403: settings.PAGE_NOT_ALLOWED,
            404: settings.PAGE_NOT_FOUND,
            500: settings.PAGE_ERROR,
        }
        self.request_class.max_content_length = settings.MAX_CONTENT_LENGTH
        self.request_class.max_form_memory_size = settings.MAX_FORM_MEMORY_SIZE
        self.session_lifetime = timedelta(hours=settings.SESSION_LIFETIME)
        self.session_interface = ItsdangerousSessionInterface(self)
        self.create_default_services()
    
    def assert_secret_key(self):
        """Make sure the SECRET_KEY is long enough (only if there's one
        defined in the settings).

        """
        key = self.settings.SECRET_KEY
        if key and len(key) < SECRET_KEY_MINLEN:
            raise RuntimeError("Your 'SECRET_KEY' setting is too short to be"
                " safe.  Make sure is *at least* %i chars long."
                % SECRET_KEY_MINLEN)

    def create_default_services(self):
        """Creates the default `render` and `i18n` services using the
        `root_path` as the base path for the `'templates'` and `'locales'` dirs.

        """
        templates_dir = join(self.root_path, TEMPLATES_DIR)
        render = Render(templates_dir,
            default_mimetype=self.settings.get('DEFAULT_MIMETYPE'),
            response_class=self.response_class)

        locales_dir = (self.settings.get('LOCALES_DIR') or
            join(self.root_path, LOCALES_DIR))
        if isinstance(locales_dir, basestring):
            locales_dir = [locales_dir]
        get_request = lambda: local.request

        i18n = I18n(
            locales_dirs=locales_dir,
            get_request=get_request,
            default_locale=self.settings.DEFAULT_LOCALE,
            default_timezone=self.settings.DEFAULT_TIMEZONE
        )

        render.env.globals['t'] = i18n.translate
        render.env.filters.update({
            'format': i18n.format,
            'datetimeformat': i18n.format_datetime,
            'dateformat': i18n.format_date,
            'timeformat': i18n.format_time,
            'timedeltaformat': i18n.format_timedelta,
            'numberformat': i18n.format_number,
            'decimalformat': i18n.format_decimal,
            'currencyformat': i18n.format_currency,
            'percentformat': i18n.format_percent,
            'scientificformat': i18n.format_scientific,
        })

        self.render = render
        self.i18n = i18n
    
    def route(self, url, *args, **kwargs):
        """A decorator for mounting an endpoint in a URL.
        Example:

            @app.route('/')
            def example():
                return 'example'

        """
        def real_decorator(target):
            self.url_map.add(Rule(url, target, *args, **kwargs))
            return target
        return real_decorator
    
    def add_url(self, rule, *args, **kwargs):
        """Adds an URL rule.
        Example:


            def example():
                return 'example'

            app.add_url('/', example, name='myexample')

        """
        self.url_map.add(Rule(rule, *args, **kwargs))
    
    def add_urls(self, urls):
        """Adds all the URL rules from a list (or iterable).

        """
        for url in urls:
            self.url_map.add(url)
    
    def add_static(self, url, path):
        """Can be used to specify an URL for static files on the web and
        the folder with static files that should be served at that URL.
        Used only for the local development server.  In production, you'll have
        to define the static paths in your server config.

        """
        url = '/' + url.strip('/')
        path = normpath(abspath(realpath(path)))
        # Instead of a path, we've probably recieved the value of __file__
        if not isdir(path):
            path = join(dirname(path), STATIC_DIR)
        self.static_dirs[url] = path
    
    def before_request(self, function):
        """Register a function to run before each request.
        Can be used as a decorator.  See `preprocess_request()`.

        """
        if function not in self.before_request_funcs:
            self.before_request_funcs.append(function)
        return function
    
    def after_request(self, function):
        """Register a function to be run after each request.
        Your function must take one parameter, a response_class object and
        return a new response object or the same.  Can be used as a decorator.
        See `process_response()`.

        """
        if function not in self.after_request_funcs:
            self.after_request_funcs.append(function)
        return function

    before_response = after_request
    
    def on_exception(self, function):
        """Register a function to be run if an exception
        occurs.  Can be used as a decorator.

        """
        if function not in self.on_exception_funcs:
            self.on_exception_funcs.append(function)
        return function
    
    def preprocess_request(self, request, kwargs):
        for handler in self.before_request_funcs:
            resp_value = handler(request, **kwargs)
            if resp_value is not None:
                return resp_value

    def process_response(self, response):
        for handler in self.after_request_funcs:
            response = handler(response)
        return response

    def make_request(self, environ):
        request = self.request_class(environ)
        self.session_interface.open_session(request)
        local.request = request
        return request

    def wsgi_app(self, environ, start_response):
        """The actual WSGI application.  This is not implemented in
        `__call__` so that middlewares can be applied without losing a
        reference to the class.  So instead of doing this:
            
            app = MyMiddleware(app)
        
        It's a better idea to do this instead::
            
            app.wsgi_app = MyMiddleware(app.wsgi_app)
        
        Then you still have the original application object around and
        can continue to call methods on it.
        
        environ
        :   a WSGI environment
        start_response
        :   a callable accepting a status code, a list of headers and an
            optional exception context to start the response.

        """
        local.app = self
        self.force_script_name(environ)
        request = self.make_request(environ)
        response = self.dispatch(request)
        response = self.process_response(response)
        if isinstance(response, self.response_class):
            response = self.session_interface.save_session(request.session, response)
            print 'cookieheader', response.headers.getlist('Set-Cookie')
        local_manager.cleanup()
        return response(environ, start_response)

    def force_script_name(self, environ):
        """In some servers (like Lighttpd), when deploying using FastCGI
        and you want the application to work in the URL root you have to work
        around a bug by setting `FORCE_SCRIPT_NAME = ''`.

        """
        script_name = environ.get('SCRIPT_NAME')
        new_script_name = self.settings.FORCE_SCRIPT_NAME
        
        if (new_script_name != False) and script_name:
            environ['SCRIPT_NAME'] = new_script_name
            redirect_uri = environ.get('REDIRECT_URI')
            
            if redirect_uri:
                environ['REDIRECT_URI'] = redirect_uri.replace(
                    script_name, new_script_name)

    def dispatch(self, request):
        """Does the request dispatching.  Matches the URL and returns the
        return value of the view or error handler.  This does not have to
        be a response object.  In order to convert the return value to a
        proper response object, call `make_response`.

        If DEBUG=True, a `NotFound` exception emitted by your code is treated
        like a regular exception without error handlers, so it's easy
        to differetiate it from a real `HTTP 404: NOT FOUND`.

        """
        try:
            endpoint, kwargs = self.match_url(request)
            request.view_kwargs = kwargs
            resp_value = self.preprocess_request(request, kwargs)
            if resp_value is None:
                resp_value = endpoint(request, **kwargs)
            response = self.make_response(resp_value)

        except (HTTPException), exception:
            if self.settings.DEBUG and isinstance(exception, DataNotFound):
                response = self.handle_exception(request, error)
            else:
                response = self.handle_http_exception(request, exception)

        except (Exception), error:
            response = self.handle_exception(request, error)

        return response

    def match_url(self, request):
        local.urls = urls = self.create_url_adapter(request)
        rule, kwargs = urls.match(return_rule=True)
        endpoint = rule.endpoint
        if isinstance(endpoint, basestring):
            endpoint = import_string(endpoint)
        
        request.url_rule = rule
        request.endpoint = endpoint
        request.kwargs = kwargs
        return endpoint, kwargs

    def create_url_adapter(self, request):
        """Creates a URL adapter for the given request.

        """
        server_name = self.settings.SERVER_NAME
        port = self.settings.SERVER_PORT
        if port:
            server_name = '%s:%s' % (server_name, port)
        return self.url_map.bind_to_environ(request, server_name=server_name)

    def make_response(self, resp='', status=None, headers=None, **kwargs):
        """Converts the return value from a view function to a real
        response object that is an instance of `Shake.response_class`.
        
        The following types are allowed for `resp_value`:
            
        `None`
        :   an empty response object is created.
        `response`
        :   the object is returned unchanged.
        `str`
        :   a response object is created with the string as body.
        `unicode`
        :   a response object is created with the string encoded to utf-8
            as body.
        `dict`
        :   creates a response object with the JSON representation of the
            dictionary and the mimetype of `application/json`.
        WSGI function
        :   the function is called as WSGI application and buffered as
            response object.
        
        Parameters:

        resp_value
        :   the return value from the view function.
        status
        :   An optional status code.
        headers
        :   A dictionary with custom headers.
        
        return: an instance of `response_class`
        
        """
        return make_response(resp, status=status, headers=headers,
            response_class=self.response_class, **kwargs)

    def handle_http_exception(self, request, exception):
        """Handles an HTTP exception.  By default try to use the handler
        for that exception code.  If no such handler exists, in DEBUG mode
        the exception is re-raised, otherwise a default 500 internal
        server error message will be displayed.

        """
        status = exception.code
        # If less than 400 is not an error but flow control (eg. redirect)
        if status < 400:
            return exception

        for handler in self.on_exception_funcs:
            handler(exception)
        endpoint = self.error_handlers.get(status)
        if endpoint is None:
            if self.settings.DEBUG:
                raise
            endpoint = self.error_handlers.get(500)
        
        if isinstance(endpoint, basestring):
            endpoint = import_string(endpoint)
        resp_value = endpoint(request, exception)
        response = self.make_response(resp_value, status)
        return response

    def handle_exception(self, request, error):
        """Default exception handling that kicks in when an exception
        occours that is not caught.  In debug mode the exception is
        re-raised immediately, otherwise it is logged and the handler
        for a 500 internal server error is used.  If no such handler
        exists, a default 500 internal server error message is displayed.

        """
        for handler in self.on_exception_funcs:
            handler(error)
        if self.settings.DEBUG:
            raise
        endpoint = self.error_handlers.get(500)
        if isinstance(endpoint, basestring):
            endpoint = import_string(endpoint)
        resp_value = endpoint(request, error)
        response = self.make_response(resp_value, 500)
        return response

    def print_welcome_msg(self):
        """Prints a welcome message, if you run this application
        without declaring URLs first.

        """
        is_dev_server = os.environ.get('WERKZEUG_RUN_MAIN') != 'true'
        no_urls = len(self.url_map._rules) == 0
        if is_dev_server and no_urls:
            wml = len(WELCOME_MESSAGE) + 2
            print '\n '.join(['',
                '-' * wml,
                ' %s ' % WELCOME_MESSAGE,
                '-' * wml,
                ''])

    def print_help_msg(self, host, port):
        """Prints a help message.

        """
        if host == '0.0.0.0':
            print ' * Running on http://0.0.0.0:%s' % (port,)
            # local IP address for easy debugging.
            ips = [ip 
                for ip in socket.gethostbyname_ex(socket.gethostname())[2]
                if not ip.startswith("127.")
            ][:1]
            if ips:
                print ' * Running on http://%s:%s' % (ips[0], port)
        print '-- Quit the server with Ctrl+C --'

    def run(self, host=None, port=None, debug=None, reloader=None, 
            reloader_interval=2, threaded=True, processes=1,
            ssl_context=None, **kwargs):
        """Runs the application on a local development server.
        
        The development server is not intended to be used on production
        systems.  It was designed especially for development purposes and
        performs poorly under high load.
        
        host
        :   the host for the application. eg: 'localhost' or '0.0.0.0'.
        port
        :   the port for the server. eg: 8080.
        debug
        :   run in debug mode?  The default is the value of settings.DEBUG.
        reloader
        :   use the automatic reloader?  The default is the value of
            settings.RELOADER.
        reloader_interval
        :   the interval for the reloader in seconds.  Default `2`.
        threaded
        :   should the process handle each request in a separate thread?
            Default `False`.
        processes
        :   number of processes to spawn.  Default `1`.
        ssl_context
        :   an SSL context for the connection.  Either an OpenSSL context, the
            string 'adhoc' if the server should automatically create one, or
            `None` to disable SSL (which is the default).

        If no static_dir was defined (using `add_static`) a default`'/static'`
        URL mounted at ``<root_path>/static'` is added automatically.
        
        """
        host = host or self.settings.SERVER_NAME
        port = port or self.settings.SERVER_PORT
        try:
            port = int(port)
        except (ValueError, TypeError):
            port = None

        debug = bool(debug if debug is not None else
            self.settings.DEBUG)
        reloader = bool(reloader if (reloader is not None) else
            self.settings.RELOADER)
        static_dirs = self.static_dirs

        if not static_dirs:
            static_path = join(self.root_path, STATIC_DIR)
            static_dirs['/static'] = static_path

        self.print_welcome_msg()
        self.print_help_msg(host, port)

        return run_simple(host, port, self,
            use_reloader=reloader,
            use_debugger=debug,
            reloader_interval=reloader_interval,
            threaded=threaded,
            processes=processes,
            ssl_context=ssl_context,
            static_files=static_dirs,
            **kwargs)
    
    def test_client(self, **kwargs):
        """Creates a test client which you can use to send virtual requests
        to the application.
        For general information refer to `werkzeug.test.Client`.

        """
        from werkzeug.test import Client
        if self.settings.SERVER_NAME in '127.0.0.1':
            self.settings.SERVER_NAME = 'localhost'
        kwargs.setdefault('use_cookies', True)
        return Client(self, self.response_class, **kwargs)
    
    def __call__(self, environ, start_response):
        """Shortcut for `wsgi_app`.

        """
        return self.wsgi_app(environ, start_response)


def set_env(env):
    """Set the working environment to `env` saving it in `.SHAKE_ENV`.
    `env` is the name of the new environment eg: 'development', 'production',
    'testing', etc.

    You use environments to load different settings for development,
    production, testing, etc.

    """
    with io.open(ENV_FILE, 'wt') as f:
        f.write(to_unicode(env))
    os.environ[ENV_NAME] = env
    return env


def get_env(default=DEFAULT_ENV):
    """Read the current working environment from `.SHAKE_ENV` or from the
    environment variable `SHAKE_ENV` .

    You use environments to load different settings for development,
    production, testing, etc.

    """
    env = None
    try:
        with io.open(ENV_FILE, 'rt') as f:
            env = f.read()
    except IOError:
        pass
    return env or os.environ.get(ENV_NAME) or default


def env_is(env):
    """Check if the current working environment is the same as `env`.

    You use environments to load different settings for development,
    production, testing, etc.
    Example:

        if shake.env_is('production'):
            import production as settings
        else:
            import development as settings

    """
    return get_env() == env


manager = Manager()

