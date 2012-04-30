# -*- coding: utf-8 -*-
"""
Administration scripts

"""
from shake import manager
from pyceo import prompt_pass


@manager.command
def create_user(login, passw, **data):
    """[-login] LOGIN [-passw] PASSWORD
    Creates a new user.
    """
    from bundles.users import auth
    
    password_minlen = auth.settings.password_minlen
    while len(passw) < password_minlen:
        print 'Password is too short (min %i chars).' % password_minlen
        passw = prompt_pass('>>> Password? ')

    auth.create_user(login, passw, **data)
    print 'Created user `%s` with password `%s`.' % (login, passw)
    print 'To change the password use `manage.py change_password %s`' % login
    print 'To change the email use `manage.py update_user %s email=mynew@email`' % login


@manager.command
def change_password(login, passw=None):
    """[-login] LOGIN [-passw] NEW_PASSWORD
    Changes the password of an existing user."""
    from bundles.users import auth
    
    if passw is None:
        passw = prompt_pass('>>> Password? ')
    
    password_minlen = auth.settings.password_minlen
    while len(passw) < password_minlen:
        print 'Password is too short (min %i chars).' % password_minlen
        passw = prompt_pass('>>> Password? ')

    auth.change_password(login, passw)
    print 'Changed the password of user `%s`.' % login


@manager.command
def update_user(login, **data):
    """[-login] LOGIN [key=value, ...]
    Changes the password of an existing user."""
    from main import db
    from bundles.users.models import User

    user = db.query(User).filter(User.login==login).first()
    if not user:
        print 'User `%s` not found.' % login
        return
    
    for key, val in data.items():
        setattr(user, key, val)
    db.commit()
    print 'User `%s` updated.' % login


@manager.command
def add_perms(login, *perms):
    """[-login] LOGIN [-perms] *PERMISSIONS
    Add permissions to the user
    """
    from main import db
    from bundles.users.models import User
    
    user = db.query(User).filter(User.login==login).first()
    if not user:
        print 'User `%s` not found.' % login
        return
    user.add_perms(perms)
    db.commit()
    print 'Changed the permissions of user `%s`.' % login


if __name__ == "__main__":
    manager.run()
