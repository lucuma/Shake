# -*- coding: utf-8 -*-
import pytest
from shake import routes as r
from shake import Response
from werkzeug.datastructures import ImmutableDict
from werkzeug.test import create_environ


def test_basic_routing():
    map = r.Map([
        r.Rule('/', endpoint='index'),
        r.Rule('/foo', endpoint='foo'),
        r.Rule('/bar/', endpoint='bar'),
    ])
    adapter = map.bind('example.org', '/')

    assert adapter.match('/') == ('index', {})
    assert adapter.match('/foo') == ('foo', {})
    assert adapter.match('/bar/') == ('bar', {})
    with pytest.raises(r.RequestRedirect):
        adapter.match('/bar')
    with pytest.raises(r.NotFound):
        adapter.match('/blub')

    adapter = map.bind('example.org', '/test')
    try:
        adapter.match('/bar')
    except r.RequestRedirect, e:
        assert e.new_url == 'http://example.org/test/bar/'
    else:
        assert False, 'Expected request redirect'

    adapter = map.bind('example.org', '/')
    try:
        adapter.match('/bar')
    except r.RequestRedirect, e:
        assert e.new_url == 'http://example.org/bar/'
    else:
        assert False, 'Expected request redirect'

    adapter = map.bind('example.org', '/')
    try:
        adapter.match('/bar', query_args={'aha': 'muhaha'})
    except r.RequestRedirect, e:
        assert e.new_url == 'http://example.org/bar/?aha=muhaha'
    else:
        assert False, 'Expected request redirect'

    adapter = map.bind('example.org', '/')
    try:
        adapter.match('/bar', query_args='aha=muhaha')
    except r.RequestRedirect, e:
        assert e.new_url == 'http://example.org/bar/?aha=muhaha'
    else:
        assert False, 'Expected request redirect'

    adapter = map.bind_to_environ(create_environ('/bar?foo=bar',
        'http://example.org/'))
    try:
        adapter.match()
    except r.RequestRedirect, e:
        assert e.new_url == 'http://example.org/bar/?foo=bar'
    else:
        assert False, 'Expected request redirect'


def test_raw_regex():
    map = r.Map([
        r.Rule('/(?P<num>[0-9])', endpoint='foo'),
        r.Rule('/<int:num>', endpoint='bar'),
        r.Rule('/blub/<int:num>', endpoint='blub'),
        r.Rule(r'/articles/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
            endpoint='argh')
    ])
    adapter = map.bind('example.org', '/')

    assert adapter.match('/3') == ('foo', {'num': u'3'})
    assert adapter.match('/blub/4') == ('blub', {'num': 4})
    assert adapter.match('/articles/2011/11/20/') == \
        ('argh', {'year': u'2011', 'month': u'11', 'day': u'20'})


def test_named_routes():
    map = r.Map([
        r.Rule('/foo', 'cfoo', name='foo'),
        r.Rule('/bar/', 'cbar', name='bar'),
        r.Rule('/<blob>/', 'ctest', name='test'),
    ])
    adapter = map.bind('example.com', '/')
    
    assert adapter.build('foo', {}) == '/foo'
    assert adapter.build('bar', {}) == '/bar/'
    assert adapter.build('test', {'blob': 'blub'}) == '/blub/'


def test_environ_defaults():
    environ = create_environ("/foo")
    assert environ["PATH_INFO"] == '/foo'

    m = r.Map([
        r.Rule("/foo", endpoint="foo"),
        r.Rule("/bar", endpoint="bar"),
    ])
    a = m.bind_to_environ(environ)

    assert a.match('/foo') == ('foo', {})
    assert a.match() == ('foo', {})
    assert a.match('/bar') == ('bar', {})
    with pytest.raises(r.NotFound):
        a.match('/bars')


