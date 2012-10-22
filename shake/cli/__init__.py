# -*- coding: utf-8 -*-
"""
    Shake.cli
    --------------------------

    Command-line scripts

"""
from os.path import sep, dirname, isfile, join, abspath, normpath, realpath

import inflector
from pyceo import Manager, format_title
import voodoo

from . import helpers as h


ROOTDIR = normpath(abspath(realpath(join(dirname(__file__), '..', 'skeletons'))))
APP_SKELETON = join(ROOTDIR, 'project')
RESOURCE_SKELETON = join(ROOTDIR, 'resource')

ENV_OPTIONS = {
    'autoescape': False,
    'block_start_string': '[%',
    'block_end_string': '%]',
    'variable_start_string': '[[',
    'variable_end_string': ']]',
}

FILTER = ('.pyc', '.DS_Store', '.pyo')


manager = Manager()


@manager.command
def new(app_path='.', skeleton=APP_SKELETON, **options):
    """APP_PATH='.' [SKELETON_PATH]
    
    The 'shake new' command creates a new Shake application with a default
    directory structure at the path you specify.

    Example:
        shake new projects/wiki
    
    By default it uses Shake's built-in skeleton, but you can provide a custom
    one if you want.
    """
    quiet = options.get('quiet', options.get('q', False))
    pretend = options.get('pretend', options.get('p', False))

    app_path = app_path.rstrip(sep)
    data = {
        'SECRET1': h.make_secret(),
        'SECRET2': h.make_secret(),
    }
    voodoo.reanimate_skeleton(skeleton, app_path, data=data,
        filter_ext=FILTER, env_options=ENV_OPTIONS, **options)
    
    if not pretend:
        h.install_requirements(app_path, quiet)

    if not quiet:
        print voodoo.formatm('Done!', '', color='green')


@manager.command
def add(name=None, *args, **options):
    """NAME [field:type, ...] [options]

    Generates the model, templates and view of a resource.
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

    Examples:
        shake add post
        shake add post title:Unicode(255) body:UnicodeText published:Boolean
        shake add post purchase order_id:Integer amount:Numeric

    """
    if not name:
        print manager.get_help()
        return

    quiet = options.get('quiet', options.get('q', False))
    pretend = options.get('pretend', options.get('p', False))
    name = name.rstrip(sep)
    singular, plural, class_name = h.sanitize_name(name)

    bundle_src = join(RESOURCE_SKELETON, 'bundle')
    templates_src = join(RESOURCE_SKELETON, 'templates')
    bundle_dst = join('bundles', plural)
    templates_dst = join('templates', plural)

    data = {
        'singular': singular,
        'plural': plural,
        'class_name': class_name,
        'fields': h.get_model_fields(args),
    }
    
    # Bundle
    if not quiet:
        print voodoo.formatm('invoke', bundle_dst, color='white')
    bundle_dst = abspath(bundle_dst)
    voodoo.reanimate_skeleton(bundle_src, bundle_dst, data=data,
        filter_ext=FILTER, env_options=ENV_OPTIONS, **options)

    # templates
    if not quiet:
        print voodoo.formatm('invoke', templates_dst, color='white')
    templates_dst = abspath(templates_dst)
    voodoo.reanimate_skeleton(templates_src, templates_dst, data=data,
        filter_ext=FILTER, env_options=ENV_OPTIONS, **options)

    # Insert bundle import in urls.py
    if not quiet:
        print voodoo.formatm('update', 'urls.py', color='green')
    path = abspath('urls.py')
    if not isfile(path):
        if not quiet:
            print voodoo.formatm('warning', 'urls.py not found', color='yellow')
        return
    h.insert_import(path, 'from bundles import ' + plural)


@manager.command
def version():
    """Print the Shake current version."""
    import shake
    print shake.__version__


def main():
    ok = manager.run()
    if not ok:
        print format_title('GENERAL OPTIONS') + """
    -h, [--help]     # Show help
    -p, [--pretend]  # Run but do not make any changes
    -f, [--force]    # Overwrite files that already exist
    -s, [--skip]     # Skip files that already exist
    -q, [--quiet]    # Suppress status output
    """


# generator = manager.subcommand('generate',
#     description='shake generate GENERATOR [ARGS] [OPTIONS]',
#     item_name='generator')


if __name__ == "__main__":
    main()
