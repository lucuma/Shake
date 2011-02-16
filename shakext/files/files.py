# -*- coding: utf-8 -*-
"""

"""
import datetime
import os
import random
import re
import uuid

import sqlalchemy.types as types
from werkzeug.exceptions import RequestEntityTooLarge, UnsupportedMediaType
from werkzeug.utils import secure_filename


IMAGES = ('jpg', 'jpeg', 'png', 'gif', 'svg', 'bmp')

AUDIO = ('wav', 'mp3', 'aac', 'ogg', 'oga', 'flac')

DOCUMENTS = ('pdf', 'rtf', 'txt',
    'odf', 'odp', 'ods', 'odg', 'ott', 'otp', 'ots', 'otg',
    'pages', 'key', 'numbers', 'gnumeric', 'abw',
    'doc', 'ppt', 'xls', 'vsd', 'docx', 'pptx', 'xlsx', 'vsx',
    )

DATA = ('csv', 'json', 'xml', 'ini', 'plist', 'yaml', 'yml')

ARCHIVES = ('zip', 'gz', 'bz2', 'tar', 'tgz', 'txz', '7z')

DEFAULT = IMAGES + AUDIO + DOCUMENTS


class FileObj(object):
    """
    """

    def __init__(self, data, root_path):
        data = data or {}
        self.name = data.get('name', u'')
        self.size = data.get('size', u'')
        self.type = data.get('type', u'')
        self._path = data.get('path')
        self.root_path = root_path
        self.is_image = self.type.startswith('image/')

    def __nonzero__(self):
        return self._path is not None

    def __repr__(self):
        return '<FileObj %s "%s">' % (self.type, self.name)

    @property
    def path(self):
        if self._path is None:
            return u''
        return os.path.join(self.root_path, self._path, self.name)

    @property
    def url(self):
        if self._path is None:
            return u''
        lst_url = [self._path, self.name]
        return '/'.join(lst_url)

    def get_thumb_path(self, tname):
        if self._path is None:
            return u''
        return os.path.join(self.root_path, self._path, tname, self.name)

    def get_thumb_url(self, tname):
        if self._path is None:
            return u''
        lst_url = [self._path, tname, self.name]
        return '/'.join(lst_url)

    def remove(self, *thumb_names):
        try:
            os.remove(self.path)
        except OSError:
            pass
        for tname in thumb_names:
            try:
                os.remove(self.get_thumb_path(tname))
            except OSError:
                pass


class FileStorage(object):

    def __init__(self, root_path, upload_to='{yyyy}/{mm}/{dd}/', secret=False,
            allowed=DEFAULT, denied=None):
        """
        :param root_path:

        :param upload_to:
            Un patrón de ruta como los usados en `format_path`.

        :param secret:
            Si es True, en vez del nombre de archivo original se usa uno al
            azar.

        :param allowed:
            Lista de extensiones permitidas. `None` para cualquiera.
            Si el archivo no tiene una de estas extensiones se lanza
            un error :class:`werkzeug.exceptions.UnsupportedMediaType`

        :param denied:
            Lista de extensiones prohibidas. `None` para ninguna.
            Si el archivo tiene una de estas extensiones se lanza
            un error :class:`werkzeug.exceptions.UnsupportedMediaType`

        """
        self.root_path = root_path
        self.upload_to = upload_to
        self.secret = secret
        self.allowed = allowed
        self.denied = denied

    def __repr__(self):
        return '<FileStorage "%s" secret=%s>' % (self.upload_to, self.secret)

    def save(self, filesto, prefix=''):
        """
        :param:filesto::
            Un objeto werkzeug.FileStorage.

        :param prefix:
            Para evitar race-conditions entre varios usuarios subiendo archivos
            llamados igual al mismo tiempo. No se usa si `secret` es True.

        """
        original_filename = filesto.filename
        tmplpath = self.upload_to
        if callable(tmplpath):
            tmplpath = tmplpath(original_filename)
        filepath = format_path(tmplpath, original_filename)

        name, ext = original_filename.rsplit('.', 1)
        self.check_file_extension(ext)

        if self.secret:
            name = None
        else:
            name = prefix + name

        filename = get_unique_filename(self.root_path, filepath,
            name=name, ext=ext)
        fullpath = os.path.join(self.root_path, filepath)
        fullpath = os.path.abspath(fullpath)
        try:
            os.makedirs(fullpath)
        except OSError:
            pass
        fullpath = os.path.join(fullpath, filename)
        filesto.save(fullpath)
        filesize = os.path.getsize(fullpath)
        data = {
            'name': filename,
            'path': filepath,
            'size': filesize,
            'ftype': filesto.content_type,
            'fullpath': fullpath,
        }
        return data

    def check_file_extension(self, ext):
        if self.allowed and not ext in self.allowed:
            raise UnsupportedMediaType()
        if self.denied and ext in self.denied:
            raise UnsupportedMediaType()


