# -*- coding: utf-8 -*-
"""
    # Shake.app

    This module implements the central WSGI application object.

"""
from datetime import datetime, timedelta
import os
import sys

from werkzeug.exceptions import HTTPException, BadRequestKeyError
from werkzeug.local import LocalManager
from werkzeug.serving import run_simple
from werkzeug.utils import import_string

from .config import ShakeSettings
from .routes import Map, Rule
from .helpers import local
from .serializers import to_json
from .wrappers import Request, Response


local_manager = LocalManager([local])
SECRET_KEY_MINLEN = 20
STATIC_DIR = 'static'

WELCOME_MESSAGE = "Welcome aboard. You're now using Shake!"


class Shake(object):
    """Implements a WSGI application and acts as the central
    object.
    
    :param url_map: Sequence of url rules.
    
    :param settings: A module or dict with the custom settings.
    
    Usually you create a :class:Shake instance in your main module or
    in the `__init__.py` file of your package like this::
        
        from shake import Shake
        app = Shake(urls, settings)
    
    For a small application, you can also do:
        
        app = Shake()
        ...
        app.add_url_rule(...)
        ...
        app.settings.FOO = 'bar'
    
    """
    
    # The class that is used for request objects.
    request_class = Request
    
    # The class that is used for response objects.
    response_class = Response
    
    def __init__(self, *args):
        url_map = []
        settings = {}
        largs = len(args)
        if largs == 1:
            settings = args[0]
            if isinstance(args[0], (list, tuple, Map)):
                url_map = args[0]
                settings = {}
        elif largs > 1:
            url_map = args[0]
            settings = args[1]
        local.app = self
        
        # Functions to run before each request and response
        self.before_request_funcs = []
        # Functions to run before each response
        self.before_response_funcs = []
        # Functions to run if an exception occurs
        self.on_exception_funcs = []
        
        # Registered database objects
        self.databases = []
        
        # A dict of static url:path to be used during development.
        # If not empty, it'll be passed to a
        # `werkzeug.wsgi.SharedDataMiddleware` instance.
        self.static_dirs = {}
        
        settings = ShakeSettings(settings)
        self.settings = settings
        if not isinstance(url_map, Map):
            url_map = Map(url_map,
                default_subdomain=settings.DEFAULT_SUBDOMAIN)
        self.url_map = url_map
        
        self.error_handlers = {
            403: settings.PAGE_NOT_ALLOWED,
            404: settings.PAGE_NOT_FOUND,
            500: settings.PAGE_ERROR,
            }
        
        self.request_class.max_content_length = settings.MAX_CONTENT_LENGTH
        self.request_class.max_form_memory_size = settings.MAX_FORM_MEMORY_SIZE
        
        self.assert_secret_key()
        self.session_expires = timedelta(hours=settings.SESSION_EXPIRES)
    
    def assert_secret_key(self):
        key = self.settings.SECRET_KEY
        if key and len(key) < SECRET_KEY_MINLEN:
            raise RuntimeError("Your 'SECRET_KEY' setting is too short to be"
                " safe.  Make sure is *at least* %i chars long."
                % SECRET_KEY_MINLEN)
    
    def route(self, url, *args, **kwargs):
        """Decorator for mounting a function in a URL route.
        """
        def real_decorator(target):
            self.url_map.add(Rule(url, target, *args, **kwargs))
            return target
        return real_decorator
    
    def add_url(self, rule, *args, **kwargs):
        self.url_map.add(Rule(rule, *args, **kwargs))
    
    def add_urls(self, urls):
        for url in urls:
            self.url_map.add(url)
    
    def add_static(self, url, path):
        url = '/' + url.strip('/')
        path = os.path.normpath(os.path.realpath(path))
        # Instead of a path, we've probably recieved the value of __file__
        if os.path.isfile(path):
            path = os.path.join(os.path.dirname(path), STATIC_DIR)
        self.static_dirs[url] = path
    
    def before_request(self, function):
        """Register a function to run before each request.
        Can be used as a decorator."""
        if function not in self.before_request_funcs:
            self.before_request_funcs.append(function)
        return function
    
    def before_response(self, function):
        """Register a function to be run before each response.
        Can be used as a decorator."""
        if function not in self.before_response_funcs:
            self.before_response_funcs.append(function)
        return function
    
    def on_exception(self, function):
        """Register a function to be run if an exception
        occurs."""
        if function not in self.on_exception_funcs:
            self.on_exception_funcs.append(function)
        return function
    
    def preprocess_request(self, request):
        for handler in self.before_request_funcs:
            resp_value = handler(request)
            if resp_value is not None:
                return resp_value
    
    def process_response(self, response):
        for handler in self.before_response_funcs:
            response = handler(response)
        return response
    
    def save_session(self, session, response):
        """Saves the session if it needs updates.  For the default
        implementation, check :meth:`Request.session`.
        
        :param session: the session to be saved (a :class:`~SecureCookie`
            object)
        :param response: an instance of :attr:`response_class`
        """
        if session.should_save:
            expires = datetime.utcnow() + self.session_expires
            session_data = session.serialize()
            response.set_cookie(self.settings.SESSION_COOKIE_NAME,
                session_data, httponly=True, expires=expires)
    
    def wsgi_app(self, environ, start_response):
        """The actual WSGI application.  This is not implemented in
        `__call__` so that middlewares can be applied without losing a
        reference to the class.  So instead of doing this::
            
            app = MyMiddleware(app)
        
        It's a better idea to do this instead::
            
            app.wsgi_app = MyMiddleware(app.wsgi_app)
        
        Then you still have the original application object around and
        can continue to call methods on it.
        
        :param environ:
            a WSGI environment
        
        :param start_response: a callable accepting a status code,
            a list of headers and an optional exception context to start
            the response.
        """
        self.force_script_name(environ)
        
        request = self.request_class(environ)
        local.request = request  # ##
        
        try:
            endpoint, kwargs = self.match_url(request, environ)
            
            resp_value = self.preprocess_request(request)
            if resp_value is None:
                resp_value = endpoint(request, **kwargs)
            response = self.make_response(resp_value, environ)
            self.save_session(request.session, response)
            response = self.process_response(response)
        
        except (HTTPException), error:
            code = error.code
            # If less than 400 is not an error
            if code < 400:
                return error(environ, start_response)
            
            for handler in self.on_exception_funcs:
                handler(error)
            
            endpoint = None
            endpoint = self.error_handlers.get(code)
            if endpoint is None:
                if self.settings.DEBUG:
                    if isinstance(error, BadRequestKeyError):
                        reraise(error)
                    return error(environ, start_response)
                # In production try to use the default error handler
                endpoint = self.error_handlers.get(500)
            
            if isinstance(endpoint, basestring):
                endpoint = import_string(endpoint)
            resp_value = endpoint(request, error)
            response = self.make_response(resp_value, environ)
            response.status_code = code
        
        except (Exception), error:
            for handler in self.on_exception_funcs:
                handler(error)
            endpoint = self.error_handlers.get(500)
            if endpoint is None or self.settings.DEBUG:
                reraise(error)
            
            if isinstance(endpoint, basestring):
                endpoint = import_string(endpoint)
            resp_value = endpoint(request, error)
            response = self.make_response(resp_value, environ)
            response.status_code = 500
        
        finally:
            local_manager.cleanup()
        
        return response(environ, start_response)
    
    def force_script_name(self, environ):
        script_name = environ.get('SCRIPT_NAME')
        new_script_name = self.settings.FORCE_SCRIPT_NAME
        
        if (new_script_name != False) and script_name:
            environ['SCRIPT_NAME'] = new_script_name
            redirect_uri = environ.get('REDIRECT_URI')
            
            if redirect_uri:
                environ['REDIRECT_URI'] = redirect_uri.replace(
                    script_name, new_script_name)
    
    def match_url(self, request, environ):
        local.urls = urls = self.url_map.bind_to_environ(environ)  # ##
        
        rule, kwargs = urls.match(return_rule=True)
        endpoint = rule.endpoint
        if isinstance(endpoint, basestring):
            endpoint = import_string(endpoint)
        
        request.url_rule = rule
        request.endpoint = endpoint
        request.kwargs = kwargs
        return endpoint, kwargs
    
    def make_response(self, resp_value, environ):
        """Converts the return value from a view function to a real
        response object that is an instance of :attr:`response_class`.
        
        The following types are allowed for `resp_value`:
            
            :attr:`response_class`: the object is returned unchanged.
            
            :class:`str`: a response object is created with the string as body.
            
            :class:`unicode`: a response object is created with the string
                encoded to utf-8 as body.
            
            :class:`dict`: creates a response object with the JSON
                representation of the dictionary and the mimetype of
                `application/json`. This can be very useful when making
                client-intensive web apps.
            
            :class:`None`: an empty response object is created.
            
            a WSGI function: the function is called as WSGI application
                and buffered as response object.
        
        :param resp_value:
            the return value from the view function
        
        :return: an instance of :attr:`response_class`
        
        """
        if isinstance(resp_value, self.response_class):
            return resp_value
        if isinstance(resp_value, basestring):
            return self.response_class(resp_value)
        if isinstance(resp_value, dict):
            return self.response_class(
                to_json(resp_value, indent=None),
                mimetype='application/json')
        if resp_value is None:
            return self.response_class('')
        return self.response_class.force_type(resp_value, environ)
    
    def _welcome_msg(self):
        """Prints a welcome message, if you run an application
        without URLs."""
        if os.environ.get('WERKZEUG_RUN_MAIN') != 'true' \
                and len(self.url_map._rules) == 0:
            wml = len(WELCOME_MESSAGE) + 2
            print '\n '.join(['',
                '-' * wml,
                ' %s ' % WELCOME_MESSAGE,
                '-' * wml,
                ''])
    
    def run(self, host=None, port=None, debug=None, reloader=None, 
            threaded=True, processes=1, reloader_interval=2,
            ssl_context=None, **kwargs):
        """Runs the application on a local development server.
        
        The development server is not intended to be used on production
        systems. It was designed especially for development purposes and
        performs poorly under high load.
        
        :param host:
            The host for the application. eg: 'localhost'.
        
        :param port:
            The port for the server. eg: 8080
        
        :param debug:
            Run in debug mode? The default is the value of settings.DEBUG.
        
        :param threaded:
            Should the process handle each request in a separate thread?
            Default `false`.
        
        :param processes:
            Number of processes to spawn. Default `1`.
        
        :param reloader_interval:
            The interval for the reloader in seconds. Default `2`.
        
        :param ssl_context:
            An SSL context for the connection. Either an OpenSSL context, the
            string 'adhoc' if the server should automatically create one, or
            `None` to disable SSL (which is the default).
        
        """
        host = host or self.settings.SERVER_NAME
        port = port or self.settings.SERVER_PORT
        debug = bool(debug if (debug is not None) else
            self.settings.get('DEBUG', True))
        reloader = bool(reloader if (reloader is not None) else
            self.settings.get('RELOAD', True))
        
        self._welcome_msg()
        
        return run_simple(host, port, self,
            use_reloader=reloader,
            use_debugger=debug,
            reloader_interval=reloader_interval,
            threaded=threaded,
            processes=processes,
            ssl_context=ssl_context,
            static_files=self.static_dirs,
            **kwargs)
    
    def test_client(self):
        """Creates a test client for this application.
        """
        from werkzeug.test import Client
        if self.settings.SERVER_NAME == '127.0.0.1':
            self.settings.SERVER_NAME = 'localhost'
        return Client(self, self.response_class, use_cookies=True)
    
    def __call__(self, environ, start_response):
        local.app = self
        return self.wsgi_app(environ, start_response)


def reraise(exception):
    """Re-raise an exception.
    """
    # Re-raise and remove ourselves from the stack trace.
    raise exception, None, sys.exc_info()[-1]

