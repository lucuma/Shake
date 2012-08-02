# -*- coding: utf-8 -*-
"""
    Manage scripts.
    --------------------------

"""
import shake
from shake import manager
from main import app, db
import urls


@manager.command
def server(host='0.0.0.0', port=None, **kwargs):
    """[-host HOST] [-port PORT]
    Runs the application on the local development server.
    """
    app.run(host, port, **kwargs)


@manager.command
def syncdb():
    """Create the database tables (if they don't exist)"""
    from bundles.users.models import create_admin

    print 'Founded this tables:'
    print ' '.join(db.Model.metadata.tables.keys())
    print 'Creating tables if needed...'
    db.create_all()
    print 'Done.'
    create_admin()


@manager.command
def load_data():
    """Load the inital data"""
    db.load_data(app.settings.FIXTURES_DIR)
    db.load_media(app.settings.FIXTURES_DIR)


@manager.command
def dump_data():
    """Serialize the current data to fixtures/xxx.json"""
    db.dump_data(app.settings.FIXTURES_DIR)


@manager.command
def set_env(env):
    """Set the current environment.
    """
    print 'SHAKE_ENV is now %s' % shake.set_env(env)


@manager.command
def get_env():
    """Print the current environment.
    """
    print 'SHAKE_ENV is %s' % shake.get_env()


## Insert here the imports to the manage scripts of your bundles
import bundles.users.manage


if __name__ == "__main__":
    manager.run()

