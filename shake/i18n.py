# -*- coding: utf-8 -*-
"""
    Shake.i18n
    --------------------------

    Implements i18n/l10n support for Shake applications based on Babel and pytz.

    ----------------
    Some portions derived from Flask-Babel (c) 2010 by Armin Ronacher.
    Used under the modified BSD license.

"""
from __future__ import absolute_import
import os

# Workaround for a OSX bug
if os.environ.get('LC_CTYPE', '').lower() == 'utf-8':
    os.environ['LC_CTYPE'] = 'en_US.utf-8'

from collections import defaultdict
from datetime import datetime
import io
from os.path import join, dirname, realpath, abspath, normpath, isdir, isfile

from babel import dates, numbers, support, Locale
from jinja2 import Markup
from pytz import timezone, UTC
from werkzeug import ImmutableDict
import yaml


LOCALES_DIR = 'locales'


class I18n(object):
    """Internationalization system
    """

    default_date_formats = ImmutableDict({
        'time': 'medium',
        'date': 'medium',
        'datetime': 'medium',
        'time.short': None,
        'time.medium': None,
        'time.full': None,
        'time.long': None,
        'date.short': None,
        'date.medium': None,
        'date.full': None,
        'date.long': None,
        'datetime.short': None,
        'datetime.medium': None,
        'datetime.full': None,
        'datetime.long': None,
    })
    

    def __init__(self, locales_dirs=None, app=None, date_formats=None):
        """

        locales_dirs
        :   list of paths that will be searched, in order, for the locales
        app
        :   a `Shake` instance.
        date_formats
        :   defaults date formats.

        """
        self.translations = {}

        locales_dirs = locales_dirs or [LOCALES_DIR]
        search_paths = []
        for p in locales_dirs:
            p = normpath(abspath(realpath(p)))
            if not isdir(p):
                p = dirname(p)
            search_paths.append(p)
        self.search_paths = search_paths
        self.date_formats = self.default_date_formats.copy()
        if app:
            self.init_app(app)


    def init_app(self, app):
        """
        """
        self.app = app


    @property
    def default_locale(self):
        """The default locale from the configuration as a string.

        """
        return self.app.settings.DEFAULT_LOCALE


    @property
    def default_timezone(self):
        """The default timezone from the configuration as instance of a
        `pytz.timezone` object.

        """
        return timezone(self.app.settings.DEFAULT_TIMEZONE)


    def get_str_locale(self):
        """Returns the locale that should be used for this request as
        a string. This returns the default locale if used outside of a request.

        """
        locale = local.request and local.request.get_locale()
        locale = locale or self.default_locale
        return locale.split('.')[0].replace('_', '-')


    def get_locale(self):
        """Returns the locale that should be used for this request as
        an instance of `Babel.Locale`.
        This returns the default locale if used outside of a request.

        """
        slocale = self.get_str_locale()
        return Locale.parse(slocale, sep='-')


    def get_timezone(self):
        """Returns the timezone that should be used for this request as
        `pytz.timezone` object.  This returns the default timezone if used
        outside of a request or if no timezone was defined.

        """
        tzinfo = local.request and local.request.tzinfo
        if not tzinfo:
            tzinfo = self.default_timezone
        elif isinstance(tzinfo, basestring):
            tzinfo = timezone(tzinfo)
        return tzinfo


    def translate(self, key, count=None, locale=None, **kwargs):
        """Load the translation for the given key using the current locale.

        If the value is a dictionary, and `count` is defined, uses the value
        whose key is that number.  If that key doesn't exist, a `'n'` key
        is tried instead.  If that doesn't exits either, an empty string is
        returned.

        The final value is formatted using `kwargs` (and also `count` if
        available) so the format placeholders must be named instead of
        positional.

        If the value isn't a dictionary or a string, is returned as is.

        Examples:

            >>> translate('hello_world')
            'hello %(what)s'
            >>> translate('hello_world', what='world')
            'hello world'
            >>> translate('a_list', what='world')
            ['a', 'b', 'c']

        """
        key = str(key)
        locale = locale or self.get_str_locale()
        value = self.key_lookup(key)
        if not value:
            return Markup('<missing:%s>' % (key, ))
        
        if isinstance(value, dict):
            value = self.pluralize(value, count)

        if isinstance(value, basestring):
            value = value % kwargs
            if key.endswith('_html'):
                return Markup(value)

        return value


    def key_lookup(self, key):
        """
        """
        path, subkey = self._find_keypath(key)
        if not (path and subkey):
            return None

        value = self._load_language(path, locale)

        try:
            for k in subkey.split('.'):
                value = value.get(k)
            return value
        except (IndexError, ValueError), e:
            return None


    def _find_keypath(self, key):
        if ':' not in key:
            return self.search_paths[0], key

        path, subkey = key.split(':', 1)
        lpath = path.split('.')

        for root in self.search_paths:
            dirname, dirnames, filenames = os.walk(root).next()
            if lpath[0] in dirnames:
                break
        else:
            return None, None

        path = join(root, *lpath)
        if not isdir(path):
            return None, None
        return path, subkey


    def _load_language(self, path, locale):
        """From the given `path`, load the language file for the current or
        given locale.  If the locale has a regional part (eg: 'en-US') the
        language-wide version will be tried as well (eg: 'en') if the first
        is not found.

        """
        filenames = [locale]
        if '-' in locale:
            filenames.append(locale.split()[0])
        filenames.append(self.default_locale)

        for filename in filenames:
            cache_key = join(path, filename)
            cached = self.translations.get(cache_key)
            if cached:
                return cached
            filename = cache_key + '.yml'
            if isfile(filename):
                break
        else:
            return
        try:
            with io.open(filename) as f:
                data = yaml.load(f)
            self.translations[cache_key] = data
            return data
        except (IOError, AttributeError):
            return


    def pluralize(self, d, count):
        """Takes a dictionary and a number and return the value whose key in
        the dictionary is that number.  If that key doesn't exist, a `'n'` key
        is tried instead.  If that doesn't exits either, an empty string is
        returned.  Examples:

            >>> i18n = I18n()
            >>> d = {
                0: 'No apples'
                1: 'One apple',
                3: 'Few apples',
                'n': '%(count)s apples',
                }
            >>> i18n.pluralize(d, 0)
            'No apples'
            >>> i18n.pluralize(d, 1)
            'One apple'
            >>> i18n.pluralize(d, 3)
            'Few apples'
            >>> i18n.pluralize(d, 10)
            '10 apples'
            >>> i18n.pluralize({0: 'off', 'n': 'on'}, 3)
            'on'
            >>> i18n.pluralize({0: 'off', 'n': 'on'}, 0)
            'off'
            >>> i18n.pluralize({}, 3)
            ''

        """
        en_count = str(count)
        if count is None:
            count = 0
        if isinstance(count, int):
            en_count = number_to_english(count)
        return d.get(count, d.get(en_count, d.get('other', u'')))
    

    def _get_format(self, key, format):
        """A small helper for the datetime formatting functions.  Looks up
        format defaults for different kinds.

        """
        if format is None:
            format = self.date_formats.get(key)
        if format in ('short', 'medium', 'full', 'long'):
            rv = self.date_formats['%s.%s' % (key, format)]
            if rv is not None:
                format = rv
        return format
    

    def to_user_timezone(self, datetime):
        """Convert a datetime object to the user's timezone.  This automatically
        happens on all date formatting unless rebasing is disabled.  If you need
        to convert a :class:`datetime.datetime` object at any time to the user's
        timezone (as returned by `get_timezone` this function can be used).

        """
        if datetime.tzinfo is None:
            datetime = datetime.replace(tzinfo=UTC)
        tzinfo = self.get_timezone()
        return tzinfo.normalize(datetime.astimezone(tzinfo))


    def to_utc(self, datetime):
        """Convert a datetime object to UTC and drop tzinfo.  This is the
        opposite operation to `to_user_timezone`.

        """
        if datetime.tzinfo is None:
            datetime = self.get_timezone().localize(datetime)
        return datetime.astimezone(UTC).replace(tzinfo=None)


    def format_datetime(self, datetime=None, format=None, rebase=True):
        """Return a date formatted according to the given pattern.  If no
        `datetime.datetime` object is passed, the current time is
        assumed.  By default rebasing happens which causes the object to
        be converted to the users's timezone (as returned by
        `to_user_timezone`).  This function formats both date and
        time.

        The format parameter can either be `'short'`, `'medium'`,
        `'long'` or `'full'` (in which cause the language's default for
        that setting is used, or the default from the `Babel.date_formats`
        mapping is used) or a format string as documented by Babel.

        This function is also available in the template context as filter
        named `datetimeformat`.

        """
        format = self._get_format('datetime', format)
        return self._date_format(dates.format_datetime, datetime, format, rebase)


    def format_date(self, date=None, format=None, rebase=True):
        """Return a date formatted according to the given pattern.  If no
        `datetime.datetime` or `datetime.date` object is passed,
        the current time is assumed.  By default rebasing happens which causes
        the object to be converted to the users's timezone (as returned by
        `to_user_timezone`).  This function only formats the date part
        of a `datetime.datetime` object.

        The format parameter can either be `'short'`, `'medium'`,
        `'long'` or `'full'` (in which cause the language's default for
        that setting is used, or the default from the `Babel.date_formats`
        mapping is used) or a format string as documented by Babel.

        This function is also available in the template context as filter
        named `dateformat`.

        """
        if rebase and isinstance(date, datetime):
            date = self.to_user_timezone(date)
        format = self._get_format('date', format)
        return self._date_format(dates.format_date, date, format, rebase)


    def format_time(self, time=None, format=None, rebase=True):
        """Return a time formatted according to the given pattern.  If no
        `datetime.datetime` object is passed, the current time is
        assumed.  By default rebasing happens which causes the object to
        be converted to the users's timezone (as returned by
        `to_user_timezone`).  This function formats both date and
        time.

        The format parameter can either be `'short'`, `'medium'`,
        `'long'` or `'full'` (in which cause the language's default for
        that setting is used, or the default from the Babel.date_formats`
        mapping is used) or a format string as documented by Babel.

        This function is also available in the template context as filter
        named `timeformat`.

        """
        format = _get_format('time', format)
        return self._date_format(dates.format_time, time, format, rebase)


    def format_timedelta(self, datetime_or_timedelta, granularity='second'):
        """Format the elapsed time from the given date to now or the given
        timedelta.

        This function is also available in the template context as filter
        named `timedeltaformat`.

        """
        locale = self.get_locale()
        if isinstance(datetime_or_timedelta, datetime):
            datetime_or_timedelta = datetime.utcnow() - datetime_or_timedelta
        return dates.format_timedelta(datetime_or_timedelta, granularity,
            locale=locale)


    def _date_format(formatter, obj, format, rebase, **extra):
        """Internal helper that formats the date."""
        locale = self.get_locale()
        extra = {}
        if formatter is not dates.format_date and rebase:
            extra['tzinfo'] = self.get_timezone()
        return formatter(obj, format, locale=locale, **extra)


    def format_number(self, number):
        """Return the given number formatted for the locale in the
        current request.
        
        number
        :   the number to format
        
        return (unicode)
        :   the formatted number

        This function is also available in the template context as filter
        named `numberformat`.
        
        """
        locale = self.get_locale()
        return numbers.format_number(number, locale=locale)


    def format_decimal(self, number, format=None):
        """Return the given decimal number formatted for the locale in the
        current request.

        number
        :   the number to format
        format
        :   the format to use
        
        return (unicode)
        :   the formatted number

        This function is also available in the template context as filter
        named `decimalformat`.
        
        """
        locale = self.get_locale()
        return numbers.format_decimal(number, format=format, locale=locale)


    def format_currency(self, number, currency, format=None):
        """Return the given number formatted for the locale in the
        current request.

        number
        :   the number to format
        currency
        :   the currency code
        format
        :   the format to use
        
        return (unicode)
        :   the formatted number

        This function is also available in the template context as filter
        named `currencyformat`.
        
        """
        locale = self.get_locale()
        return numbers.format_currency(
            number, currency, format=format, locale=locale
        )


    def format_percent(self, number, format=None):
        """Return a percent value formatted for the locale in the
        current request.

        number
        :   the number to format
        format
        :   the format to use
        
        return (unicode)
        :   the formatted percent number
        
        This function is also available in the template context as filter
        named `percentformat`.

        """
        locale = self.get_locale()
        return numbers.format_percent(number, format=format, locale=locale)


    def format_scientific(self, number, format=None):
        """Return value formatted in scientific notation for the locale in
        the current request.

        number
        :   the number to format
        format
        :   the format to use
        
        return (unicode)
        :   the formatted percent number
        
        This function is also available in the template context as filter
        named `scientificformat`.

        """
        locale = self.get_locale()
        return numbers.format_scientific(number, format=format, locale=locale)

