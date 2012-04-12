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
    from users import auth
    
    password_minlen = auth.settings.password_minlen
    while len(passw) < password_minlen:
        print 'Password is too short (min %i chars).' % password_minlen
        passw = prompt_pass('>>> Password? ')

    auth.create_user(login, passw, **data)
    print 'Created user `%s` with password `%s`.' % (login, passw)
    print 'To change the password use `manage.py change_password %s`' % login


@manager.command
def change_password(login, passw=None):
    """[-login] LOGIN [-passw] NEW_PASSWORD
    Changes the password of an existing user."""
    from users import auth
    
    if passw is None:
        passw = prompt_pass('>>> Password? ')
    
    password_minlen = auth.settings.password_minlen
    while len(passw) < password_minlen:
        print 'Password is too short (min %i chars).' % password_minlen
        passw = prompt_pass('>>> Password? ')

    auth.change_password(login, passw)
    print 'Changed the password of user `%s`.' % login


@manager.command
def add_perms(login, *perms):
    """[-login] LOGIN [-perms] *PERMISSIONS
    Add permissions to the user
    """
    from main import db
    from users.models import User
    
    user = db.query(User).filter(User.login==login).first()
    if not user:
        raise ValueError(login)
    user.add_perms(perms)
    db.commit()
    print 'Changed the permissions of user `%s`.' % login


if __name__ == "__main__":
    manager.run()