def test_basic_building():
    map = r.Map([
        r.Rule('/', endpoint='index'),
        r.Rule('/foo', endpoint='foo'),
        r.Rule('/bar/<baz>', endpoint='bar'),
        r.Rule('/bar/<int:bazi>', endpoint='bari'),
        r.Rule('/bar/<float:bazf>', endpoint='barf'),
        r.Rule('/bar/<path:bazp>', endpoint='barp'),
        r.Rule('/hehe', endpoint='blah', subdomain='blah'),
    ])
    adapter = map.bind('example.org', '/', subdomain='blah')

    assert adapter.build('index', {}) == 'http://example.org/'
    assert adapter.build('foo', {}) == 'http://example.org/foo'
    assert adapter.build('bar', {'baz': 'blub'}) == 'http://example.org/bar/blub'
    assert adapter.build('bari', {'bazi': 50}) == 'http://example.org/bar/50'
    assert adapter.build('barf', {'bazf': 0.815}) == 'http://example.org/bar/0.815'
    assert adapter.build('barp', {'bazp': 'la/di'}) == 'http://example.org/bar/la/di'
    assert adapter.build('blah', {}) == '/hehe'
    with pytest.raises(r.BuildError):
        adapter.build('urks')

    adapter = map.bind('example.org', '/test', subdomain='blah')

    assert adapter.build('index', {}) == 'http://example.org/test/'
    assert adapter.build('foo', {}) == 'http://example.org/test/foo'
    assert adapter.build('bar', {'baz': 'blub'}) == 'http://example.org/test/bar/blub'
    assert adapter.build('bari', {'bazi': 50}) == 'http://example.org/test/bar/50'
    assert adapter.build('barf', {'bazf': 0.815}) == 'http://example.org/test/bar/0.815'
    assert adapter.build('barp', {'bazp': 'la/di'}) == 'http://example.org/test/bar/la/di'
    assert adapter.build('blah', {}) == '/test/hehe'


def test_defaults():
    map = r.Map([
        r.Rule('/foo/', defaults={'page': 1}, endpoint='foo'),
        r.Rule('/foo/<int:page>', endpoint='foo'),
    ])
    adapter = map.bind('example.org', '/')

    assert adapter.match('/foo/') == ('foo', {'page': 1})
    with pytest.raises(r.RequestRedirect):
        adapter.match('/foo/1')
    assert adapter.match('/foo/2') == ('foo', {'page': 2})
    assert adapter.build('foo', {}) == '/foo/'
    assert adapter.build('foo', {'page': 1}) == '/foo/'
    assert adapter.build('foo', {'page': 2}) == '/foo/2'


def test_greedy():
    map = r.Map([
        r.Rule('/foo', endpoint='foo'),
        r.Rule('/<path:bar>/<path:blub>', endpoint='bar'),
        r.Rule('/<path:bar>', endpoint='bar'),
    ])
    adapter = map.bind('example.org', '/')

    assert adapter.match('/foo') == ('foo', {})
    assert adapter.match('/blub') == ('bar', {'bar': 'blub'})
    assert adapter.match('/he/he') == ('bar', {'bar': 'he', 'blub': 'he'})

    assert adapter.build('foo', {}) == '/foo'
    assert adapter.build('bar', {'bar': 'blub'}) == '/blub'
    assert adapter.build('bar', {'bar': 'blub', 'blub': 'bar'}) == '/blub/bar'


def test_path():
    map = r.Map([
        r.Rule('/', defaults={'name': 'FrontPage'}, endpoint='page'),
        r.Rule('/Special', endpoint='special'),
        r.Rule('/<int:year>', endpoint='year'),
        r.Rule('/<path:name>/silly/<path:name2>/edit', endpoint='editsillypage'),
        r.Rule('/<path:name>/silly/<path:name2>', endpoint='sillypage'),
        r.Rule('/<path:name>/edit', endpoint='editpage'),
        r.Rule('/Talk:<path:name>', endpoint='talk'),
        r.Rule('/User:<username>', endpoint='user'),
        r.Rule('/User:<username>/<path:name>', endpoint='userpage'),
        r.Rule('/Files/<path:file>', endpoint='files'),
        r.Rule('/<path:name>', endpoint='page'),
    ])
    adapter = map.bind('example.org', '/')

    assert adapter.match('/') == ('page', {'name':'FrontPage'})
    with pytest.raises(r.RequestRedirect):
        adapter.match('/FrontPage')
    assert adapter.match('/Special') == ('special', {})
    assert adapter.match('/2007') == ('year', {'year':2007})
    assert adapter.match('/Some/Page') == ('page', {'name':'Some/Page'})
    assert adapter.match('/Some/Page/edit') == ('editpage', {'name':'Some/Page'})
    assert adapter.match('/Foo/silly/bar') == ('sillypage', {'name':'Foo', 'name2':'bar'})
    assert adapter.match('/Foo/silly/bar/edit') == ('editsillypage', {'name':'Foo', 'name2':'bar'})
    assert adapter.match('/Talk:Foo/Bar') == ('talk', {'name':'Foo/Bar'})
    assert adapter.match('/User:thomas') == ('user', {'username':'thomas'})
    assert adapter.match('/User:thomas/projects/werkzeug') == \
        ('userpage', {'username':'thomas', 'name':'projects/werkzeug'})
    assert adapter.match('/Files/downloads/werkzeug/0.2.zip') == \
        ('files', {'file':'downloads/werkzeug/0.2.zip'})


