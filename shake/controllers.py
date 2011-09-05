# -*- coding: utf-8 -*-
"""
    shake.controllers
    ----------------------------------------------
    
    Generic controllers
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    :func:`send_file` and :func:`from_dir` copied almost unchanged
    from the Flask framework <http://flask.pocoo.org/>
    Copyright (c) 2010 by Armin Ronacher.
    Used under the modified BSD license.
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    :Copyright © 2010-2011 by Lúcuma labs (http://lucumalabs.com).
    :MIT License. (http://www.opensource.org/licenses/mit-license.php)

"""
import mimetypes
import os
from random import choice
from time import time
from werkzeug.datastructures import Headers
from werkzeug.wsgi import wrap_file
from werkzeug.exceptions import NotFound
from zlib import adler32

from .config import QUOTES
from .helpers import local
from .views import default_render


def not_found_page(request, error):
    """Default "Not Found" page.
    """
    rules = local.urls.map._rules
    return default_render('not_found.html', rules=rules)


def error_page(request, error):
    """A generic error page.
    """
    return default_render('error.html')


def not_allowed_page(request, error):
    """A default "access denied" page.
    """
    return default_render('not_allowed.html')


def welcome_page(request, error):
    """A default "welcome to shake" page.
    """
    quote = choice(QUOTES)
    return default_render('welcome.html', quote=quote)


def render_view(request, render, view, **kwargs):
    """A really simple controller who render directly a view.
    
    :param render: The view renderer to use.
    :param kwargs: Values to add to the view context.
    """
    return render(view, **kwargs)


def send_file(request, filename_or_fp, mimetype=None, as_attachment=False,
        attachment_filename=None, add_etags=True, cache_timeout=60 * 60 * 12,
        conditional=False):
    """Sends the contents of a file to the client.  This will use the
    most efficient method available and configured.  By default it will
    try to use the WSGI server's file_wrapper support.  Alternatively
    you can set the application's `USE_X_SENDFILE` setting
    to ``True`` to directly emit an `X-Sendfile` header.  This however
    requires support of the underlying webserver for `X-Sendfile`.
    
    By default it will try to guess the mimetype for you, but you can
    also explicitly provide one.  For extra security you probably want
    to sent certain files as attachment (HTML for instance).  The mimetype
    guessing requires a `filename` or an `attachment_filename` to be
    provided.
    
    :param filename_or_fp:
        the filename of the file to send.  This is relative to the
        :attr:`~Shake.root_path` if a relative path is specified. Alternatively
        a file object might be provided in which case `X-Sendfile` might not
        work and fall back to the traditional method.
    
    :param mimetype:
        the mimetype of the file if provided, otherwise auto detection happens.
    
    :param as_attachment:
        set to `True` if you want to send this file with a
        ``Content-Disposition: attachment`` header.
    
    :param attachment_filename:
        the filename for the attachment if it differs from the file's filename.
    
    :param add_etags:
        set to `False` to disable attaching of etags.
    
    :param conditional:
        set to `True` to enable conditional responses.
    
    :param cache_timeout:
        the timeout in seconds for the headers.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Copied almost unchanged from Flask <http://flask.pocoo.org/>
    Copyright (c) 2010 by Armin Ronacher.
    Used under the modified BSD license.
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """
    mtime = None
    if isinstance(filename_or_fp, basestring):
        filename = filename_or_fp
        if '..' in filename or filename.startswith('/'):
            raise NotFound()
        filep = None
    else:
        filep = filename_or_fp
        filename = getattr(filep, 'name', None)
    
    if filename is not None:
        assert os.path.isabs(filename)
    if mimetype is None and (filename or attachment_filename):
        mimetype = mimetypes.guess_type(filename or attachment_filename)[0]
    if mimetype is None:
        mimetype = 'application/octet-stream'
    
    headers = Headers()
    if as_attachment:
        if attachment_filename is None:
            if filename is None:
                raise TypeError('filename unavailable, required for '
                    'sending as attachment')
            attachment_filename = os.path.basename(filename)
        headers.add('Content-Disposition', 'attachment',
            filename=attachment_filename)
    
    if local.app.settings.get('USE_X_SENDFILE') and filename:
        if filep is not None:
            filep.close()
        headers['X-Sendfile'] = filename
        data = None
    else:
        if filep is None:
            filep = open(filename, 'rb')
            mtime = os.path.getmtime(filename)
        data = wrap_file(request.environ, filep)
    
    response = local.app.response_class(data, mimetype=mimetype,
        headers=headers, direct_passthrough=True)
    
    # if we know the file modification date, we can store it as the
    # current time to better support conditional requests.  Werkzeug
    # as of 0.6.1 will override this value however in the conditional
    # response with the current time.  This will be fixed in Werkzeug
    # with a new release, however many WSGI servers will still emit
    # a separate date header.
    if mtime is not None:
        response.date = int(mtime)
    
    response.cache_control.public = True
    if cache_timeout:
        response.cache_control.max_age = cache_timeout
        response.expires = int(time() + cache_timeout)
    
    if add_etags and filename is not None:
        response.set_etag('shake-%s-%s-%s' % (
            os.path.getmtime(filename),
            os.path.getsize(filename),
            adler32(filename) & 0xffffffff,
        ))
        if conditional:
            response = response.make_conditional(request)
            # make sure we don't send x-sendfile for servers that
            # ignore the 304 status code for x-sendfile.
            if response.status_code == 304:
                response.headers.pop('x-sendfile', None)
    return response


def from_dir(request, path, filename, **options):
    """Send a file from a given directory with :func:`send_file`.  This
    is a secure way to quickly expose static files from an upload directory
    or something similar.
    
    Example usage::
        
        def download_file(request, filename):
            return from_dir(
                request,
                app.settings.UPLOAD_FOLDER,
                filename,
                as_attachment=True
                )
    
    .. admonition:: Sending files and Performance
       
       It is strongly recommended to activate either `X-Sendfile` support in
       your web server or (if no authentication happens) to tell the web server
       to serve files for the given path on its own without calling into the
       web application for improved performance.

    
    :param directory:
        the directory where all the files are stored.
    
    :param filename:
        the filename relative to that directory to download.
    
    :param options:
        optional keyword arguments that are directly forwarded
        to :func:`send_file`.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Copied almost unchanged from Flask <http://flask.pocoo.org/>
    Copyright (c) 2010 by Armin Ronacher.
    Used under the modified BSD license.
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """
    filename = os.path.normpath(filename)
    if filename.startswith(('/', '../')):
        raise NotFound()
    filename = os.path.join(path, filename)
    if not os.path.isfile(filename):
        raise NotFound()
    return send_file(request, filename, conditional=True, **options)


def check_if_exist(request, model, column_name):
    """A controller that check if a row in a model already exists
    (eg. a username). This function is intended to be called using AJAX.
    
    :param model:
        model classname.
    
    :param column_name:
        The name of a both the model column that contains the unique field
        and the GET variable containing the data to be checked.
    
    """
    get_data = request.form.get(column_name)
    if get_data is None:
        return ''
    attr = getattr(model, column_name)
    data = model.query.filter(attr == get_data).first()
    if data is None:
        return ''
    return '1'
