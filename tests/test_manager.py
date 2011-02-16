# -*- coding: utf-8 -*-
"""
    Test the shake.manager module.
    
    :copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
    :license: BSD. See LICENSE for more details.
"""
from unittest import TestCase
from StringIO import StringIO
import sys

from shake.manager import (parse_args, Manager, 
    prompt, prompt_pass, prompt_bool, prompt_choices)


class TestParser(TestCase):
    
    def test_args(self):
        result = parse_args(['abc', 'xy', '-w=3', '--foo', 'bar', '-narf=zort'])
        expected = (['abc', 'xy'], {'foo': 'bar', 'w': '3', 'narf': 'zort'})
        print result
        assert result == expected
    
    def test_args_list(self):
        result = parse_args(['-f', '1', '-f', '2', '-f', '3'])
        expected = ([], {'f': ['1', '2', '3']})
        print result
        assert result == expected
        
        result = parse_args(['-f', '1', '2', '3'])
        print result
        assert result == expected
    
    def test_args_text(self):
        result = parse_args(['-foo', 'yes, indeed', '-bar', 'no'])
        expected = ([], {'foo': 'yes, indeed', 'bar': 'no'})
        print result
        assert result == expected
    
    def test_single_flags(self):
        result = parse_args(['-abc'])
        expected = ([], {'abc': True})
        print result
        assert result == expected
        
    def test_key_n_flag(self):
        result = parse_args(['-foo', 'bar', '-abc'])
        expected = ([], {'abc': True, 'foo': 'bar'})
        print result
        assert result == expected
        
        result = parse_args(['-abc', '-foo', 'bar'])
        print result
        assert result == expected
    
    def test_pos_n_flag(self):
        result = parse_args(['foo', '-abc'])
        expected = (['foo'], {'abc': True})
        print result
        assert result == expected
    
    def test_typo_flag(self):
        result = parse_args(['-abc', '123', '-abc'])
        expected = ([], {'abc': '123'})
        print result
        assert result == expected
        
        result = parse_args(['-abc', '-abc', '123'])
        expected = ([], {'abc': '123'})
        print result
        assert result == expected


class TestManager(TestCase):
    
    def setUp(self):
        sys.stdout = StringIO()
    
    def tearDown(self):
        sys.stdout = sys.__stdout__
    
    def test_command_args(self):
        manager = Manager()
        
        @manager.command
        def hello(name='fred'):
            print "hello", name
        
        sys.argv = ['manage.py', 'hello', '-name=joe']
        manager.run()
        assert 'hello joe\n' == sys.stdout.getvalue()
    
    def test_no_command(self):
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
        
    def test_default_command(self):
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
    
    def test_command_no_args(self):
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
    
    def test_command_wrong_args(self):
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
        self.assertRaises(TypeError, manager.run)
        
        sys.argv = ['manage.py', 'hello', '-name', 'joe', '-foo', 'bar']
        self.assertRaises(TypeError, manager.run)
        
        sys.argv = ['manage.py', 'kwargs', '-n', 'joe']
        manager.run()
        
        sys.argv = ['manage.py', 'kwargs', 'joe']
        self.assertRaises(TypeError, manager.run)
        
        sys.argv = ['manage.py', 'args', 'joe']
        manager.run()
        
        sys.argv = ['manage.py', 'args', '-n', 'joe']
        self.assertRaises(TypeError, manager.run)
        
        sys.argv = ['manage.py', 'dontcare', 'joe']
        manager.run()
        
        sys.argv = ['manage.py', 'dontcare', '-n', 'joe']
        manager.run()
    
    def test_help(self):
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


class TestHelpers(TestCase):
    
    def setUp(self):
        sys.stdout = StringIO()
    
    def tearDown(self):
        sys.stdout = sys.__stdout__
    
    def test_prompt(self):
        user_input = 'hello world'
        text = 'hello?'
        result = prompt(text, _test=user_input)
        assert result == user_input
        assert (text + '\n') == sys.stdout.getvalue()
    
    def test_prompt_default(self):
        user_input = ''
        text = 'hello?'
        default = 'hello world'
        result = prompt(text, default=default, _test=user_input)
        assert result == default
        assert '%s [%s]\n' % (text, default) == sys.stdout.getvalue()
    
    def test_prompt_pass(self):
        user_input = 'password'
        text = 'passw?'
        result = prompt_pass(text, _test=user_input)
        assert result == user_input
        assert (text + '\n') == sys.stdout.getvalue()
    
    def test_prompt_pass_default(self):
        user_input = ''
        text = 'passw?'
        default = 'password'
        result = prompt_pass(text, default=default, _test=user_input)
        assert result == default
        assert '%s [%s]\n' % (text, default) == sys.stdout.getvalue()

if __name__ == '__main__':
    unittest.main()