def test_dispatch():
    env = create_environ('/')
    map = r.Map([
        r.Rule('/', endpoint='root'),
        r.Rule('/foo/', endpoint='foo'),
    ])
    adapter = map.bind_to_environ(env)

    raise_this = None

    def view_func(endpoint, values):
        if raise_this is not None:
            raise raise_this
        return Response(repr((endpoint, values)))
    
    def dispatch(p, q=False):
        return Response.force_type(adapter.dispatch(view_func, p,
            catch_http_exceptions=q), env)

    assert dispatch('/').data == "('root', {})"
    assert dispatch('/foo').status_code == 301

    raise_this = r.NotFound

    with pytest.raises(raise_this):
        dispatch('/bar')
    assert dispatch('/bar', True).status_code == 404


def test_http_host_before_server_name():
    env = {
        'HTTP_HOST': 'wiki.example.com',
        'SERVER_NAME': 'web0.example.com',
        'SERVER_PORT': '80',
        'SCRIPT_NAME': '',
        'PATH_INFO': '',
        'REQUEST_METHOD': 'GET',
        'wsgi.url_scheme': 'http',
    }
    map = r.Map([
        r.Rule('/', endpoint='index', subdomain='wiki'),
    ])
    adapter = map.bind_to_environ(env, server_name='example.com')

    assert adapter.match('/') == ('index', {})
    assert adapter.build('index', force_external=True) == 'http://wiki.example.com/'
    assert adapter.build('index') == '/'

    env['HTTP_HOST'] = 'admin.example.com'
    adapter = map.bind_to_environ(env, server_name='example.com')

    assert adapter.build('index') == 'http://wiki.example.com/'


def test_adapter_url_parameter_sorting():
    map = r.Map([
        r.Rule('/', endpoint='index'),
    ], sort_parameters=True, sort_key=lambda x: x[1])
    adapter = map.bind('localhost', '/')

    assert adapter.build('index', {'x': 20, 'y': 10, 'z': 30},
        force_external=True) == 'http://localhost/?y=10&x=20&z=30'


def test_request_direct_charset_bug():
    map = r.Map([
        r.Rule(u'/öäü/'),
    ])
    adapter = map.bind('localhost', '/')
    try:
        adapter.match(u'/öäü')
    except r.RequestRedirect, e:
        assert e.new_url == 'http://localhost/%C3%B6%C3%A4%C3%BC/'
    else:
        assert False, 'expected request redirect exception'


def test_request_redirect_default():
    map = r.Map([
        r.Rule(u'/foo', defaults={'bar': 42}),
        r.Rule(u'/foo/<int:bar>'),
    ])
    adapter = map.bind('localhost', '/')
    try:
        adapter.match(u'/foo/42')
    except r.RequestRedirect, e:
        assert e.new_url == 'http://localhost/foo'
    else:
        assert False, 'expected request redirect exception'


def test_request_redirect_default_subdomain():
    ### Do we really want this behavior?
    map = r.Map([
        r.Rule(u'/foo', defaults={'bar': 42}, subdomain='test'),
        r.Rule(u'/foo/<int:bar>', subdomain='other'),
    ])
    adapter = map.bind('localhost', '/', subdomain='other')
    try:
        adapter.match(u'/foo/42')
    except r.RequestRedirect, e:
        assert e.new_url == 'http://test.localhost/foo'
    else:
        assert False, 'expected request redirect exception'


