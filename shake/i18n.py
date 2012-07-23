# -*- coding: utf-8 -*-
"""
    Shake.i18n
    --------------------------

    Implements i18n/l10n support for Shake applications based on the 
    awesome Babel and pytz.

    ----------------
    Some code derived from Flask-Babel (c) 2010 by Armin Ronacher.
    Used under the modified BSD license.

"""
from __future__ import absolute_import
import os

# Workaround for a OSX bug
if os.environ.get('LC_CTYPE', '').lower() == 'utf-8':
    os.environ['LC_CTYPE'] = 'en_US.utf-8'

from collections import defaultdict
import datetime as d
from decimal import Decimal
import io
from os.path import join, dirname, realpath, abspath, normpath, isdir, isfile

from babel import dates, numbers, support, Locale
from jinja2 import Markup
from pytz import timezone, UTC
from werkzeug import ImmutableDict
import yaml

from .helpers import local


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

        if isinstance(locales_dirs, basestring):
            locales_dirs = [locales_dirs]
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
        """The default locale from the configuration as an instance of
        `Babel.Locale`.

        """
        locale = self.app.settings.DEFAULT_LOCALE
        if isinstance(locale, tuple):
            return Locale(*locale)
        return Locale.parse(locale)


    @property
    def default_timezone(self):
        """The default timezone from the configuration as instance of a
        `pytz.timezone` object.

        """
        return timezone(self.app.settings.DEFAULT_TIMEZONE)


    def get_locale(self):
        """Returns the locale that should be used for this request as
        an instance of `Babel.Locale`.
        This returns the default locale if used outside of a request.

        """
        locale = hasattr(local, 'request') and local.request.get_locale()
        return locale or self.default_locale


    def get_timezone(self):
        """Returns the timezone that should be used for this request as
        `pytz.timezone` object.  This returns the default timezone if used
        outside of a request or if no timezone was defined.

        """
        tzinfo = hasattr(local, 'request') and local.request.tzinfo
        if not tzinfo:
            tzinfo = self.default_timezone
        elif isinstance(tzinfo, basestring):
            tzinfo = timezone(tzinfo)
        return tzinfo


    def load_language(self, path, locale):
        """From the given `path`, load the language file for the current or
        given locale.  If the locale has a territory attribute (eg: 'US') the
        the specific 'en_US' version will be tried first.

        """
        if locale.territory:
            filenames = [str(locale), locale.language]
        else:
            filenames = [locale.language]
        filenames.append(str(self.default_locale))

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


    def find_keypath(self, key):
        """Based on the `key`, teturn the path of the language file and the
        subkey inside that file.

        """
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


    def key_lookup(self, key, locale):
        """
        """
        path, subkey = self.find_keypath(key)
        if not (path and subkey):
            return None

        value = self.load_language(path, locale)
        if value is None:
            return None

        try:
            for k in subkey.split('.'):
                value = value.get(k)
                if value is None:
                    return None
            return value
        except (IndexError, ValueError), e:
            return None


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
        locale = locale or self.get_locale()
        value = self.key_lookup(key, locale)
        if not value:
            return Markup('<missing:%s>' % (key, ))
        
        if isinstance(value, dict):
            value = self.pluralize(value, count)

        if isinstance(value, basestring):
            kwargs.setdefault('count', count)
            value = value % kwargs
            if key.endswith('_html'):
                return Markup(value)

        return value


    def pluralize(self, d, count):
        """Takes a dictionary and a number and return the value whose key in
        the dictionary is that number.  If that key doesn't exist, a `'n'` key
        is tried instead.  If that doesn't exits either, an empty string is
        returned.  Examples:

            >>> i18n = I18n()
            >>> d = {
                0: u'No apples',
                1: u'One apple',
                3: u'Few apples',
                'n': u'%(count)s apples',
                }
            >>> i18n.pluralize(d, 0)
            'No apples'
            >>> i18n.pluralize(d, 1)
            'One apple'
            >>> i18n.pluralize(d, 3)
            'Few apples'
            >>> i18n.pluralize(d, 10)
            '%(count)s apples'
            >>> i18n.pluralize({0: 'off', 'n': 'on'}, 3)
            'on'
            >>> i18n.pluralize({0: 'off', 'n': 'on'}, 0)
            'off'
            >>> i18n.pluralize({}, 3)
            ''

        """
        if count is None:
            count = 0
        scount = str(count)
        return d.get(count, d.get(scount, d.get('n', u'')))
    

    def to_user_timezone(self, datetime, tzinfo=None):
        """Convert a datetime object to the user's timezone.  This automatically
        happens on all date formatting unless rebasing is disabled.  If you need
        to convert a `datetime.datetime` object at any time to the user's
        timezone (as returned by `get_timezone` this function can be used).

        """
        if datetime.tzinfo is None:
            datetime = datetime.replace(tzinfo=UTC)
        tzinfo = tzinfo or self.get_timezone()
        return tzinfo.normalize(datetime.astimezone(tzinfo))


    def to_utc(self, datetime, tzinfo=None):
        """Convert a datetime object to UTC and drop tzinfo.  This is the
        opposite operation to `to_user_timezone`.

        """
        if datetime.tzinfo is None:
            tzinfo = tzinfo or self.get_timezone()
            datetime = tzinfo.localize(datetime)
        return datetime.astimezone(UTC).replace(tzinfo=None)


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


    def _date_format(self, formatter, obj, format, rebase,
            locale=None, tzinfo=None, **extra):
        """Internal helper that formats the date.

        """
        locale = locale or self.get_locale()
        extra = {}
        if formatter is not dates.format_date and rebase:
            extra['tzinfo'] = tzinfo or self.get_timezone()
        return formatter(obj, format, locale=locale, **extra)


    def format(self, value, *args, **kwargs):
        """Return a formatted `value` according to the detected type and
        given parameters.  It doesn't know anything about currency, percent or
        scientific formats, so use the other methods for those cases.
        
        """
        locale = kwargs.pop('locale', None)
        tzinfo = kwargs.pop('tzinfo', None)

        if isinstance(value, d.date):
            if isinstance(value, d.datetime):
                return self.format_datetime(value, locale=locale, tzinfo=tzinfo,
                    *args, **kwargs)
            else:
                return self.format_date(value, locale=locale, tzinfo=tzinfo, 
                    *args, **kwargs)

        if isinstance(value, int):
            return self.format_number(value, locale=locale, *args, **kwargs)
        if isinstance(value, (float, Decimal)):
            return self.format_decimal(value, locale=locale, *args, **kwargs)

        if isinstance(value, d.time):
            return self.format_time(value, locale=locale, tzinfo=tzinfo,
                *args, **kwargs)
        if isinstance(value, d.timedelta):
            return self.format_timedelta(value, locale=locale, *args, **kwargs)

        return value


    def format_datetime(self, datetime=None, format=None, rebase=True,
            locale=None, tzinfo=None):
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
        return self._date_format(dates.format_datetime, datetime, format,
            rebase, locale=locale, tzinfo=tzinfo)


    def format_date(self, date=None, format=None, rebase=True,
            locale=None, tzinfo=None):
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
        if rebase and isinstance(date, d.datetime):
            date = self.to_user_timezone(date, tzinfo=tzinfo)
        format = self._get_format('date', format)
        return self._date_format(dates.format_date, date, format, rebase,
            locale=locale, tzinfo=tzinfo)


    def format_time(self, time=None, format=None, rebase=True,
            locale=None, tzinfo=None):
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
        format = self._get_format('time', format)
        return self._date_format(dates.format_time, time, format, rebase,
            locale=locale, tzinfo=tzinfo)


    def format_timedelta(self, datetime_or_timedelta, granularity='second',
            locale=None):
        """Format the elapsed time from the given date to now or the given
        timedelta.

        This function is also available in the template context as filter
        named `timedeltaformat`.

        """
        locale = locale or self.get_locale()
        if isinstance(datetime_or_timedelta, d.datetime):
            datetime_or_timedelta = d.datetime.utcnow() - datetime_or_timedelta
        return dates.format_timedelta(datetime_or_timedelta, granularity,
            locale=locale)


    def format_number(self, number, locale=None):
        """Return the given number formatted for the locale in the
        current request.
        
        number
        :   the number to format
        
        return (unicode)
        :   the formatted number

        This function is also available in the template context as filter
        named `numberformat`.
        
        """
        locale = locale or self.get_locale()
        return numbers.format_number(number, locale=locale)


    def format_decimal(self, number, format=None, locale=None):
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
        locale = locale or self.get_locale()
        return numbers.format_decimal(number, format=format, locale=locale)


    def format_currency(self, number, currency, format=None, locale=None):
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
        locale = locale or self.get_locale()
        return numbers.format_currency(
            number, currency, format=format, locale=locale
        )


    def format_percent(self, number, format=None, locale=None):
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
        locale = locale or self.get_locale()
        return numbers.format_percent(number, format=format, locale=locale)


    def format_scientific(self, number, format=None, locale=None):
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
        locale = locale or self.get_locale()
        return numbers.format_scientific(number, format=format, locale=locale)

