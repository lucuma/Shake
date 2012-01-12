# -*- coding: utf-8 -*-
"""
# Shake.cli.generators

Generators of boilerplate code.

"""
import os
import re

from .globals import *
from .helpers import (underscores_to_camelcase, camelcase_to_underscores,
    pluralize, sanitize_name)


GEN_SKELETON = os.path.join(ROOTDIR, 'generators')

GENERATE_DESCRIPTION = """shake generate GENERATOR [ARGS] [OPTIONS]

      Generators of boilerplate code.
"""
generator = manager.subcommand('generate', description=GENERATE_DESCRIPTION,
    item_name='generator')


class BaseGenerator(object):
    """A base class for all generators"""

    field_types = {
        # Generic
        'biginteger': ('BigInteger', 'IntegerField'),
        'bigint': ('BigInteger', 'IntegerField'),
        'bool': ('Boolean', 'BooleanField'),
        'boolean': ('Boolean', 'BooleanField'),
        'date': ('Date', 'DateField'),
        'datetime': ('DateTime', 'DateTimeField'),
        'float': ('Float', 'FloatField'),
        'integer': ('Integer', 'IntegerField'),
        'int': ('Integer', 'IntegerField'),
        'binary': ('LargeBinary', ''),
        'decimal': ('Numeric', 'DecimalField'),
        'numeric': ('Numeric', 'DecimalField'),
        'smallinteger': ('SmallInteger', 'IntegerField'),
        'smallint': ('SmallInteger', 'IntegerField'),
        'string': ('Unicode(255)', 'TextField'),
        'text': ('UnicodeText', 'TextAreaField'),
        'unicode': ('Unicode(255)', 'TextField'),
        'unicodetext': ('UnicodeText', 'TextAreaField'),
        'time': ('Time', 'TextField'),
    }

    default_field = ('Unicode(255)', 'TextField')

    def __init__(self):
        if not hasattr(self, '__name__'):
            class_name = self.__class__.__name__
            class_name = class_name.replace('Generator', '')
            self.__name__ = camelcase_to_underscores(class_name)

    def run(self, *args, **kwargs):
        raise NotImplementedError
    
    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)


@generator.command
class ResourceGenerator(BaseGenerator):
    """NAME [field:type, ...] [options]

    Generates the model, views and controller of a resource.
    The resource is ready to use as a starting point for your RESTful,
    resource-oriented application.

    Pass the name of the model (in singular form), either CamelCased or
    under_scored, as the first argument, and an optional list of attribute
    pairs.

    Attribute pairs are field:type arguments specifying the
    model's attributes. Timestamps are added by default, so you don't have to
    specify them by hand as 'created_at:datetime'.

    You don't have to think up every attribute up front, but it helps to
    sketch out a few so you can start working with the resource immediately.

    For example, `resource post title:string body:text published:boolean`
    gives you a model with those three attributes, a controller that handles
    the create/show/update/destroy, forms to create and edit your posts, and
    an index that lists them all, as well as the routes in `urls.py`.

    Examples:
        shake generate resource post
        shake generate resource post title:string body:text published:boolean
        shake generate resource purchase order_id:integer amount:numeric
    
    """
    
    bundle_src = os.path.join(GEN_SKELETON, 'resource', 'bundle')
    views_src = os.path.join(GEN_SKELETON, 'resource', 'views')
    static_src = os.path.join(GEN_SKELETON, 'resource', 'static')

    bundle_dst = 'app/%s'
    views_dst = 'app/views/%s'
    static_dst = 'static'

    def run(self, *args, **kwargs):
        resource = sanitize_name('app', args[0])
        resource_plural = pluralize(resource)
        self.resource = resource
        self.resource_plural = resource_plural

        self.data = {
            'resource': resource,
            'resource_plural': resource_plural,
            'table_name': underscores_to_camelcase(resource),
            'fields': self.get_fields(args),
        }
        self.generate_bundle()
        self.generate_views()
        self.generate_static()
        self.insert_urls()
        self.insert_model_import()
    
    def get_fields(self, args):
        field_types = self.field_types
        default_field = self.default_field

        fields = []
        for f in args[1:]:
            try:
                fname, ftype = f.split(':')
            except ValueError:
                fname = f
                ftype = 'string'
            ftype = re.sub(r'[^a-z0-9]', '', ftype.lower())
            field = field_types.get(ftype, default_field)
            field = (fname, field[0], field[1])
            fields.append(field)
        return fields
    
    def generate_bundle(self):
        bundle_dst = self.bundle_dst % self.resource_plural
        print voodoo.formatm('invoke', bundle_dst, color='white')

        voodoo.reanimate_skeleton(self.bundle_src, bundle_dst, data=self.data,
            filter_ext=FILTER, env_options=ENV_OPTIONS)
        
    def generate_views(self):
        views_dst = self.views_dst % self.resource_plural
        print voodoo.formatm('invoke', views_dst, color='white')

        voodoo.reanimate_skeleton(self.views_src, views_dst, data=self.data,
            filter_ext=FILTER, env_options=ENV_OPTIONS)
    
    def generate_static(self):
        static_dst = self.static_dst
        print voodoo.formatm('invoke', static_dst, color='white')

        voodoo.reanimate_skeleton(self.static_src, static_dst, data=self.data,
            filter_ext=FILTER, env_options=ENV_OPTIONS)
    
    def insert_urls(self):
        urls_dst = 'app/urls.py'
        print voodoo.formatm('update', urls_dst, color='white')
        
        content = voodoo.read_from(urls_dst, binary=False)
        content = self._insert_url_import(content)
        content = self._insert_url_mount(content)
        voodoo.write_to(urls_dst, content, binary=False)
    
    def _insert_url_import(self, content):
        # Find the first two blank lines
        # Not the robustest method, but for now it works
        nc = "\nfrom .%s.urls import %s_urls\n\n\n" % \
            (self.resource_plural, self.resource_plural)
        return  re.sub(r'(\n\s*){3}', nc, content)
    
    def _insert_url_mount(self, content):
        # Find the last ']'
        # Not the robustest method, but for now it works
        nc = ",\n\n    Submount('/%s/', %s_urls),\n]\n" % \
            (self.resource_plural, self.resource_plural)
        return  re.sub(r',?\s*\][^\]]*$', nc, content)
    
    def insert_model_import(self):
        app_dst = 'app/app.py'
        print voodoo.formatm('update', app_dst, color='white')
        
        content = voodoo.read_from(app_dst, binary=False)
        # Find the first two blank lines
        # Not the robustest method, but for now it works
        nc = "\nfrom .%(rp)s import models as %(rp)s_models\n\n\n" % \
            {'rp': self.resource_plural}
        content = re.sub(r'(\n\s*){3}', nc, content)
        voodoo.write_to(app_dst, content, binary=False)

