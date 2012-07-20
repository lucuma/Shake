# -*- coding: utf-8 -*-
"""
    Shake.helpers
    --------------------------

"""
import datetime
from decimal import Decimal
import io
import mimetypes
import os
import posixpath
import sys
import types
from time import time
from zlib import adler32

from werkzeug.datastructures import Headers
from werkzeug.exceptions import NotFound
from werkzeug.local import Local, LocalProxy
from werkzeug.urls import url_quote
from werkzeug.wsgi import wrap_file

from .routes import BuildError


__all__ = (
    'local', 'Local', 'LocalProxy', 'url_for',
    'path_join', 'url_join', 'to64', 'from64', 'to36', 'from36',
    'StorageDict', 'safe_join', 'send_file', 'to_unicode', 'to_bytestring',
)

local = Local()


def url_for(endpoint, anchor=None, method=None, external=False, **values):
    """Generates a URL to the given endpoint with the method provided.
    
    endpoint
    :   The endpoint of the URL (name of the function).
    anchor
    :   If provided this is added as anchor to the URL.
    method
    :   If provided this explicitly specifies an HTTP method.
    external
    :   Set to `True`, to generate an absolute URL.
    values
    :   The variable arguments of the URL rule

    """
    try:
        urls = local.urls
    except AttributeError:
        raise RuntimeError("You must call this function only from"
            " inside a view or a template")
    try:
        url = urls.build(endpoint, values, method=method,
            force_external=external)
    except BuildError:
        url = ''
    
    if anchor is not None:
        url += '#' + url_quote(anchor)
    return url


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


class StorageDict(dict):
    """A StorageDict object is like a dictionary except than
       `obj.key` can be used in addition to `obj['key']`.
    
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


def safe_join(directory, filename):
    """Safely join `directory` and `filename`.

    Example usage:

        def wiki_page(request, filename):
            filepath = safe_join(WIKI_FOLDER, filename)
            with open(filepath, 'rb') as fd:
                content = fd.read() # Read and process the file content.
            return content

    param directory:
        the base directory.
    
    param filename:
        the untrusted filename relative to that directory.
    
    raises:
        `NotFound` if the resulting path would fall out of `directory`.
    """
    filename = posixpath.normpath(filename)
    if os.path.isabs(filename):
        raise NotFound
    return os.path.join(directory, filename)


def send_file(request, filepath_or_fp, mimetype=None, as_attachment=False,
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
    
    param filepath_or_fp: 
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
    if isinstance(filepath_or_fp, basestring):
        filepath = filepath_or_fp
        file = None
    else:
        assert bool(mimetype or attachment_filename)
        add_etags = False
        file = filepath_or_fp
        filepath = getattr(file, 'name', None)
    
    if filepath is not None:
        filepath = os.path.abspath(filepath)
    if mimetype is None and (filepath or attachment_filename):
        mimetype = mimetypes.guess_type(filepath or attachment_filename)[0]
    if mimetype is None:
        mimetype = 'application/octet-stream'

    headers = Headers()
    if as_attachment:
        if attachment_filename is None:
            if filepath is None:
                raise TypeError('filename unavailable, required for '
                    'sending as attachment')
            attachment_filename = os.path.basename(filepath)
        headers.add('Content-Disposition', 'attachment',
            filename=attachment_filename)

    if use_x_sendfile and filepath:
        if file is not None:
            file.close()
        headers['X-Sendfile'] = filepath
        data = None
    else:
        if file is None:
            file = io.open(filepath, 'rb')
            mtime = os.path.getmtime(filepath)
        data = wrap_file(request.environ, file)
    
    response_class = response_class or Response
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

    if add_etags and filepath is not None:
        resp.set_etag('shake-%s-%s-%s' % (
            os.path.getmtime(filepath),
            os.path.getsize(filepath),
            adler32(
                filepath.encode('utf8') if isinstance(filepath, unicode)
                else filepath
            ) & 0xffffffff
        ))
        if conditional:
            resp = resp.make_conditional(request)
            # make sure we don't send x-sendfile for serespers that
            # ignore the 304 status code for x-sendfile.
            if resp.status_code == 304:
                resp.headers.pop('x-sendfile', None)
    return resp


def is_protected_type(obj):
    """Determine if the object instance is of a protected type.

    Objects of protected types are preserved as-is when passed to
    force_unicode(strings_only=True).
    """
    return isinstance(obj, (
        types.NoneType,
        int, long,
        datetime.datetime, datetime.date, datetime.time,
        float, Decimal)
    )


def to_unicode(s, encoding='utf-8', strings_only=False, errors='strict'):
    """Returns a unicode object representing 's'. Treats bytestrings using the
    `encoding` codec.

    If strings_only is True, don't convert (some) non-string-like objects.

    --------------------------------
    Copied almost unchanged from Django <https://www.djangoproject.com/>
    Copyright © Django Software Foundation and individual contributors.
    Used under the modified BSD license.
    """
    # Handle the common case first, saves 30-40% in performance when s
    # is an instance of unicode.
    if isinstance(s, unicode):
        return s
    if strings_only and is_protected_type(s):
        return s
    encoding = encoding or 'utf-8'
    try:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                try:
                    s = unicode(str(s), encoding, errors)
                except UnicodeEncodeError:
                    if not isinstance(s, Exception):
                        raise
                    # If we get to here, the caller has passed in an Exception
                    # subclass populated with non-ASCII data without special
                    # handling to display as a string. We need to handle this
                    # without raising a further exception. We do an
                    # approximation to what the Exception's standard str()
                    # output should be.
                    s = u' '.join([to_unicode(arg, encoding, strings_only,
                        errors) for arg in s])
        elif not isinstance(s, unicode):
            # Note: We use .decode() here, instead of unicode(s, encoding,
            # errors), so that if s is a SafeString, it ends up being a
            # SafeUnicode at the end.
            s = s.decode(encoding, errors)
    except UnicodeDecodeError, e:
        if not isinstance(s, Exception):
            raise UnicodeDecodeError(s, *e.args)
        else:
            # If we get to here, the caller has passed in an Exception
            # subclass populated with non-ASCII bytestring data without a
            # working unicode method. Try to handle this without raising a
            # further exception by individually forcing the exception args
            # to unicode.
            s = u' '.join([to_unicode(arg, encoding, strings_only,
                errors) for arg in s])
    return s


def to_bytestring(s, encoding='utf-8', strings_only=False, errors='strict'):
    """Returns a bytestring version of 's', encoded as specified in 'encoding'.

    If strings_only is True, don't convert (some) non-string-like objects.

    --------------------------------
    Copied almost unchanged from Django <https://www.djangoproject.com/>
    Copyright © Django Software Foundation and individual contributors.
    Used under the modified BSD license.
    """
    if strings_only and isinstance(s, (types.NoneType, int)):
        return s
    encoding = encoding or 'utf-8'
    if not isinstance(s, basestring):
        try:
            return str(s)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                # An Exception subclass containing non-ASCII data that doesn't
                # know how to print itself properly. We shouldn't raise a
                # further exception.
                return ' '.join([to_bytestring(arg, encoding, strings_only,
                    errors) for arg in s])
            return unicode(s).encode(encoding, errors)
    elif isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s

