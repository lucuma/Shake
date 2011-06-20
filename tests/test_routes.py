# -*- coding: utf-8 -*-
"""
    :copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
    :license: BSD. See LICENSE for more details.
"""
import pytest
from werkzeug.datastructures import ImmutableDict
from werkzeug.test import create_environ

from shake import (Response, BuildError, EndpointPrefix, Map, MethodNotAllowed,
    NotFound, RequestRedirect, Rule, RuleTemplate, Submount, Subdomain)
from shake.routes import UnicodeConverter


def test_basic_routing():
    """Basic URL routing"""
    map = Map([
        Rule('/', 'index'),
        Rule('/foo', 'cfoo'),
        Rule('/bar/', 'cbar'),
        ])
    adapter = map.bind('example.com', '/')
    assert adapter.match('/') == ('index', {})
    assert adapter.match('/foo') == ('cfoo', {})
    assert adapter.match('/bar/') == ('cbar', {})
    with pytest.raises(RequestRedirect):
        adapter.match('/bar')
    with pytest.raises(NotFound):
        adapter.match('/blub')

    adapter = map.bind('example.com', '/test')
    try:
        adapter.match('/bar')
    except RequestRedirect, e:
        print e.new_url
        assert e.new_url == 'http://example.com/test/bar/'
    else:
        assert False

    adapter = map.bind('example.com', '/')
    try:
        adapter.match('/bar')
    except RequestRedirect, e:
        print e.new_url
        assert e.new_url == 'http://example.com/bar/'
    else:
        assert False

    adapter = map.bind('example.com', '/')
    try:
        adapter.match('/bar', query_args={'aha': 'muhaha'})
    except RequestRedirect, e:
        print e.new_url
        assert e.new_url == 'http://example.com/bar/?aha=muhaha'
    else:
        assert False


def test_named_routes():
    map = Map([
        Rule('/foo', 'cfoo', name='foo'),
        Rule('/bar/', 'cbar', name='bar'),
        Rule('/<name>/', 'ctest', name='test'),
        ])
    adapter = map.bind('example.com', '/')

    assert adapter.build('foo', {}) == '/foo'
    assert adapter.build('bar', {}) == '/bar/'
    assert adapter.build('test', {'name': 'blub'}) == '/blub/'


def test_environ_defaults():
    environ = create_environ('/foo')
    assert environ['PATH_INFO'] == '/foo'

    m = Map([Rule('/foo', 'foo'), Rule('/bar', 'bar')])
    a = m.bind_to_environ(environ)
    assert a.match('/foo') == ('foo', {})
    assert a.match() == ('foo', {})
    assert a.match('/bar') == ('bar', {})
    with pytest.raises(NotFound):
        a.match('/bars')


def test_basic_building():
    """Basic URL building"""
    map = Map([
        Rule('/', 'index'),
        Rule('/foo', 'foo'),
        Rule('/bar/<baz>', 'bar'),
        Rule('/bar/<int:bazi>', 'bari'),
        Rule('/bar/<float:bazf>', 'barf'),
        Rule('/bar/<path:bazp>', 'barp'),
        Rule('/hehe', 'blah', subdomain='blah'),
        ])
    adapter = map.bind('example.com', '/', subdomain='blah')

    assert adapter.build('index', {}) == 'http://example.com/'
    assert adapter.build('foo', {}) == 'http://example.com/foo'
    assert adapter.build('bar', {'baz': 'blub'}) == 'http://example.com/bar/blub'
    assert adapter.build('bari', {'bazi': 50}) == 'http://example.com/bar/50'
    assert adapter.build('barf', {'bazf': 0.815}) == 'http://example.com/bar/0.815'
    assert adapter.build('barp', {'bazp': 'la/di'}) == 'http://example.com/bar/la/di'
    assert adapter.build('blah', {}) == '/hehe'
    with pytest.raises(BuildError):
        adapter.build('urks')

    adapter = map.bind('example.com', '/test', subdomain='blah')
    assert adapter.build('index', {}) == 'http://example.com/test/'
    assert adapter.build('foo', {}) == 'http://example.com/test/foo'
    assert adapter.build('bar', {'baz': 'blub'}) == 'http://example.com/test/bar/blub'
    assert adapter.build('bari', {'bazi': 50}) == 'http://example.com/test/bar/50'
    assert adapter.build('barf', {'bazf': 0.815}) == 'http://example.com/test/bar/0.815'
    assert adapter.build('barp', {'bazp': 'la/di'}) == 'http://example.com/test/bar/la/di'
    assert adapter.build('blah', {}) == '/test/hehe'


def test_defaults():
    """URL routing defaults"""
    map = Map([
        Rule('/foo/', 'foo', defaults={'page': 1}),
        Rule('/foo/<int:page>', 'foo')
    ])
    adapter = map.bind('example.com', '/')

    assert adapter.match('/foo/') == ('foo', {'page': 1})
    with pytest.raises(RequestRedirect):
        adapter.match('/foo/1')
    assert adapter.match('/foo/2') == ('foo', {'page': 2})
    assert adapter.build('foo', {}) == '/foo/'
    assert adapter.build('foo', {'page': 1}) == '/foo/'
    assert adapter.build('foo', {'page': 2}) == '/foo/2'


