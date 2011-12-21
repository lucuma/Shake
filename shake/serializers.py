# -*- coding: utf-8 -*-
import datetime
# Get the fastest json available
try:
    import simplejson as json
except ImportError:
    try:
        from django.utils import simplejson as json
    except ImportError:
        try:
            import json
        except ImportError:
            raise ImportError('Unable to find a JSON implementation')


def to_json(value, **options):
    options.setdefault('cls', JSONEncoder)
    options.setdefault('sort_keys', True)
    return json.dumps(value, **options)


def from_json(value, **options):
    options.setdefault('object_hook', json_decoder)
    return json.loads(value, **options)


#------------------------------------------------------------------------------


DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'


class JSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime(DATETIME_FORMAT)
        else:
            return json.JSONEncoder.default(self, obj)


def json_decoder(d):
    if isinstance(d, list):
        pairs = enumerate(d)
    elif isinstance(d, dict):
        pairs = d.items()
    result = []
    for k, v in pairs:
        if isinstance(v, basestring):
            try:
                v = datetime.datetime.strptime(v, DATETIME_FORMAT)
            except ValueError:
                try:
                    v = datetime.datetime.strptime(v, DATE_FORMAT).date()
                except ValueError:
                    pass
        elif isinstance(v, (dict, list)):
            v = json_decoder(v)
        result.append((k, v))
    if isinstance(d, list):
        return [x[1] for x in result]
    elif isinstance(d, dict):
        return dict(result)

