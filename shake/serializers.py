# -*- coding: utf-8 -*-
import datetime
# Get the fastest json available
try:
    import simplejson as json
except ImportError:
    import json


__all__ = ('to_json', 'from_json',)


DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'


def to_json(value, **options):
    options.setdefault('cls', JSONEncoder)
    options.setdefault('sort_keys', True)
    return json.dumps(value, **options)


def from_json(value, **options):
    options.setdefault('object_hook', _json_decoder)
    return json.loads(value, **options)


class JSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime(DATETIME_FORMAT)
        else:
            return json.JSONEncoder.default(self, obj)


def _json_decoder(d):
    if isinstance(d, list):
        return [_json_decoder(item) for item in d]
    for k, v in d.items():
        if not isinstance(v, basestring):
            continue
        try:
            d[k] = datetime.datetime.strptime(v, DATETIME_FORMAT)
        except ValueError:
            try:
                d[k] = datetime.datetime.strptime(v, DATE_FORMAT).date()
            except ValueError:
                pass
    return d