def test_path():
    """URL routing path converter behavior"""
    map = Map([
        Rule('/', 'page', defaults={'name': 'FrontPage'}),
        Rule('/Special', 'special'),
        Rule('/<int:year>', 'year'),
        Rule('/<path:name>', 'page'),
        Rule('/<path:name>/edit', 'editpage'),
        Rule('/<path:name>/silly/<path:name2>', 'sillypage'),
        Rule('/<path:name>/silly/<path:name2>/edit', 'editsillypage'),
        Rule('/<path:name>/do/<action>', 'action'),
        Rule('/Talk:<path:name>', 'talk'),
        Rule('/User:<username>', 'user'),
        Rule('/User:<username>/<path:name>', 'userpage'),
        Rule('/Files/<path:file>', 'files'),
        ])
    adapter = map.bind('example.com', '/')

    assert adapter.match('/') == ('page', {'name':'FrontPage'})
    with pytest.raises(RequestRedirect):
        adapter.match('/FrontPage')
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


def test_dispatch():
    """URL routing dispatch helper"""
    env = create_environ('/')
    map = Map([
        Rule('/', 'root'),
        Rule('/foo/', 'foo')
    ])
    adapter = map.bind_to_environ(env)

    raise_this = None
    def control_func(endpoint, values):
        if raise_this is not None:
            raise raise_this
        return Response(repr((endpoint, values)))
    dispatch = lambda p, q=False: Response.force_type(adapter.dispatch(control_func, p,
        catch_http_exceptions=q), env)

    assert dispatch('/').data == "('root', {})"
    assert dispatch('/foo').status_code == 301
    raise_this = NotFound()
    with pytest.raises(NotFound):
        dispatch('/bar')
    assert dispatch('/bar', True).status_code == 404


def test_http_host_before_server_name():
    """URL routing HTTP host takes precedence before server name"""
    env = {
        'HTTP_HOST':            'wiki.example.com',
        'SERVER_NAME':          'web0.example.com',
        'SERVER_PORT':          '80',
        'SCRIPT_NAME':          '',
        'PATH_INFO':            '',
        'REQUEST_METHOD':       'GET',
        'wsgi.url_scheme':      'http'
    }
    map = Map([Rule('/', 'index', subdomain='wiki')])
    adapter = map.bind_to_environ(env, server_name='example.com')
    assert adapter.match('/') == ('index', {})
    assert adapter.build('index', force_external=True) == 'http://wiki.example.com/'
    assert adapter.build('index') == '/'

    env['HTTP_HOST'] = 'admin.example.com'
    adapter = map.bind_to_environ(env, server_name='example.com')
    assert adapter.build('index') == 'http://wiki.example.com/'


def test_adapter_url_parameter_sorting():
    """Optional adapter URL parameter sorting"""
    map = Map([Rule('/', 'index')], sort_parameters=True,
              sort_key=lambda x: x[1])
    adapter = map.bind('localhost', '/')
    assert adapter.build('index', {'x': 20, 'y': 10, 'z': 30},
        force_external=True) == 'http://localhost/?y=10&x=20&z=30'


def test_request_direct_charset_bug():
    map = Map([Rule(u'/öäü/')])
    adapter = map.bind('localhost', '/')
    try:
        adapter.match(u'/öäü')
    except RequestRedirect, e:
        assert e.new_url == 'http://localhost/%C3%B6%C3%A4%C3%BC/'
    else:
        raise AssertionError('expected request redirect exception')


def test_request_redirect_default():
    map = Map([
        Rule(u'/foo', defaults={'bar': 42}),
        Rule(u'/foo/<int:bar>'),
        ])
    adapter = map.bind('localhost', '/')
    try:
        adapter.match(u'/foo/42')
    except RequestRedirect, e:
        assert e.new_url == 'http://localhost/foo'
    else:
        raise AssertionError('expected request redirect exception')


def test_request_redirect_default_subdomain():
    map = Map([
        Rule(u'/foo', defaults={'bar': 42}, subdomain='test'),
        Rule(u'/foo/<int:bar>', subdomain='other'),
        ])
    adapter = map.bind('localhost', '/', subdomain='other')
    try:
        adapter.match(u'/foo/42')
    except RequestRedirect, e:
        assert e.new_url == 'http://test.localhost/foo'
    else:
        raise AssertionError('expected request redirect exception')


def test_adapter_match_return_rule():
    """Returning the matched Rule"""
    rule = Rule('/foo/', 'foo')
    map = Map([rule])
    adapter = map.bind('localhost', '/')
    assert adapter.match('/foo/', return_rule=True) == (rule, {})


def test_server_name_interpolation():
    """URL routing server name interpolation."""
    server_name = 'example.invalid'
    map = Map([
        Rule('/', 'index'),
        Rule('/', 'alt', subdomain='alt'),
        ])
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


