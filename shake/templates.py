# -*- coding: utf-8 -*-
"""
    Shake.templates
    --------------------------

    Template globals, filters and tests

"""
import re
from xml.sax.saxutils import quoteattr

from jinja2 import Markup

from .helpers import local, to_unicode, url_for


__all__ = (
    'link_to', 'dumb_plural', 
)


def dumb_plural(num, plural='s', singular=''):
    """A dumb simple pluralize function.  Don't use this is your application
    is internationalizated.  Use {{ t('key_name', count) }} instead.
    """
    return plural if num != 1 else singular


def html_attrs(classes=None, **kwargs):
    """Generate HTML attributes from the provided keyword arguments.

    The output value is sorted by the passed keys, to provide a consistent
    output.  Because of the frequent use of the normally reserved keyword
    `class`, `classes` is used instead. Also, all underscores are translated
    to regular dashes.

    Set any property with a `True` value.

    >>> _get_html_attrs({'id': 'text1', 'classes': 'myclass',
        'data_id': 1, 'checked': True})
    u'class="myclass" data-id="1" id="text1" checked'

    """
    attrs = []
    props = []

    classes = classes.strip()
    if classes:
        classes = to_unicode(quoteattr(classes))
        attrs.append('class=%s' % classes)

    for key, value in kwargs.iteritems():
        key = key.replace('_', '-')
        key = to_unicode(key)
        if isinstance(value, bool):
            if value is True:
                props.append(key)
        else:
            value = quoteattr(to_unicode(value))
            attrs.append(u'%s=%s' % (key, value))

    attrs.sort()
    props.sort()
    attrs.extend(props)
    return u' '.join(attrs)


URL_RE = ur'^([a-z]{3,7}:(//)?)?([^/:]+%s|([0-9]{1,3}\.){3}[0-9]{1,3})(:[0-9]+)?(\/.*)?$'


def link_to(text='', endpoint='', classes='', wrapper=None, partial=False, **kwargs):
    """Build an HTML anchor element for the provided URL.
    If the url match the beginning of that in the current request, an `active`
    class is added.  This is intended to be use to build navigation links.

    Other HTML attributes are generated from the keyword argument
    (see the `html_attrs` function).

    Example:

        >>> link_to('Hello', '/hello/', title='click me')
        u'<a href="/hello/" title="click me">Hello</a>'
        >>> link_to('Hello', '/hello/', wrapper='li', classes='last')
        u'<li class="last"><a href="/hello/">Hello</a></li>'

        >>> from werkzeug.test import EnvironBuilder
        >>> builder = EnvironBuilder(method='GET', path='/foo/')
        >>> env = builder.get_environ()
        >>> from shake import Request
        >>> local.request = Request(env)
        >>> link_to('Bar', '/foo/')
        u'<a href="/foo/" class="active">Bar</a>'

    :param text:
        The text (or HTML) of the link.

    :param endpoint:
        URL or endpoint name. This can also be a *list* of URLs and/or
        endpoint names. The first one will be used for the link, the rest only
        to match the current page

    :param classes:
        Because of the frequent use of the normally reserved keyword
        `class`, `classes` is used instead.

    :param wrapper:
        Optional tag name of a wrapper element for the link.
        The "active" class and other attributes will be applied to this
        element instead of the <a>. Example:

        >>> link_to('Hello', '/hello/', wrapper='li', title='Hi')
        u'<li title="Hi"><a href="/hello/">Hello</a></li>'

    :param partial:
        If True, the endpoint will be matched against the beginning of the
        current URL. For instance, if the current URL is `/foo/bar/123/`,
        an endpoint like `/foo/bar/` will be considered a match.

    :param kwargs:
        Extra HTML attributes. All underscores will be translated to
        regular dashes.

    """
    request = local.request
    path = request.path.rstrip('/')

    patterns = endpoint if isinstance(endpoint, (list, tuple)) else [endpoint]
    patterns = [p
        if p.startswith('/') or re.match(URL_RE, p) else url_for(p)
        for p in patterns]

    for url in patterns:
        url = url.rstrip('/')
        if path == url or (partial and path.startswith(url)):
            classes += ' active'
            break

    data = {
        'url': patterns[0],
        'text': text,
        'attrs': html_attrs(classes, **kwargs),
    }
    data['attrs'] = ' ' + data['attrs'] if data['attrs'] else ''
    if wrapper:
        data['wr'] = str(wrapper).lower()
        tmpl = u'<%(wr)s %(attrs)s><a href="%(url)s">%(text)s</a></%(wr)s>'
    else:
        tmpl = u'<a href="%(url)s"%(attrs)s>%(text)s</a>'
    return Markup(tmpl % data)

