# -*- coding: utf-8 -*-
"""
    Shake.controllers
    --------------------------

    Generic controllers

"""
from random import choice

from .helpers import local, NotFound, safe_join, send_file
from .views import default_render


__all__ = (
    'not_found_page', 'error_page', 'not_allowed_page', 'render_view',
)


def not_found_page(request, error):
    """Default "Not Found" page.

    """
    rules = local.urls.map._rules
    return default_render('error_notfound.html', locals())


def error_page(request, error):
    """A generic error page.

    """
    return default_render('error.html')


def not_allowed_page(request, error):
    """A default "access denied" page.

    """
    return default_render('error_notallowed.html')


def render_view(request, render, view, context=None, **kwargs):
    """A really simple controller who render directly a view.
    
    render
    :   the renderer to use.
    view
    :   the view to render.
    context
    :   values to add to the view context.

    """
    return render(view, context, **kwargs)


def send_from_directory(request, directory, filename, **options):
    """Send a file from a given directory with `send_file`.  This
    is a secure way to quickly expose static files from an upload folder
    or something similar.

    Example usage:

        @app.route('/uploads/<path:filename>')
        def download_file(filename):
            return send_from_directory(UPLOAD_FOLDER, filename,
                as_attachment=True)

    It is strongly recommended to activate either `X-Sendfile` support in
    your webserver or (if no authentication happens) to tell the webserver
    to serve files for the given path on its own without calling into the
    web application for improved performance.
    
    directory
    :   the directory where all the files are stored.
    filename
    :   the filepath relative to that directory to download.
    options
    :   optional keyword arguments that are directly forwarded to `send_file`.
    
    --------------------------------
    Copied almost unchanged from Flask <http://flask.pocoo.org/>
    Copyright © 2010 by Armin Ronacher.
    Used under the modified BSD license.
    """
    filepath = safe_join(directory, filename)
    if not os.path.isfile(filepath):
        raise NotFound
    return send_file(request, filepath, conditional=True, **options)

