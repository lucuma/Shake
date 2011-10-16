# -*- coding: utf-8 -*-
"""
    # shake.helpers
    
    
    --------
    Copyright © 2010-2011 by Lúcuma labs (http://lucumalabs.com).
    
    MIT License. (http://www.opensource.org/licenses/mit-license.php)

"""
# Get the fastest json available
try:
    import simplejson as json
except ImportError:
    try:
        import json
    except ImportError:
        raise ImportError('Unable to find a json implementation')

import os
from werkzeug.local import Local

from .routes import BuildError


local = Local()


def url_for(endpoint, method=None, external=False, **values):
    """Generates a URL to the given endpoint with the method provided.
    
    :param endpoint: the endpoint of the URL (name of the function)
    :param _external: if set to `True`, an absolute URL is generated.
    :param values: the variable arguments of the URL rule
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
    return url


def execute(cmd, args=None):
    """Simple wrapper for executing commands.
    
    :param cmd: command to execute
    :param args: sequence or a basestring, a basestring will be
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


def url_join(path, *args):
    url = '/'.join([path.rstrip('/')] + list(args))
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