def test_rule_emptying():
    """Rule emptying"""
    r = Rule('/foo', 'x', defaults={'meh': 'muh'}, methods=['POST'],
             build_only=False, subdomain='x', strict_slashes=True,
             redirect_to=None, name=None)
    r2 = r.empty()
    assert r.__dict__ == r2.__dict__
    r.methods.add('GET')
    assert r.__dict__ != r2.__dict__
    r.methods.discard('GET')
    r.defaults['meh'] = 'aha'
    assert r.__dict__ != r2.__dict__


def test_rule_templates():
    """Rule templates"""
    testcase = RuleTemplate(
        [ Submount('/test/$app',
          [ Rule('/foo/', 'handle_foo')
          , Rule('/bar/', 'handle_bar')
          , Rule('/baz/', 'handle_baz')
          ]),
          EndpointPrefix('foo_',
          [ Rule('/blah', 'bar')
          , Rule('/meh', 'baz')
          ]),
          Subdomain('meh',
          [ Rule('/blah', 'x_bar')
          , Rule('/meh', 'x_baz')
          ])
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


def test_default_converters():
    class MyMap(Map):
        default_converters = Map.default_converters.copy()
        default_converters['foo'] = UnicodeConverter
    assert isinstance(Map.default_converters, ImmutableDict)
    m = MyMap([
        Rule('/a/<foo:a>', 'a'),
        Rule('/b/<foo:b>', 'b'),
        Rule('/c/<c>', 'c')
        ], converters={'bar': UnicodeConverter})
    a = m.bind('example.com', '/')
    assert a.match('/a/1') == ('a', {'a': '1'})
    assert a.match('/b/2') == ('b', {'b': '2'})
    assert a.match('/c/3') == ('c', {'c': '3'})
    assert 'foo' not in Map.default_converters


def test_build_append_unknown():
    """Test the new append_unknown feature of URL building"""
    map = Map([
        Rule('/bar/<float:bazf>', 'barf'),
        ])
    adapter = map.bind('example.com', '/', subdomain='blah')
    assert adapter.build('barf', {'bazf': 0.815, 'bif' : 1.0}) == \
        'http://example.com/bar/0.815?bif=1.0'
    assert adapter.build('barf', {'bazf': 0.815, 'bif' : 1.0},
        append_unknown=False) == 'http://example.com/bar/0.815'


def test_method_fallback():
    """Test that building falls back to different rules"""
    map = Map([
        Rule('/', 'index', methods=['GET']),
        Rule('/<name>', 'hello_name', methods=['GET']),
        Rule('/select', 'hello_select', methods=['POST']),
        Rule('/search_get', 'search', methods=['GET']),
        Rule('/search_post', 'search', methods=['POST']),
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


def test_implicit_head():
    """Test implicit HEAD in URL rules where GET is present"""
    url_map = Map([
        Rule('/get', 'a', methods=['GET']),
        Rule('/post', 'b', methods=['POST']),
        ])
    adapter = url_map.bind('example.com')
    assert adapter.match('/get', method='HEAD') == ('a', {})
    with pytest.raises(MethodNotAllowed):
        adapter.match('/post', method='HEAD')


def test_protocol_joining_bug():
    """Make sure the protocol joining bug is fixed"""
    m = Map([Rule('/<foo>', 'x')])
    a = m.bind('example.com')
    assert a.build('x', {'foo': 'x:y'}) == '/x:y'
    assert a.build('x', {'foo': 'x:y'}, force_external=True) == 'http://example.com/x:y'


def test_allowed_methods_querying():
    """Make sure it's possible to test for allowed methods"""
    m = Map([
        Rule('/<foo>', methods=['GET']),
        Rule('/foo', methods=['POST']),
        ])
    a = m.bind('example.com')
    assert sorted(a.allowed_methods('/foo')) == ['GET', 'HEAD', 'POST']


def test_external_building_with_port():
    """Test external URL building with port number"""
    map = Map([
        Rule('/', 'index'),
        ])
    adapter = map.bind('example.com:5000', '/')
    built_url = adapter.build('index', {}, force_external=True)
    assert built_url == 'http://example.com:5000/', built_url


def test_external_building_with_port_bind_to_environ():
    """Test external URL building with port number (map.bind_to_environ)"""
    map = Map([
        Rule('/', 'index'),
        ])
    adapter = map.bind_to_environ(
        create_environ('/', 'http://example.com:5000/'),
        server_name="example.com:5000"
    )
    built_url = adapter.build('index', {}, force_external=True)
    assert built_url == 'http://example.com:5000/', built_url


def test_invalid_endpoint():
    """Test that building fails when the endpoint isn't valid."""
    with pytest.raises(ValueError):
        Rule('/foo/', ('a', 'b'))
    with pytest.raises(ValueError):
        Rule('/foo/', [])
    with pytest.raises(ValueError):
        Rule('/foo/', 42)
    with pytest.raises(ValueError):
        Rule('/foo/', {'foo': 'bar'})

