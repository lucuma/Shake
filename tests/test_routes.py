# -*- coding: utf-8 -*-
"""
    :copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
    :license: BSD. See LICENSE for more details.
"""
import unittest

from werkzeug.datastructures import ImmutableDict
from werkzeug.test import create_environ

from shake import Response, BuildError, EndpointPrefix, Map, MethodNotAllowed
from shake import NotFound, RequestRedirect, Rule, RuleTemplate, Submount, Subdomain
from shake.routes import UnicodeConverter


class TestRoutes(unittest.TestCase):
    
    def test_basic_routing(self):
        """Basic URL routing"""
        map = Map([
            Rule('/', 'index'),
            Rule('/foo', 'foo'),
            Rule('/bar/', endpoint='bar')
        ])
        adapter = map.bind('example.org', '/')
        assert adapter.match('/') == ('index', {})
        assert adapter.match('/foo') == ('foo', {})
        assert adapter.match('/bar/') == ('bar', {})
        self.assertRaises(RequestRedirect, lambda: adapter.match('/bar'))
        self.assertRaises(NotFound, lambda: adapter.match('/blub'))
    
    
    def test_basic_building(self):
        """Basic URL building"""
        map = Map([
            Rule('/', 'index'),
            Rule('/foo', 'foo'),
            Rule('/bar/<baz>', 'bar'),
            Rule('/bar/<int:bazi>', 'bari'),
            Rule('/bar/<float:bazf>', 'barf'),
            Rule('/bar/<path:bazp>', 'barp'),
            Rule('/hehe', 'blah', subdomain='blah')
        ])
        adapter = map.bind('example.org', '/', subdomain='blah')

        assert adapter.build('index', {}) == 'http://example.org/'
        assert adapter.build('foo', {}) == 'http://example.org/foo'
        assert adapter.build('bar', {'baz': 'blub'}) == 'http://example.org/bar/blub'
        assert adapter.build('bari', {'bazi': 50}) == 'http://example.org/bar/50'
        assert adapter.build('barf', {'bazf': 0.815}) == 'http://example.org/bar/0.815'
        assert adapter.build('barp', {'bazp': 'la/di'}) == 'http://example.org/bar/la/di'
        assert adapter.build('blah', {}) == '/hehe'
        self.assertRaises(BuildError, lambda: adapter.build('urks'))
    
    
    def test_defaults(self):
        """URL routing defaults"""
        map = Map([
            Rule('/foo/', 'foo', defaults={'page': 1}),
            Rule('/foo/<int:page>', 'foo')
        ])
        adapter = map.bind('example.org', '/')

        assert adapter.match('/foo/') == ('foo', {'page': 1})
        self.assertRaises(RequestRedirect, lambda: adapter.match('/foo/1'))
        assert adapter.match('/foo/2') == ('foo', {'page': 2})
        assert adapter.build('foo', {}) == '/foo/'
        assert adapter.build('foo', {'page': 1}) == '/foo/'
        assert adapter.build('foo', {'page': 2}) == '/foo/2'
    
    
    def test_greedy(self):
        """URL routing greedy settings"""
        map = Map([
            Rule('/foo', 'foo'),
            Rule('/<path:bar>/<path:blub>', 'bar'),
            Rule('/<path:bar>', 'bar'),
        ])
        adapter = map.bind('example.org', '/')

        assert adapter.match('/foo') == ('foo', {})
        assert adapter.match('/blub') == ('bar', {'bar': 'blub'})
        assert adapter.match('/he/he') == ('bar', {'bar': 'he', 'blub': 'he'})

        assert adapter.build('foo', {}) == '/foo'
        assert adapter.build('bar', {'bar': 'blub'}) == '/blub'
        assert adapter.build('bar', {'bar': 'blub', 'blub': 'bar'}) == '/blub/bar'
    
    
    def test_order(self):
        """URL routing order"""
        map = Map([
            Rule('/', 'index'),
            Rule('/4', 'foo'),
            Rule('/<int:id>', 'bar'),
            Rule('/<int:id>', 'blub'),
            Rule('/3', 'foo'),
            Rule('/page', 'foo'),
            Rule('/<name>', 'bar'),
            Rule('/admin', 'blub'),
        ])
        adapter = map.bind('example.org', '/')
        assert adapter.match('/4') == ('foo', {})
        assert adapter.match('/5') == ('bar', {'id': 5})
        assert adapter.match('/3') == ('bar', {'id': 3})
        assert adapter.match('/page') == ('foo', {})
        assert adapter.match('/baz') == ('bar', {'name': 'baz'})
        assert adapter.match('/admin') == ('bar', {'name': 'admin'})
    
    
    def test_path(self):
        """URL routing path converter behavior"""
        map = Map([
            Rule('/', 'page', defaults={'name': 'FrontPage'}),
            Rule('/Special', 'special'),
            Rule('/<int:year>', 'year'),
            Rule('/<path:name>/silly/<path:name2>/edit', 'editsillypage'),
            Rule('/<path:name>/silly/<path:name2>', 'sillypage'),
            Rule('/<path:name>/edit', 'editpage'),
            Rule('/Talk:<path:name>', 'talk'),
            Rule('/User:<username>', 'user'),
            Rule('/User:<username>/<path:name>', 'userpage'),
            Rule('/Files/<path:file>', 'files'),
            Rule('/<path:name>', 'page'),
        ])
        adapter = map.bind('example.org', '/')

        assert adapter.match('/') == ('page', {'name':'FrontPage'})
        self.assertRaises(RequestRedirect, lambda: adapter.match('/FrontPage'))
        assert adapter.match('/Special') == ('special', {})
        assert adapter.match('/2007') == ('year', {'year':2007})
        assert adapter.match('/Some/Page') == ('page', {'name':'Some/Page'})
        assert adapter.match('/Some/Page/edit') == ('editpage', {'name':'Some/Page'})
        assert adapter.match('/Foo/silly/bar') == ('sillypage', {'name':'Foo', 'name2':'bar'})
        assert adapter.match('/Foo/silly/bar/edit') == ('editsillypage', {'name':'Foo', 'name2':'bar'})
        assert adapter.match('/Talk:Foo/Bar') == ('talk', {'name':'Foo/Bar'})
        assert adapter.match('/User:thomas') == ('user', {'username':'thomas'})
        assert adapter.match('/User:thomas/projects/werkzeug') == ('userpage', {'username':'thomas', 'name':'projects/werkzeug'})
        assert adapter.match('/Files/downloads/werkzeug/0.2.zip') == ('files', {'file':'downloads/werkzeug/0.2.zip'})
    
    
    def test_http_host_before_server_name(self):
        """URL routing HTTP host takes precedence before server name"""
        env = {
            'HTTP_HOST': 'wiki.example.com',
            'SERVER_NAME': 'web0.example.com',
            'SERVER_PORT': '80',
            'SCRIPT_NAME': '',
            'PATH_INFO': '',
            'REQUEST_METHOD': 'GET',
            'wsgi.url_scheme': 'http'
        }
        map = Map([Rule('/', 'index', subdomain='wiki')])
        adapter = map.bind_to_environ(env, server_name='example.com')
        assert adapter.match('/') == ('index', {})
        assert adapter.build('index', force_external=True) == 'http://wiki.example.com/'
        assert adapter.build('index') == '/'

        env['HTTP_HOST'] = 'admin.example.com'
        adapter = map.bind_to_environ(env, server_name='example.com')
        assert adapter.build('index') == 'http://wiki.example.com/'
    
    
    def test_adapter_url_parameter_sorting(self):
        """Optional adapter URL parameter sorting"""
        map = Map([Rule('/', 'index')], sort_parameters=True,
                  sort_key=lambda x: x[1])
        adapter = map.bind('localhost', '/')
        assert adapter.build('index', {'x': 20, 'y': 10, 'z': 30},
            force_external=True) == 'http://localhost/?y=10&x=20&z=30'
    
    
    def test_request_direct_charset_bug(self):
        map = Map([Rule(u'/öäü/')])
        adapter = map.bind('localhost', '/')
        try:
            adapter.match(u'/öäü')
        except RequestRedirect, e:
            print repr(e.new_url)
            assert e.new_url == 'http://localhost/%C3%B6%C3%A4%C3%BC/'
        else:
            raise AssertionError('Expected request redirect exception')
    
    
    def test_adapter_match_return_rule(self):
        """Returning the matched Rule"""
        rule = Rule('/foo/', endpoint='foo')
        map = Map([rule])
        adapter = map.bind('localhost', '/')
        assert adapter.match('/foo/', return_rule=True) == (rule, {})
    
    
    def test_server_name_interpolation(self):
        """URL routing server name interpolation."""
        server_name = 'example.invalid'
        map = Map([Rule('/', endpoint='index'),
                   Rule('/', endpoint='alt', subdomain='alt')])

        env = create_environ('/', 'http://%s/' % server_name)
        adapter = map.bind_to_environ(env, server_name=server_name)
        assert adapter.match() == ('index', {})

        env = create_environ('/', 'http://alt.%s/' % server_name)
        adapter = map.bind_to_environ(env, server_name=server_name)
        assert adapter.match() == ('alt', {})

        try:
            env = create_environ('/', 'http://%s/' % server_name)
            adapter = map.bind_to_environ(env, server_name='foo')
        except ValueError, e:
            msg = str(e)
            assert 'provided (%r)' % 'foo' in msg
            assert 'environment (%r)' % server_name in msg
        else:
            assert False, 'expected exception'
    
    
    def test_rule_emptying(self):
        """Rule emptying"""
        r = Rule('/foo', 'x', defaults={'meh': 'muh'}, methods=['POST'])
        r2 = r.empty()
        assert r.__dict__ == r2.__dict__
        r.methods.add('GET')
        assert r.__dict__ != r2.__dict__
        r.methods.discard('GET')
        r.defaults['meh'] = 'aha'
        assert r.__dict__ != r2.__dict__
    
    
    def test_rule_templates(self):
        """Rule templates"""
        testcase = RuleTemplate([
            Submount('/test/$app', [ 
                Rule('/foo/', 'handle_foo'),
                Rule('/bar/', 'handle_bar'),
                Rule('/baz/', 'handle_baz'),
                ]),
            EndpointPrefix('foo_', [ 
                Rule('/blah', 'bar'),
                Rule('/meh', 'baz'),
                ]),
            Subdomain('meh', [ 
                Rule('/blah', 'x_bar'),
                Rule('/meh', 'x_baz'),
                ]),
            ])

        url_map = Map(
            [ testcase(app='test1')
            , testcase(app='test2')
            , testcase(app='test3')
            , testcase(app='test4')
            ])

        out = [(x.rule, x.subdomain, x.endpoint)
               for x in url_map.iter_rules()]
        assert out == (
            [ ('/test/test1/foo/', '', 'handle_foo')
            , ('/test/test1/bar/', '', 'handle_bar')
            , ('/test/test1/baz/', '', 'handle_baz')
            , ('/blah', '', 'foo_bar')
            , ('/meh', '', 'foo_baz')
            , ('/blah', 'meh', 'x_bar')
            , ('/meh', 'meh', 'x_baz')
            , ('/test/test2/foo/', '', 'handle_foo')
            , ('/test/test2/bar/', '', 'handle_bar')
            , ('/test/test2/baz/', '', 'handle_baz')
            , ('/blah', '', 'foo_bar')
            , ('/meh', '', 'foo_baz')
            , ('/blah', 'meh', 'x_bar')
            , ('/meh', 'meh', 'x_baz')
            , ('/test/test3/foo/', '', 'handle_foo')
            , ('/test/test3/bar/', '', 'handle_bar')
            , ('/test/test3/baz/', '', 'handle_baz')
            , ('/blah', '', 'foo_bar')
            , ('/meh', '', 'foo_baz')
            , ('/blah', 'meh', 'x_bar')
            , ('/meh', 'meh', 'x_baz')
            , ('/test/test4/foo/', '', 'handle_foo')
            , ('/test/test4/bar/', '', 'handle_bar')
            , ('/test/test4/baz/', '', 'handle_baz')
            , ('/blah', '', 'foo_bar')
            , ('/meh', '', 'foo_baz')
            , ('/blah', 'meh', 'x_bar')
            , ('/meh', 'meh', 'x_baz') ]
        )
    
    
    def test_default_converters(self):
        class MyMap(Map):
            default_converters = Map.default_converters.copy()
            default_converters['foo'] = UnicodeConverter
        assert isinstance(Map.default_converters, ImmutableDict)
        m = MyMap([
            Rule('/a/<foo:a>', endpoint='a'),
            Rule('/b/<foo:b>', endpoint='b'),
            Rule('/c/<c>', endpoint='c')
        ], converters={'bar': UnicodeConverter})
        a = m.bind('example.org', '/')
        assert a.match('/a/1') == ('a', {'a': '1'})
        assert a.match('/b/2') == ('b', {'b': '2'})
        assert a.match('/c/3') == ('c', {'c': '3'})
        assert 'foo' not in Map.default_converters
    
    
    def test_build_append_unknown(self):
        """Test the new append_unknown feature of URL building"""
        map = Map([
            Rule('/bar/<float:bazf>', endpoint='barf')
        ])
        adapter = map.bind('example.org', '/', subdomain='blah')
        assert adapter.build('barf', {'bazf': 0.815, 'bif' : 1.0}) == \
            'http://example.org/bar/0.815?bif=1.0'
        assert adapter.build('barf', {'bazf': 0.815, 'bif' : 1.0},
            append_unknown=False) == 'http://example.org/bar/0.815'
    
    
    def test_method_fallback(self):
        """Test that building falls back to different rules"""
        map = Map([
            Rule('/', endpoint='index', methods=['GET']),
            Rule('/<name>', endpoint='hello_name', methods=['GET']),
            Rule('/select', endpoint='hello_select', methods=['POST']),
            Rule('/search_get', endpoint='search', methods=['GET']),
            Rule('/search_post', endpoint='search', methods=['POST'])
        ])
        adapter = map.bind('example.com')
        assert adapter.build('index') == '/'
        assert adapter.build('index', method='GET') == '/'
        assert adapter.build('hello_name', {'name': 'foo'}) == '/foo'
        assert adapter.build('hello_select') == '/select'
        assert adapter.build('hello_select', method='POST') == '/select'
        assert adapter.build('search') == '/search_get'
        assert adapter.build('search', method='GET') == '/search_get'
        assert adapter.build('search', method='POST') == '/search_post'
    
    
    def test_implicit_head(self):
        """Test implicit HEAD in URL rules where GET is present"""
        url_map = Map([
            Rule('/get', methods=['GET'], endpoint='a'),
            Rule('/post', methods=['POST'], endpoint='b')
        ])
        adapter = url_map.bind('example.org')
        assert adapter.match('/get', method='HEAD') == ('a', {})
        self.assertRaises(MethodNotAllowed, adapter.match, '/post', method='HEAD')
    
    
    def test_invalid_endpoint(self):
        """Test that building fails when the endpoint isn't valid."""
        self.assertRaises(ValueError, lambda: Rule('/foo/', endpoint=('a', 'b', 'c')))
        self.assertRaises(ValueError, lambda: Rule('/foo/', endpoint=['a', 'b', 'c']))
        self.assertRaises(ValueError, lambda: Rule('/foo/', endpoint=456))
        self.assertRaises(ValueError, lambda: Rule('/foo/', endpoint={'foo': 'bar'}))


if __name__ == '__main__':
    unittest.main()

