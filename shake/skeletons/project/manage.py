# -*- coding: utf-8 -*-
"""
Administration scripts

"""
import os
import sys

from shake import manager

lib_path = os.path.join(os.path.dirname(__file__), 'lib')
sys.path.insert(0, lib_path)
bundles_path = os.path.join(os.path.dirname(__file__), 'bundles')
sys.path.insert(0, bundles_path)

from main import app
import urls


@manager.command
def runserver(host='0.0.0.0', port=None, **kwargs):
    """[-host HOST] [-port PORT]
    Runs the application on the local development server.
    """
    from main import app
    app.run(host, port, **kwargs)


@manager.command
def syncdb():
    """Create the database tables (if they don't exist)"""
    from main import db
    from users.models import create_admin

    print 'Creating tables...'
    db.create_all()
    print 'Done.'
    create_admin()


## Insert here the imports to the manage scripts of your bundles
import users.manage


if __name__ == "__main__":
    manager.run()

