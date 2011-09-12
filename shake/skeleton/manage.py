# -*- coding: utf-8 -*-
"""
    manage.py
    ----------------------------------------------
    Admin scripts

"""
from shake import manager

from app.app import app


@manager.command
def runserver(host='0.0.0.0', port=None, **kwargs):
    """[-host HOST] [-port PORT]
    Runs the application on the local development server.
    """
    app.run(host, port, **kwargs)


@manager.command
def run_wsgi():
    """Expose the application to be executed using the WSGI protocol."""
    import os
    import sys
    
    cwd = os.path.abspath(os.path.dirname(__file__))
    sys.path.insert(0, cwd)
    application = app


@manager.command
def run_cherrypy(host=None, port=None, processes=1, server_name=None, **kwargs):
    """Runs the application on top of the CherryPy WSGI server.
    This server can be used on production but it is recomended to use
    another server, like NGINX for the static files.
    """
    app.run_cherrypy(host, port, processes=processes, server_name=server_name,
        **kwargs)


@manager.command
def initdb():
    """Create the database tables (if they don't exist)"""
    from app.models import db
    
    db.create_all()


@manager.command
def syncdb():
    initdb()


@manager.command
def create_user(login, passw, **data):
    """[-login] LOGIN [-passw] PASSWORD
    Creates a new user.
    """
    from app.app import auth
    
    auth.create_user(login, passw, **data)


@manager.command
def change_password(login, passw):
    """[-login] LOGIN [-passw] NEW_PASSWORD
    Changes the password of an existing user."""
    from app.app import auth
    
    auth.change_password(login, passw)


@manager.command
def add_perms(login, *perms):
    """[-login] LOGIN [-perms] *PERMISSIONS
    Add permissions to the user
    """
    from app.models import db, User
    
    user = User.query.filter_by(login=login).first()
    if not user:
        raise ValueError(login)
    user.add_perms(perms)
    db.session.commit()


if __name__ == "__main__":
    manager.run(default='runserver')
