# -*- coding: utf-8 -*-
"""
    Test the shake.manager module.
    
    :Copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
    :MIT License. (http://www.opensource.org/licenses/mit-license.php)
"""
import pytest
from StringIO import StringIO
import sys

from shake.pyceo import (Manager, parse_args,
    prompt, prompt_pass, prompt_bool, prompt_choices)


def set_up_stdout():
    sys.stdout = StringIO()


def restore_stdout():
    sys.stdout = sys.__stdout__
    

def test_args():
    result = parse_args(['abc', 'xy', '-w=3', '--foo', 'bar', '-narf=zort'])
    expected = (['abc', 'xy'], {'foo': 'bar', 'w': '3', 'narf': 'zort'})
    print result
    assert result == expected


def test_args_list():
    result = parse_args(['-f', '1', '-f', '2', '-f', '3'])
    expected = ([], {'f': ['1', '2', '3']})
    print result
    assert result == expected
    
    result = parse_args(['-f', '1', '2', '3'])
    print result
    assert result == expected


def test_args_text():
    result = parse_args(['-foo', 'yes, indeed', '-bar', 'no'])
    expected = ([], {'foo': 'yes, indeed', 'bar': 'no'})
    print result
    assert result == expected


def test_single_flags():
    result = parse_args(['-abc'])
    expected = ([], {'abc': True})
    print result
    assert result == expected


def test_key_n_flag():
    result = parse_args(['-foo', 'bar', '-abc'])
    expected = ([], {'abc': True, 'foo': 'bar'})
    print result
    assert result == expected
    
    result = parse_args(['-abc', '-foo', 'bar'])
    print result
    assert result == expected


def test_pos_n_flag():
    result = parse_args(['foo', '-abc'])
    expected = (['foo'], {'abc': True})
    print result
    assert result == expected


def test_typo_flag():
    result = parse_args(['-abc', '123', '-abc'])
    expected = ([], {'abc': '123'})
    print result
    assert result == expected
    
    result = parse_args(['-abc', '-abc', '123'])
    expected = ([], {'abc': '123'})
    print result
    assert result == expected
    

def test_command_args():
    set_up_stdout()
    manager = Manager()
    
    @manager.command
    def hello(name='fred'):
        print "hello", name
    
    sys.argv = ['manage.py', 'hello', '-name=joe']
    manager.run()
    assert 'hello joe\n' == sys.stdout.getvalue()
    restore_stdout()


def test_no_command():
    set_up_stdout()
    manager = Manager()
    
    @manager.command
    def hello():
        print 'hello world'
    
    @manager.command
    def bye():
        print 'goodbye'
    
    assert 'hello' in manager.commands
    assert 'bye' in manager.commands
    
    sys.argv = ['manage.py']
    manager.run()
    assert '= USAGE =' in sys.stdout.getvalue()
    restore_stdout()


def test_default_command():
    set_up_stdout()
    manager = Manager()
    
    @manager.command
    def hello():
        print 'hello world'
    
    @manager.command
    def bye():
        print 'goodbye'
    
    assert 'hello' in manager.commands
    assert 'bye' in manager.commands
    
    sys.argv = ['manage.py']
    manager.run(default='hello')
    assert 'hello world\n' == sys.stdout.getvalue()
    
    sys.stdout = StringIO()
    sys.argv = ['manage.py']
    manager.run(default='bye')
    assert 'goodbye\n' == sys.stdout.getvalue()
    restore_stdout()


def test_command_no_args():
    set_up_stdout()
    manager = Manager()
    
    @manager.command
    def hello():
        print 'hello world'
    
    @manager.command
    def bye():
        print 'goodbye'
    
    sys.argv = ['manage.py', 'hello']
    manager.run()
    assert 'hello world\n' == sys.stdout.getvalue()
    
    sys.stdout = StringIO()
    sys.argv = ['manage.py', 'bye']
    manager.run()
    assert 'goodbye\n' == sys.stdout.getvalue()
    
    sys.stdout = StringIO()
    sys.argv = ['manage.py', 'bye']
    manager.run(default='hello')
    assert 'goodbye\n' == sys.stdout.getvalue()
    restore_stdout()


def test_command_wrong_args():
    set_up_stdout()
    manager = Manager()
    
    @manager.command
    def hello(name):
        print "hello", name
    
    @manager.command
    def kwargs(**kwargs):
        pass
    
    @manager.command
    def args(*args):
        pass
    
    @manager.command
    def dontcare(*args, **kwargs):
        pass
    
    sys.argv = ['manage.py', 'hello', '-n', 'joe']
    with pytest.raises(TypeError):
        manager.run()
    
    sys.argv = ['manage.py', 'hello', '-name', 'joe', '-foo', 'bar']
    with pytest.raises(TypeError):
        manager.run()
    
    sys.argv = ['manage.py', 'kwargs', '-n', 'joe']
    manager.run()
    
    sys.argv = ['manage.py', 'kwargs', 'joe']
    with pytest.raises(TypeError):
        manager.run()
    
    sys.argv = ['manage.py', 'args', 'joe']
    manager.run()
    
    sys.argv = ['manage.py', 'args', '-n', 'joe']
    with pytest.raises(TypeError):
        manager.run()
    
    sys.argv = ['manage.py', 'dontcare', 'joe']
    manager.run()
    
    sys.argv = ['manage.py', 'dontcare', '-n', 'joe']
    manager.run()
    restore_stdout()


def test_help():
    set_up_stdout()
    manager = Manager()
    
    @manager.command
    def hello(name):
        "Prints your name"
        pass
    
    sys.argv = ['manage.py', 'help']
    manager.run()
    assert 'Prints your name' in sys.stdout.getvalue()
    
    sys.stdout = StringIO()
    sys.argv = ['manage.py']
    manager.run()
    assert 'Prints your name' in sys.stdout.getvalue()
    restore_stdout()


def test_prompt():
    set_up_stdout()
    user_input = 'hello world'
    text = 'hello?'
    result = prompt(text, _test=user_input)
    assert result == user_input
    assert (text + '\n') == sys.stdout.getvalue()
    restore_stdout()


def test_prompt_default():
    set_up_stdout()
    user_input = ''
    text = 'hello?'
    default = 'hello world'
    result = prompt(text, default=default, _test=user_input)
    assert result == default
    assert '%s [%s]\n' % (text, default) == sys.stdout.getvalue()
    restore_stdout()


def test_prompt_pass():
    set_up_stdout()
    user_input = 'password'
    text = 'passw?'
    result = prompt_pass(text, _test=user_input)
    assert result == user_input
    assert (text + '\n') == sys.stdout.getvalue()
    restore_stdout()


def test_prompt_pass_default():
    set_up_stdout()
    user_input = ''
    text = 'passw?'
    default = 'password'
    result = prompt_pass(text, default=default, _test=user_input)
    assert result == default
    assert '%s [%s]\n' % (text, default) == sys.stdout.getvalue()
    restore_stdout()
