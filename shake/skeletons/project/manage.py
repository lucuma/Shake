# -*- coding: utf-8 -*-
"""
Administration scripts

"""
import os
import sys

from shake import manager
from pyceo import prompt

lib_path = os.path.join(os.path.dirname(__file__), 'lib')
sys.path.insert(1, lib_path)

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
    from users.models import User

    print 'Creating tables...'
    db.create_all()
    print 'Done.'
    
    u = db.query(User).filter(User.login=='admin').first()
    if not u:
        print 'Creating `admin` user…'
        email = prompt('>>> Admin email? ')
        users.manage.create_user(u'admin', '123456',
            fullname=u'Admin', email=email)


import users.manage


if __name__ == "__main__":
    manager.run()
