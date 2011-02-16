# -*- coding: utf-8 -*-
"""
    shakext.auth.perms
    --------------

    Permission system & Cross Site Request Forgery protection.

    This extension provides easy-to-use protection against
    `Cross Site Request Forgeries`_.  This type of attack occurs when a
    malicious web site creates a link or form button that is intended to
    perform some action on your Web site, using the credentials of a
    logged-in user who is tricked into clicking on the link in their browser.

    The first defense against CSRF attacks is to ensure that GET requests
    are side-effect free.  POST requests can then be protected by adding a
    unique value as hidden input in your forms.

    .. note::

        This is intended to use on POST requests that can only be made
        accompanied by a session cookie. Any other requests do not need to
        be protected, since the 'attacking' Web site could make those requests
        anyway.

    .. _Cross Site Request Forgeries:
        http://en.wikipedia.org/wiki/Cross-site_request_forgery

    # How to Use

    1.  In any template that uses a POST form, use the csrf_secret global
        variable inside the <form> element if the form is for an internal
        URL, e.g.:

            <form action="" method="post">
            ...
            {{ csrf_secret.input }}
            </form>

        This should *not* be done for POST forms that target external URLs,
        since that would cause the CSRF secret to be leaked, leading to a
        vulnerability.

    2.  If the corresponding view function is decorated with
        :func:`ext.perms.protected` the csrf secret will be automatically
        checked. If no csrf secret is found or its value is incorrect, the
        decorator will raise a :class:`shake.Forbidden` error.

        If you aren't using the decorator or prefer to do the check manually,
        you can disable this feature by passing a csrf=False argument to
        the decorator, and using :func:ext.auth.invalid_csrf_secret to
        validate the secret, e.g.:

            from shakext.auth import protected, invalid_csrf_secret

            @protected(csrf=False)
            def myview(request):
                if invalid_csrf_secret(request):
                    raise Forbidden()
                ...

    # AJAX

    To use the CSRF protection with AJAX calls insert the secret in
    your HTML template, as a javascript variable, and read it later
    from your script, e.g.:

        <script>
        var CSRF_TOKEN = '{{ csrf_secret.value }}';
        </script>

        ... later, in your javascript code::

        $.post('/theurl', {
            'something': something,
            ...

            '_csrf': CSRF_TOKEN
            });

    Additionally, Shake-Auth accept the CSRF token in the custom HTTP header
    X-CSRFToken, as well as in the form submission itself, for ease of use with
    popular JavaScript toolkits which allow insertion of custom headers into
    all AJAX requests.

    The following example using the jQuery JavaScript toolkit demonstrates
    this; the call to jQuery's ajaxSetup will cause all AJAX requests to send
    back the CSRF token in the custom X-CSRFTOKEN header:

        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                var isAbsoluteUrl = /^http:.*/.test(settings.url)
                    || /^https:.*/.test(settings.url);
                // Only send the token to relative URLs i.e. locally.
                if (! isAbsoluteUrl) {
                    xhr.setRequestHeader("X-CSRFToken", CSRF_TOKEN);
                }
            }
        });

    :copyright © 2010-2011 by Lúcuma labs <info@lucumalabs.com>.
    :license: BSD. See LICENSE for more details.

"""
from shake import redirect, Forbidden, url_for, get_csrf_secret


__all__ = [
    'REDIRECT_FIELD_NAME', 'protected', 'invalid_csrf_secret',
    ]

REDIRECT_FIELD_NAME = 'next'


def _login_required(request, sign_in_url=None, redirect_to=None):
    redirect_to = redirect_to or request.url
    request.session[REDIRECT_FIELD_NAME] = redirect_to
    sign_in_url = sign_in_url or url_for('auth.sign_in')
    if callable(sign_in_url):
        sign_in_url = sign_in_url(request)
    sign_in_url = sign_in_url or '/'
    return redirect(sign_in_url)


def protected(perm=None, group=None, test=None, sign_in_url=None, csrf=True):
    """Factory of decorators for limit the access to views.

    .. attribute:: perm
        permission the user must have.

    .. attribute:: test
        A function that takes the request and returns True or False.

    .. attribute:: group
        Group the user must be in.

    .. attribute:: sign_in_url
        If any required condition fail, redirect to this place.
        Override the default url_for('sign in').

    .. attribute:: csrf
        If True, the decorator will check the value of the csrf_secret
        on non-AJAX POST requests.

    """
    def real_decorator(target):
        def wrapped(request, *args, **kwargs):
            user = getattr(request, 'user', None)
            if not user:
                return _login_required(request, sign_in_url)

            no_perm = (perm is not None and
                not (hasattr(user, 'permissions') and perm in user.permissions)
                )
            no_group = (group is not None and
                not (hasattr(user, 'groups') and group in user.groups)
                )
            test_fail = (test is not None) and (not test(request))
            if no_perm or no_group or test_fail:
                return _login_required(request, sign_in_url)

            # CSRF protection
            if csrf and request.is_post and invalid_csrf_secret(request):
                raise Forbidden()

            return target(request, *args, **kwargs)
        return wrapped
    return real_decorator


def is_valid(request, csrf=True):
    if not request.user:
        return False
    # CSRF protection
    if csrf and request.is_post and invalid_csrf_secret(request):
        raise Forbidden()
    return True


def invalid_csrf_secret(request):
    valid_csrf_secret = get_csrf_secret(request)
    csrf_secret = request.values.get(
        valid_csrf_secret.name,
        request.headers.get('X-CSRFToken')
        )
    return csrf_secret != valid_csrf_secret.value