class FileType(types.TypeDecorator):
    """
    """

    impl = types.PickleType

    def __init__(self, root_path, upload_to='{yyyy}/{mm}/{dd}/', secret=False,
      allowed=DEFAULT, denied=None, storage=None):
        """
        :param root_path:

        :param upload_to:
            Un patrón de ruta como los usados en `format_path`.

        :param secret:
            Si es True, en vez del nombre de archivo original se usa uno
            al azar.

        :param allowed:
            Lista de extensiones permitidas. `None` para cualquiera.
            Si el archivo no tiene una de estas extensiones se lanza
            un error :class:`werkzeug.exceptions.UnsupportedMediaType`

        :param denied:
            Lista de extensiones prohibidas. `None` para ninguna.
            Si el archivo tiene una de estas extensiones se lanza
            un error :class:`werkzeug.exceptions.UnsupportedMediaType`

        """
        self.root_path = root_path
        self.upload_to = upload_to
        if storage is None:
            storage = FileStorage(root_path, upload_to, secret, allowed,
                denied)
        self.storage = storage

        types.TypeDecorator.__init__(self, mutable=False)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        data = self.storage.save(value)
        return data

    def process_result_value(self, value, dialect):
        return FileObj(value, self.root_path)

    def copy(self):
        return FileType(self.root_path, self.upload_to, storage=self.storage)


def upload_file(filesto, root_path, upload_to='{yyyy}/{mm}/{dd}/',
      secret=False, allowed=DEFAULT, denied=None, prefix=''):
    """
    :param filesto:
        Un objeto werkzeug.FileStorage.

    :param root_path:

    :param upload_to:
        Un patrón de ruta como los usados en `format_path`.

    :param secret:
        Si es True, en vez del nombre de archivo original se usa uno al azar.

    :param prefix:
        Para evitar race-conditions entre varios usuarios subiendo archivos
        llamados igual al mismo tiempo. No se usa si `secret` es True

    :param allowed:
        Lista de extensiones permitidas. `None` para cualquiera.
        Si el archivo no tiene una de estas extensiones se lanza
        un error :class:`werkzeug.exceptions.UnsupportedMediaType`

    :param denied:
        Lista de extensiones prohibidas. `None` para ninguna.
        Si el archivo tiene una de estas extensiones se lanza
        un error :class:`werkzeug.exceptions.UnsupportedMediaType`

    """
    storage = FileStorage(upload_to, secret, allowed=allowed, denied=denied)
    return storage.save(filesto, root_path, prefix)


def format_path(tmplpath, filename, now=None):
    """
    {yyyy},{yy}: Year
    {mm}, {m}: Month (0-padded or not)
    {ww}, {w}: Week number in the year (0-padded or not)
    {dd}, {d}: Day (0-padded or not)
    {hh}, {h}: Hours (0-padded or not)
    {nn}, {n}: Minutes (0-padded or not)
    {ss}, {s}: Seconds (0-padded or not)
    {a+}: Filename first letters
    {z+}: Filename last letters
    {r+}: Random letters and/or numbers

    >>> tmplpath = '{zzz}/{yyyy}/{a}/{a}/{a}'
    >>> filename = 'monkey.png'
    >>> now = datetime(2010, 1, 14)
    >>> format_path(tmplpath, filename, now)
    'png/2010/m/o/n/'

    """
    path = tmplpath.lower()
    filename = filename.lower()
    now = now or datetime.datetime.utcnow()
    srx = r'\{(y{4}|[ymdhnws]{1,2}|[azr]+)\}'
    rx = re.compile(srx, re.IGNORECASE)
    len_filename = len(filename)
    a_pos = 0
    z_pos = 0
    delta = 0
    for match in rx.finditer(path):
        pattern = match.groups()[0]
        len_pattern = len(pattern)
        replace = '%0' + str(len_pattern) + 'i'
        if pattern.startswith('y'):
            replace = str(now.year)
            replace = replace[-len_pattern:]
        elif pattern.startswith('m'):
            replace = replace % now.month
        elif pattern.startswith('w'):
            tt = now.timetuple()
            replace = '%0' + str(len_pattern) + 'i'
            week = (tt.tm_yday + 7 - tt.tm_wday) / 7 + 1
            replace = replace % week
        elif pattern.startswith('d'):
            replace = replace % now.day
        elif pattern.startswith('h'):
            replace = replace % now.hour
        elif pattern.startswith('n'):
            replace = replace % now.minute
        elif pattern.startswith('s'):
            replace = replace % now.second
        elif pattern.startswith('a'):
            if a_pos >= len_filename:
                replace = '_'
            else:
                new_a_pos = a_pos + len_pattern
                replace = filename[a_pos:new_a_pos]
                a_pos = new_a_pos
        elif pattern.startswith('z'):
            new_z_pos = z_pos + len_pattern
            if z_pos == 0:
                replace = filename[-new_z_pos:]
            else:
                replace = filename[-new_z_pos:-z_pos]
            z_pos = new_z_pos
        elif pattern.startswith('r'):
            allowed_chars = 'abcdefghijklmnopqrstuvwxyz1234567890'
            replace = ''.join([random.choice(allowed_chars) \
                for i in range(len_pattern)])
        else:
            raise ValueError
        x, y = match.span()
        path = '%s%s%s' % (path[:x - delta], replace, path[y - delta:])
        delta += len_pattern + 2 - len(replace)
    if not path.endswith('/'):
        path += '/'
    return path


def get_unique_filename(root_path, path, name=None, ext=''):
    """ """
    path = os.path.join(root_path, path)
    abspath = os.path.abspath(path)
    i = 0
    while True:
        if not name:
            filename = str(uuid.uuid4())
        elif i:
            filename = '%s_%i' % (name, i)
            filename = secure_filename(filename)
        else:
            filename = secure_filename(name)

        if ext:
            filename = '%s.%s' % (filename, ext)
        filepath = os.path.join(abspath, filename)
        if not os.path.exists(filepath):
            break
        i += 1
    return filename
