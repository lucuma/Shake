# -*- coding: utf-8 -*-
"""
# shake.helpers

"""
import io
import mimetypes
import os
import sys
from time import time
from zlib import adler32

# Get the fastest json available
try:
    import simplejson as json
except ImportError:
    try:
        import json
    except ImportError:
        try:
            from django.utils import simplejson as json
        except ImportError:
            raise ImportError('Unable to find a JSON implementation')

from werkzeug.datastructures import Headers
from werkzeug.local import Local, LocalProxy
from werkzeug.urls import url_quote
from werkzeug.wsgi import wrap_file

from .routes import BuildError


local = Local()


def url_for(endpoint, anchor=None, method=None, external=False, **values):
    """Generates a URL to the given endpoint with the method provided.
    
    param endpoint:
        The endpoint of the URL (name of the function).
    
    param anchor:
        If provided this is added as anchor to the URL.
    
    param method:
        If provided this explicitly specifies an HTTP method.
    
    param external:
        Set to `True`, to generate an absolute URL.

    param values:
        The variable arguments of the URL rule
    """
    try:
        urls = local.urls
    except AttributeError:
        raise RuntimeError("You must call this function only from"
            " inside a controller or a view")
    try:
        url = urls.build(endpoint, values, method=method,
            force_external=external)
    except BuildError:
        url = ''
    
    if anchor is not None:
        url += '#' + url_quote(anchor)
    return url


def execute(cmd, args=None):
    """Simple wrapper for executing commands.
    
    param cmd: Command to execute
    param args: Sequence or a basestring, a basestring will be
        executed with shell=True.
    """
    from subprocess import Popen, PIPE
    
    args = args or []
    if isinstance(args, basestring):
        args = '%s %s' % (cmd, args)
        shell = True
    else:
        args.insert(0, cmd)
        shell = False
    proc = Popen(args, shell=shell, stderr=PIPE, stdout=PIPE)
    retcode = proc.wait()
    if retcode != 0:
        raise Exception(proc.stderr.read())
    return proc.stdout.read()


def path_join(base_path, *paths):
    base_path = os.path.normpath(os.path.dirname(os.path.realpath(base_path)))
    return os.path.join(base_path, *paths)


def url_join(base_path, *paths):
    url = '/'.join([base_path.rstrip('/')] + list(paths))
    url = os.path.normpath(url)
    return url.replace("\\", "/")


ALPHABET36 = '0123456789abcdefghijklmnopqrstuvwxyz'

ALPHABET64 = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ=_'

ALPHABET64_REVERSE = {
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
    '9': 9, 'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15, 'g': 16,
    'h': 17, 'i': 18, 'j': 19, 'k': 20, 'l': 21, 'm': 22, 'n': 23, 'o': 24,
    'p': 25, 'q': 26, 'r': 27, 's': 28, 't': 29, 'u': 30, 'v': 31, 'w': 32,
    'x': 33, 'y': 34, 'z': 35, 'A': 36, 'B': 37, 'C': 38, 'D': 39, 'E': 40,
    'F': 41, 'G': 42, 'H': 43, 'I': 44, 'J': 45, 'K': 46, 'L': 47, 'M': 48,
    'N': 49, 'O': 50, 'P': 51, 'Q': 52, 'R': 53, 'S': 54, 'T': 55, 'U': 56,
    'V': 57, 'W': 58, 'X': 59, 'Y': 60, 'Z': 61, '=': 62, '_': 63,
    }


def to64(num, alphabet=None):
    """Converts an integer to base 64 number.
    """
    assert isinstance(num, (int, long)) and (num >= 0), \
        'Must supply a positive integer'
    
    if alphabet:
        assert isinstance(alphabet, (str, unicode)) and len(alphabet) == 64, \
            'The alphabet must be a 64 chars ASCII string'
    
    alphabet = alphabet or ALPHABET64
    converted = []
    while num != 0:
        num, rem = divmod(num, 64)
        converted.insert(0, alphabet[rem])
    return ''.join(converted) or '0'


