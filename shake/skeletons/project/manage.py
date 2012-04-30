# -*- coding: utf-8 -*-
"""
Administration scripts

"""
from shake import manager
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
    from bundles.users.models import create_admin

    print 'Founded this tables:'
    print ' '.join(db.Model.metadata.tables.keys())
    print 'Creating tables if needed...'
    db.create_all()
    print 'Done.'
    create_admin()


## Insert here the imports to the manage scripts of your bundles
import bundles.users.manage


if __name__ == "__main__":
    manager.run()

