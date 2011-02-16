# -*- coding: utf-8 -*-
"""
    shake.media
    ----------------------------------------------

    Easy management of external stylesheets, scripts, meta tags and other.

    The data structures are list of tuples instead of dicts to maintain the
    order of the attributes.

    :copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
    :license: BSD. See LICENSE for more details.

"""
import re

from .helpers import local


RX_SCRIPT = re.compile(r'</script>', re.IGNORECASE)
RX_STYLE = re.compile(r'</style>', re.IGNORECASE)


def _get_local_media():
    media = getattr(local, 'media', None)
    if not media:
        local.media = {}
    return local('media')


def _undent(text):
    return re.sub(r'[\s\n\t]+', ' ', text).strip()


def _render(name, templ, templ_raw=None):
    media = _get_local_media()

    files = media.get(name, [])
    cond_files = media.get('cond_' + name, {})

    result = []

    for data in files:
        is_raw = isinstance(data, basestring)
        if is_raw:
            result.append(templ_raw % data)
        else:
            body = _render_attributes(data)
            result.append(templ % body)

    for condition in cond_files.keys():
        sub_files = cond_files[condition]
        subres = ['<!--[if %s]>' % condition]
        for data in sub_files:
            is_raw = isinstance(data, basestring)
            if is_raw:
                subres.append(templ_raw % data)
            else:
                body = _render_attributes(data)
                subres.append(templ % body)
        subres.append('<![endif]-->')
        result.append('\n'.join(subres))
    return '\n'.join(result)


def _render_attributes(data):
    body = []
    for attr, val in data:
        if val is None:
            continue
        body.append('%s="%s"' % (attr, val))
    return ' '.join(body)


def _add_file(name, data, condition=None):
    media = _get_local_media()
    if condition:
        name = 'cond_' + name
        media.setdefault(name, {})
        cond = media[name]
        cond.setdefault(condition, [])
        group = cond[condition]
    else:
        media.setdefault(name, [])
        group = media[name]

    if data not in group:
        group.append(data)
    return ''


def add_css(src, title=None, iecon=None, media='all', alternate=False,
      raw=False):
    if raw:
        src = _undent(src)
        # You dont want to break the CSS parser, wouldn't you?
        src = RX_STYLE.sub(r'<\/style>', src)
        return _add_file('css', src, iecon)

    data = [
        ('href', src),
        ('media', media),
        ('rel', 'alternate stylesheet' if alternate else 'stylesheet'),
        ('title', title),
        ]
    return _add_file('css', data, iecon)


def add_js(src, iecon=None, raw=False):
    if raw:
        src = _undent(src)
        # You dont want to break the HTML parser, wouldn't you?
        src = RX_SCRIPT.sub(r'<\/script>', src)
        return _add_file('js', src, iecon)

    data = [
        ('src', src),
        ]
    return _add_file('js', data, iecon)


def add_link(src, rel, title=None, mtype=None):
    data = [
        ('href', src),
        ('rel', rel),
        ('title', title),
        ('type', mtype),
        ]
    return _add_file('link', data)


def add_feed(src, title, mtype='rss+xml'):
    return add_link(src, 'alternate', title, mtype)


def add_meta(name, content):
    data = [
        ('name', name),
        ('content', content),
        ]
    return _add_file('meta', data)


def render_css():
    templ = '<link %s>'
    templ_raw = '<style>%s</style>'
    return _render('css', templ, templ_raw=templ_raw)


def render_js():
    templ = '<script %s></script>'
    templ_raw = '<script>%s</script>'
    return _render('js', templ, templ_raw=templ_raw)


def render_links():
    templ = '<link %s>'
    return _render('link', templ)


def render_metas():
    templ = '<meta %s>'
    return _render('meta', templ)