def from64(snum, alphabet=None):
    """Converts a base-64 number to an integer.
    """
    if alphabet:
        assert isinstance(alphabet, (str, unicode)) and len(alphabet) == 64, \
            'The alphabet must be a 64 chars ASCII string'
        
        alphabet_reverse = dict((char, i) for (i, char) in enumerate(alphabet))
    else:
        alphabet_reverse = ALPHABET64_REVERSE
    num = 0
    snum = str(snum)
    try:
        for char in snum:
            num = num * 64 + alphabet_reverse[char]
    except KeyError:
        raise ValueError('The string is not a valid base 64 encoded integer')
    return num


def to36(num, alphabet=None):
    """Converts an integer to base 36 number.
    """
    assert isinstance(num, (int, long)) and (num >= 0), \
        'Must supply a positive integer'
    
    if alphabet:
        assert isinstance(alphabet, (str, unicode)) and len(alphabet) == 36, \
            'The alphabet must be a 36 chars ASCII string'
    
    alphabet = alphabet or ALPHABET36
    converted = []
    while num != 0:
        num, rem = divmod(num, 36)
        converted.insert(0, alphabet[rem])
    return ''.join(converted) or '0'


def from36(snum, alphabet=None):
    """Converts a base-36 number to an integer.
    """
    if not alphabet:
        return int(snum, 36)
    
    assert isinstance(alphabet, (str, unicode)) and len(alphabet) == 36, \
        'The alphabet must be a 36 chars ASCII string'
    
    alphabet_reverse = dict((char, i) for (i, char) in enumerate(alphabet))
    num = 0
    snum = str(snum)
    try:
        for char in snum:
            num = num * 36 + alphabet_reverse[char]
    except KeyError:
        raise ValueError('The string is not a valid base 36 encoded integer')
    return num


def plural(num, plural='s', singular=''):
    return plural if num != 1 else singular


class StorageDict(dict):
    """A StorageDict object is like a dictionary except `obj.key` can be used
    in addition to `obj['key']`.
    
    Basic Usage:
    
        >>> o = StorageDict(a=1)
        >>> o.a
        1
        >>> o['a']
        1
        >>> o.a = 2
        >>> o['a']
        2
        >>> del o.a
        >>> print o.a
        None
    
    """
    
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError, error:
            raise AttributeError(error)
    
    def __setattr__(self, key, value):
        self[key] = value
    
    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError, error:
            raise AttributeError(error)
    
    def __repr__(self):
        return '<StorageDict ' + dict.__repr__(self) + '>'
    
    def __getstate__(self):
        return dict(self)
    
    def __setstate__(self, value):
        for (key, value) in value.items():
            self[key] = value