def test_adapter_match_return_rule():
    rule = r.Rule('/foo/', endpoint='foo')
    map = r.Map([rule])
    adapter = map.bind('localhost', '/')
    
    assert adapter.match('/foo/', return_rule=True) == (rule, {})


def test_server_name_interpolation():
    server_name = 'example.invalid'
    map = r.Map([
        r.Rule('/', endpoint='index'),
        r.Rule('/', endpoint='alt', subdomain='alt'),
    ])

    env = create_environ('/', 'http://%s/' % server_name)
    adapter = map.bind_to_environ(env, server_name=server_name)
    assert adapter.match() == ('index', {})

    env = create_environ('/', 'http://alt.%s/' % server_name)
    adapter = map.bind_to_environ(env, server_name=server_name)
    assert adapter.match() == ('alt', {})

    env = create_environ('/', 'http://%s/' % server_name)
    adapter = map.bind_to_environ(env, server_name='foo')
    assert adapter.subdomain == 'example'


def test_rule_emptying():
    rule = r.Rule('/foo', 'x', defaults={'meh': 'muh'}, methods=['POST'],
        build_only=False, subdomain='x', strict_slashes=True, redirect_to=None)
    rule2 = rule.empty()

    assert rule.__dict__ == rule2.__dict__
    
    rule.methods.add('GET')
    assert rule.__dict__ != rule2.__dict__

    rule.methods.discard('GET')
    rule.defaults['meh'] = 'aha'
    assert rule.__dict__ != rule2.__dict__


def test_rule_templates():
    testcase = r.RuleTemplate([
        r.Submount('/test/$app', [
            r.Rule('/foo/', 'handle_foo'),
            r.Rule('/bar/', 'handle_bar'),
            r.Rule('/baz/', 'handle_baz'),
        ]),
        r.EndpointPrefix('${app}', [
            r.Rule('/${app}-blah', 'bar'),
            r.Rule('/${app}-meh', 'baz'),
        ]),
        r.Subdomain('$app', [
            r.Rule('/blah', 'x_bar'),
            r.Rule('/meh', 'x_baz'),
        ]),
    ])

    url_map = r.Map([
        testcase(app='test1'),
        testcase(app='test2'),
        testcase(app='test3'),
        testcase(app='test4'),
    ])

    out = sorted([(x.rule, x.subdomain, x.endpoint)
        for x in url_map.iter_rules()])

    assert out == ([
        ('/blah', 'test1', 'x_bar'),
        ('/blah', 'test2', 'x_bar'),
        ('/blah', 'test3', 'x_bar'),
        ('/blah', 'test4', 'x_bar'),
        ('/meh', 'test1', 'x_baz'),
        ('/meh', 'test2', 'x_baz'),
        ('/meh', 'test3', 'x_baz'),
        ('/meh', 'test4', 'x_baz'),
        ('/test/test1/bar/', '', 'handle_bar'),
        ('/test/test1/baz/', '', 'handle_baz'),
        ('/test/test1/foo/', '', 'handle_foo'),
        ('/test/test2/bar/', '', 'handle_bar'),
        ('/test/test2/baz/', '', 'handle_baz'),
        ('/test/test2/foo/', '', 'handle_foo'),
        ('/test/test3/bar/', '', 'handle_bar'),
        ('/test/test3/baz/', '', 'handle_baz'),
        ('/test/test3/foo/', '', 'handle_foo'),
        ('/test/test4/bar/', '', 'handle_bar'),
        ('/test/test4/baz/', '', 'handle_baz'),
        ('/test/test4/foo/', '', 'handle_foo'),
        ('/test1-blah', '', 'test1.bar'),
        ('/test1-meh', '', 'test1.baz'),
        ('/test2-blah', '', 'test2.bar'),
        ('/test2-meh', '', 'test2.baz'),
        ('/test3-blah', '', 'test3.bar'),
        ('/test3-meh', '', 'test3.baz'),
        ('/test4-blah', '', 'test4.bar'),
        ('/test4-meh', '', 'test4.baz'),
    ])


