# -*- coding: utf-8 -*-
"""
# pyCEO

Create management scripts for your applications so you can do
things like `python manage.py runserver`.

Copyright © 2010-2011 by Lúcuma labs (http://lucumalabs.com).
MIT License. (http://www.opensource.org/licenses/mit-license.php)
"""
import getpass
import os
import re
import string
import sys


HELP_COMMANDS = ('help', 'h')


def _is_a_key(sarg):
    """Check if `sarg` is a key (eg. -foo, --foo) or a value (eg. -33).
    """
    if not sarg.startswith('-'):
        return False
    try:
        float(sarg)
        return False
    except ValueError:
        return True


def parse_args(largs_):
    """Parse the command line arguments and return a list of the positional
    arguments and a dictionary with the named ones.
        
        >>> parse_args(['abc', 'def', '-w', '3', '--foo', 'bar', '-narf=zort'])
        (['abc, 'def'], {'w': '3', 'foo': 'bar', 'narf': 'zort'})
        >>> parse_args(['-abc'])
        ([], {'abc': True})
        >>> parse_args(['-f', '1', '-f', '2', '-f', '3'])
        ([], {'f': ['1', '2', '3']})
    
    """
    # Split the 'key=arg' arguments
    largs = []
    for arg in largs_:
        if '=' in arg:
            key, arg = arg.split('=')
            largs.append(key)
        largs.append(arg)
    
    args = []
    flags = []
    kwargs = {}
    key = None
    for sarg in largs:
        if _is_a_key(sarg):
            if key is not None:
                flags.append(key)
            key = sarg.strip('-')
            continue
        
        if not key:
            args.append(sarg)
            continue
        
        value = kwargs.get(key)
        if value:
            if isinstance(value, list):
                value.append(sarg)
            else:
                value = [value, sarg]
            kwargs[key] = value
        else:
            kwargs[key] = sarg
    
    # Get the flags
    if key:
        flags.append(key)
    # An extra key whitout a value is a flag if it hasn't been used before.
    # Otherwise is a typo.
    for flag in flags:
        if not kwargs.get(flag):
            kwargs[flag] = True
    
    return args, kwargs


class Command(object):
    
    def __init__(self, func):
        self.func = func
        
        description = func.__doc__ or ''
        indent = ' ' * 6
        description = re.sub('\n\s*', '\n' + indent, description.rstrip())
        self.description = description
    
    def parse_args(self, sargs):
        args, kwargs = parse_args(sargs)
        self.func(*args, **kwargs)


class Manager(object):
    """Controller class for handling a set of commands.
    """
    
    def __init__(self):
        self.commands = {}
    
    def command(self, func):
        """Decorator to register a function as a command.
            
            @manager.command
            def hello(name, url='http://google.com'):
                print "hello", name, 'at', url
            
            >>> python manager.py hello -name Larry
            Hello Larry at http://google.com
            
            >>> python manager.py hello -name Steve -url bing.com
            Hello Steve at bing.com
            
            >>> python manager.py hello nurse "Burbank, California"
            Hello nurse at Burbank, California
            
            >>> python manager.py hello world lucumalabs.com
            Hello world at lucumalabs.com
        
        """
        self.commands[func.__name__] = Command(func)
        return func
    
    def run(self, default=None, prefix=''):
        """Parse the command line arguments.
        
        :param default:
            Name of default command to run if no arguments are passed.
        
        :param prefix:
            Prefix text
        """
        prog = sys.argv[0]
        prog = os.path.split(prog)[1]
        
        try:
            name = sys.argv[1]
            args = sys.argv[2:]
        except IndexError:
            name = default
            args = []
        
        if name is None or name.strip('-') in HELP_COMMANDS:
            print self.get_help(prog, prefix, default)
            return
        
        command = self.commands.get(name)
        
        if command is None:
            print 'Command "%s" not found' % name
            print self.get_help(prog, prefix, default)
            return
        
        command.parse_args(args)
    
    def get_help(self, prog, prefix='', default=None):
        shelp = []
        if prefix:
            shelp.append(prefix + '\n\n')
        
        shelp.extend([
            '= USAGE ', '=' * 52, '\n',
            '  %s <action> [<options>]' % prog, '\n',
            '  %s %s' % (prog, HELP_COMMANDS[0]), '\n',
            '\n',
            '= ACTIONS ', '=' * 50, '\n',
            ])
        
        for name, command in self.commands.items():
            shelp.append('\n%s %s %s\n' % (
                ' ' if name != default else '*',
                name, command.description))
        
        return ''.join(shelp)


COLORS = {
    'OKGREEN': '\033[92m',
    'WARNING': '\033[93m',
    'FAIL': '\033[91m',
    'BOLD': '\033[1m',
    'ENDC': '\033[0m',
}


def formatm(action, msg='', color='OKGREEN'):
    color = COLORS.get(color, '')
    lparts = [color, action, COLORS['ENDC'], msg]
    return ''.join(lparts)


def prompt(text, default=None, _test=None):
    """Ask a question via raw_input() and return their answer.
    
    param text: prompt text
    param default: default value if no answer is provided.
    """
    
    text += ' [%s]' % default if default else ''
    while True:
        if _test is not None:
            print text
            resp = _test
        else:
            resp = raw_input(text)
        if resp:
            return resp
        if default is not None:
            return default


def prompt_pass(text, default=None, _test=None):
    """Prompt the user for a secret (like a password) without echoing.
    
    :param name: prompt text
    :param default: default value if no answer is provided.
    """
    
    text += ' [%s]' % default if default else ''
    while True:
        if _test is not None:
            print text
            resp = _test
        else:
            resp = getpass.getpass(text)
        if resp:
            return resp
        if default is not None:
            return default


def prompt_bool(text, default=False, yes_choices=None, no_choices=None,
      _test=None):
    """Ask a yes/no question via raw_input() and return their answer.
    
    :param text: prompt text
    :param default: default value if no answer is provided.
    :param yes_choices: default 'y', 'yes', '1', 'on', 'true', 't'
    :param no_choices: default 'n', 'no', '0', 'off', 'false', 'f'
    """
    
    yes_choices = yes_choices or ('y', 'yes', 't', 'true', 'on', '1')
    no_choices = no_choices or ('n', 'no', 'f', 'false', 'off', '0')
    
    default = yes_choices[0] if default else no_choices[0]
    while True:
        if _test is not None:
            print text
            resp = _test
        else:
            resp = prompt(text, default)
        if not resp:
            return default
        resp = str(resp).lower()
        if resp in yes_choices:
            return True
        if resp in no_choices:
            return False


def prompt_choices(text, choices, default=None, resolver=string.lower,
      _test=None):
    """Ask to select a choice from a list, and return their answer.
    
    :param text: prompt text
    :param choices: list or tuple of available choices. Choices may be
        strings or (key, value) tuples.
    :param default: default value if no answer provided.
    """
    
    _choices = []
    options = []
    
    for choice in choices:
        if isinstance(choice, basestring):
            options.append(choice)
        else:
            options.append("%s [%s]" % (choice[1], choice[0]))
            choice = choice[0]
        _choices.append(choice)
    
    text += ' – (%s)' % ', '.join(options)
    while True:
        if _test is not None:
            print text
            resp = _test
        else:
            resp = prompt(text, default)
        resp = resolver(resp)
        if resp in _choices:
            return resp
        if default is not None:
            return default