def send_file(request, filename_or_fp, mimetype=None, as_attachment=False,
        attachment_filename=None, add_etags=True, cache_timeout=60 * 60 * 12,
        conditional=False, use_x_sendfile=False, response_class=None):
    """Sends the contents of a file to the client.  This will use the
    most efficient method available and configured.  By default it will
    try to use the WSGI server's file_wrapper support.  Alternatively
    you can set the `use_x_sendfile` parameter to `True` to directly emit
    an `X-Sendfile` header.  This however requires support of the underlying
    webserver for `X-Sendfile`.

    By default it will try to guess the mimetype for you, but you can
    also explicitly provide one.  For extra security you probably want
    to send certain files as attachment (HTML for instance).  The mimetype
    guessing requires a `filename` or an `attachment_filename` to be
    provided.

    Please never pass filenames to this function from user sources without
    checking them first.  Something like this is usually sufficient to
    avoid security problems::

        if '..' in filename or filename.startswith('/'):
            raise NotFound()
    
    param request:
        ...
    
    param filename_or_fp: 
        The absolute path of the file to send.
        Alternatively a file object might be provided in which case
        `X-Sendfile` might not work and fall back to the traditional method.
        Make sure that the file pointer is positioned at the start
        of data to send before calling `send_file`.
    
    param mimetype:
        The mimetype of the file if provided, otherwise
        auto detection happens.
    
    param as_attachment:
        Set to `True` if you want to send this file with
        a `Content-Disposition: attachment` header.
    
    param attachment_filename:
        The filename for the attachment if it
        differs from the file's filename.
    
    param add_etags:
        Set to `False` to disable attaching of etags.
    
    param conditional:
        Set to `True` to enable conditional responses.
    
    param cache_timeout:
        The timeout in seconds for the headers.
    
    param use_x_sendfile:
        Set to `True` to directly emit an `X-Sendfile` header.
        This however requires support of the underlying webserver.
    
    param response_class:
        Set to overwrite the default Response class.
    
    --------------------------------
    Copied almost unchanged from Flask <http://flask.pocoo.org/>
    Copyright © 2010 by Armin Ronacher.
    Used under the modified BSD license.
    """
    from .wrappers import Response

    mtime = None
    if isinstance(filename_or_fp, basestring):
        filename = filename_or_fp
        file = None
    else:
        assert bool(mimetype or attachment_filename)
        add_etags = False
        file = filename_or_fp
        filename = getattr(file, 'name', None)
    
    if filename is not None:
        filename = os.path.abspath(filename)
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

    if use_x_sendfile and filename:
        if file is not None:
            file.close()
        headers['X-Sendfile'] = filename
        data = None
    else:
        if file is None:
            file = io.open(filename, 'rb')
            mtime = os.path.getmtime(filename)
        data = wrap_file(request.environ, file)
    
    if response_class is None:
        response_class = Response
    resp = response_class(data, mimetype=mimetype, headers=headers,
        direct_passthrough=True)

    # if we know the file modification date, we can store it as the
    # the time of the last modification.
    if mtime is not None:
        resp.last_modified = int(mtime)

    resp.cache_control.public = True
    if cache_timeout:
        resp.cache_control.max_age = cache_timeout
        resp.expires = int(time() + cache_timeout)

    if add_etags and filename is not None:
        resp.set_etag('flask-%s-%s-%s' % (
            os.path.getmtime(filename),
            os.path.getsize(filename),
            adler32(
                filename.encode('utf8') if isinstance(filename, unicode)
                else filename
            ) & 0xffffffff
        ))
        if conditional:
            resp = resp.make_conditional(request)
            # make sure we don't send x-sendfile for serespers that
            # ignore the 304 status code for x-sendfile.
            if resp.status_code == 304:
                resp.headers.pop('x-sendfile', None)
    return resp


class Settings(object):
    """A helper to manage custom and default settings
    """
    
    def __init__(self, default, custom, case_insensitive=False):
        if isinstance(default, dict):
            default = StorageDict(default)
        if isinstance(custom, dict):
            custom = StorageDict(custom)
        self.__dict__['default'] = default
        self.__dict__['custom'] = custom
        self.__dict__['case_insensitive'] = case_insensitive
    
    def __contains__(self, key):
        return hasattr(self.custom, key)
    
    def __getattr__(self, key):
        if (self.__dict__['case_insensitive']):
            key = key.lower()
        if hasattr(self.__dict__['custom'], key):
            return getattr(self.__dict__['custom'], key)
        elif hasattr(self.__dict__['default'], key):
            return getattr(self.__dict__['default'], key)
        raise AttributeError('No %s was found in the custom nor'
            ' in the default settings' % key)
    
    def __setattr__(self, key, value):
        if (self.case_insensitive):
            key = key.lower()
        setattr(self.custom, key, value)
    
    __getitem__ = __getattr__
    __setitem__ = __setattr__
    
    def get(self, key, default=None):
        if (self.case_insensitive):
            key = key.lower()
        if hasattr(self.custom, key):
            return getattr(self.custom, key)
        return getattr(self.default, key, default)
    
    def setdefault(self, key, value):
        if (self.case_insensitive):
            key = key.lower()
        if hasattr(self.custom, key):
            return getattr(self.custom, key)
        setattr(self.custom, key, value)
        return value
    
    def update(self, dict_):
        custom = self.custom
        ci = self.case_insensitive
        for key, value in dict_.items():
            if ci:
                key = key.lower()
            setattr(custom, key, value)