def test_endpoint_prefix():
    url_map = r.Map([
        r.EndpointPrefix('foo', [
            r.Rule('/foo/bar', 'bar'),
        ]),
        r.EndpointPrefix('bar.', [
            r.Rule('/bar/meh', 'meh'),
        ]),
    ])
    out = [x.endpoint for x in url_map.iter_rules()]
    assert out == ['foo.bar', 'bar.meh']


def test_complex_routing_rules():
    m = r.Map([
        r.Rule('/', endpoint='index'),
        r.Rule('/<int:blub>', endpoint='an_int'),
        r.Rule('/foo/', endpoint='nested'),
        r.Rule('/foobar/', endpoint='nestedbar'),
        r.Rule('/foo/<path:testing>/edit', endpoint='nested_edit'),
        r.Rule('/foo/<path:testing>/', endpoint='nested_show'),
        r.Rule('/users/', endpoint='users', defaults={'page': 1}),
        r.Rule('/users/page/<int:page>', endpoint='users'),
        r.Rule('/foox', endpoint='foox'),
        r.Rule('/<path:bar>/<path:blub>', endpoint='barx_path_path'),
        r.Rule('/<blub>', endpoint='a_string'),
    ])
    a = m.bind('example.com')

    assert a.match('/') == ('index', {})
    assert a.match('/42') == ('an_int', {'blub': 42})
    assert a.match('/blub') == ('a_string', {'blub': 'blub'})
    assert a.match('/foo/') == ('nested', {})
    assert a.match('/foobar/') == ('nestedbar', {})
    assert a.match('/foo/1/2/3/') == ('nested_show', {'testing': '1/2/3'})
    assert a.match('/foo/1/2/3/edit') == ('nested_edit', {'testing': '1/2/3'})
    assert a.match('/users/') == ('users', {'page': 1})
    assert a.match('/users/page/2') == ('users', {'page': 2})
    assert a.match('/foox') == ('foox', {})
    assert a.match('/1/2/3') == ('barx_path_path', {'bar': '1', 'blub': '2/3'})

    assert a.build('index') == '/'
    assert a.build('an_int', {'blub': 42}) == '/42'
    assert a.build('a_string', {'blub': 'test'}) == '/test'
    assert a.build('nested') == '/foo/'
    assert a.build('nestedbar') == '/foobar/'
    assert a.build('nested_show', {'testing': '1/2/3'}) == '/foo/1/2/3/'
    assert a.build('nested_edit', {'testing': '1/2/3'}) == '/foo/1/2/3/edit'
    assert a.build('users', {'page': 1}) == '/users/'
    assert a.build('users', {'page': 2}) == '/users/page/2'
    assert a.build('foox') == '/foox'
    assert a.build('barx_path_path', {'bar': '1', 'blub': '2/3'}) == '/1/2/3'


def test_default_converters():
    class MyMap(r.Map):
        default_converters = r.Map.default_converters.copy()
        default_converters['foo'] = r.UnicodeConverter
    
    assert isinstance(r.Map.default_converters, ImmutableDict)

    m = MyMap([
        r.Rule('/a/<foo:a>', endpoint='a'),
        r.Rule('/b/<foo:b>', endpoint='b'),
        r.Rule('/c/<c>', endpoint='c'),
    ], converters={'bar': r.UnicodeConverter})
    a = m.bind('example.org', '/')

    assert a.match('/a/1') == ('a', {'a': '1'})
    assert a.match('/b/2') == ('b', {'b': '2'})
    assert a.match('/c/3') == ('c', {'c': '3'})
    assert 'foo' not in r.Map.default_converters


def test_build_append_unknown():
    map = r.Map([
        r.Rule('/bar/<float:bazf>', endpoint='barf'),
    ])
    adapter = map.bind('example.org', '/', subdomain='blah')

    assert adapter.build('barf', {'bazf': 0.815, 'bif' : 1.0}) == \
        'http://example.org/bar/0.815?bif=1.0'
    assert adapter.build('barf', {'bazf': 0.815, 'bif' : 1.0},
        append_unknown=False) == 'http://example.org/bar/0.815'


def test_method_matching_sanity():
    map = r.Map([
        r.Rule('/save/<who>/', endpoint='get', methods=['GET']),
        r.Rule('/<action>/<who>/', endpoint='post', methods=['POST']),
    ])
    adapter = map.bind('example.org', '/')

    assert adapter.match('/save/the_cheerleader/', method='GET') == \
        ('get', {'who': 'the_cheerleader'})
    assert adapter.match('/save/the_cheerleader/', method='POST') == \
        ('post', {'action': 'save', 'who': 'the_cheerleader'})


def test_method_fallback():
    map = r.Map([
        r.Rule('/', endpoint='index', methods=['GET']),
        r.Rule('/<name>', endpoint='hello_name', methods=['GET']),
        r.Rule('/select', endpoint='hello_select', methods=['POST']),
        r.Rule('/search_get', endpoint='search', methods=['GET']),
        r.Rule('/search_post', endpoint='search', methods=['POST']),
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
    url_map = r.Map([
        r.Rule('/get', methods=['GET'], endpoint='a'),
        r.Rule('/post', methods=['POST'], endpoint='b'),
    ])
    adapter = url_map.bind('example.org')

    assert adapter.match('/get', method='HEAD') == ('a', {})
    with pytest.raises(r.MethodNotAllowed):
        adapter.match('/post', method='HEAD')


def test_protocol_joining_bug():
    m = r.Map([
        r.Rule('/<foo>', endpoint='x'),
    ])
    a = m.bind('example.org')

    assert a.build('x', {'foo': 'x:y'}) == '/x:y'
    assert a.build('x', {'foo': 'x:y'}, force_external=True) == \
        'http://example.org/x:y'


def test_allowed_methods_querying():
    m = r.Map([
        r.Rule('/<foo>', methods=['GET', 'HEAD']),
        r.Rule('/foo', methods=['POST']),
    ])
    a = m.bind('example.org')

    assert sorted(a.allowed_methods('/foo')) == ['GET', 'HEAD', 'POST']


def test_external_building_with_port():
    map = r.Map([
        r.Rule('/', endpoint='index'),
    ])
    adapter = map.bind('example.org:5000', '/')
    built_url = adapter.build('index', {}, force_external=True)

    assert built_url == 'http://example.org:5000/', built_url


def test_external_building_with_port_bind_to_environ():
    map = r.Map([
        r.Rule('/', endpoint='index'),
    ])
    adapter = map.bind_to_environ(
        create_environ('/', 'http://example.org:5000/'),
        server_name="example.org:5000"
    )
    built_url = adapter.build('index', {}, force_external=True)

    assert built_url == 'http://example.org:5000/', built_url


def test_external_building_with_port_bind_to_environ_wrong_servername():
    map = r.Map([
        r.Rule('/', endpoint='index'),
    ])
    adapter = map.bind_to_environ(
        create_environ('/', 'http://localhost:5000/'),
        server_name="127.0.0.1:5000"
    )

    assert adapter.subdomain == ''


def test_external_building_with_port_bind_to_environ_wrong_port():
    map = r.Map([
        r.Rule('/', endpoint='index'),
    ])
    adapter = map.bind_to_environ(
        create_environ('/', 'http://example.org:5000/'),
        server_name="example.org"
    )

    assert adapter.subdomain == ''


def test_converter_parser():
    args, kwargs = r.parse_converter_args(u'test, a=1, b=3.0')

    assert args == ('test',)
    assert kwargs == {'a': 1, 'b': 3.0 }

    args, kwargs = r.parse_converter_args('')
    assert not args and not kwargs

    args, kwargs = r.parse_converter_args('a, b, c,')
    assert args == ('a', 'b', 'c')
    assert not kwargs

    args, kwargs = r.parse_converter_args('True, False, None')
    assert args == (True, False, None)

    args, kwargs = r.parse_converter_args('"foo", u"bar"')
    assert args == ('foo', 'bar')


def test_alias_redirects():
    m = r.Map([
        r.Rule('/', endpoint='index'),
        r.Rule('/index.html', endpoint='index', alias=True),
        r.Rule('/users/', defaults={'page': 1}, endpoint='users'),
        r.Rule('/users/index.html', defaults={'page': 1}, alias=True,
               endpoint='users'),
        r.Rule('/users/page/<int:page>', endpoint='users'),
        r.Rule('/users/page-<int:page>.html', alias=True, endpoint='users'),
    ])
    a = m.bind('example.com')

    def ensure_redirect(path, new_url, args=None):
        try:
            a.match(path, query_args=args)
        except r.RequestRedirect, e:
            assert e.new_url == 'http://example.com' + new_url
        else:
            assert False, 'expected redirect'

    ensure_redirect('/index.html', '/')
    ensure_redirect('/users/index.html', '/users/')
    ensure_redirect('/users/page-2.html', '/users/page/2')
    ensure_redirect('/users/page-1.html', '/users/')
    ensure_redirect('/users/page-1.html', '/users/?foo=bar', {'foo': 'bar'})

    assert a.build('index') == '/'
    assert a.build('users', {'page': 1}) == '/users/'
    assert a.build('users', {'page': 2}) == '/users/page/2'


def test_defaults():
    for prefix in '', '/aaa':
        m = r.Map([
            r.Rule(prefix + '/', endpoint='x',
                defaults={'foo': 1, 'bar': False}),
            r.Rule(prefix + '/<int:foo>', endpoint='x',
                defaults={'bar': False}),
            r.Rule(prefix + '/bar/', endpoint='x',
                defaults={'foo': 1, 'bar': True}),
            r.Rule(prefix + '/bar/<int:foo>', endpoint='x',
                defaults={'bar': True}),
        ])
        a = m.bind('example.com')

        assert a.match(prefix + '/') == ('x', {'foo': 1, 'bar': False})
        assert a.match(prefix + '/2') == ('x', {'foo': 2, 'bar': False})
        assert a.match(prefix + '/bar/') == ('x', {'foo': 1, 'bar': True})
        assert a.match(prefix + '/bar/2') == ('x', {'foo': 2, 'bar': True})

        assert a.build('x', {'foo': 1, 'bar': False}) == prefix + '/'
        assert a.build('x', {'foo': 2, 'bar': False}) == prefix + '/2'
        assert a.build('x', {'bar': False}) == prefix + '/'
        assert a.build('x', {'foo': 1, 'bar': True}) == prefix + '/bar/'
        assert a.build('x', {'foo': 2, 'bar': True}) == prefix + '/bar/2'
        assert a.build('x', {'bar': True}) == prefix + '/bar/'


def test_host_matching():
    m = r.Map([
        r.Rule('/', endpoint='index', host='www.<domain>'),
        r.Rule('/', endpoint='files', host='files.<domain>'),
        r.Rule('/foo/', endpoint='x', defaults={'page': 1}, host='www.<domain>'),
        r.Rule('/<int:page>', endpoint='x', host='files.<domain>'),
    ], host_matching=True)

    a = m.bind('www.example.com')
    assert a.match('/') == ('index', {'domain': 'example.com'})
    assert a.match('/foo/') == ('x', {'domain': 'example.com', 'page': 1})
    try:
        a.match('/foo')
    except r.RequestRedirect, e:
        assert e.new_url == 'http://www.example.com/foo/'
    else:
        assert False, 'expected redirect'

    a = m.bind('files.example.com')
    assert a.match('/') == ('files', {'domain': 'example.com'})
    assert a.match('/2') == ('x', {'domain': 'example.com', 'page': 2})
    try:
        a.match('/1')
    except r.RequestRedirect, e:
        assert e.new_url == 'http://www.example.com/foo/'
    else:
        assert False, 'expected redirect'


def test_server_name_casing():
    m = r.Map([
        r.Rule('/', endpoint='index', subdomain='foo'),
    ])

    env = create_environ()
    env['SERVER_NAME'] = env['HTTP_HOST'] = 'FOO.EXAMPLE.COM'
    a = m.bind_to_environ(env, server_name='example.com')
    assert a.match('/') == ('index', {})

    env = create_environ()
    env['SERVER_NAME'] = '127.0.0.1'
    env['SERVER_PORT'] = '5000'
    del env['HTTP_HOST']
    a = m.bind_to_environ(env, server_name='example.com')
    with pytest.raises(r.NotFound):
        a.match()


def test_redirect_request_exception_code():
    exc = r.RequestRedirect('http://www.google.com/')
    exc.code = 307
    env = create_environ()
    
    assert exc.get_response(env).status_code == exc.code

