import hmac
from hashlib import sha512
from functools import wraps
from werkzeug.local import LocalProxy
from werkzeug.security import safe_str_cmp
from werkzeug.urls import url_decode, url_encode

from flask import (_request_ctx_stack, current_app, request, session, url_for,
                   has_request_context, redirect)

from flask_login import login_fresh
from flask_login._compat import text_type, urlparse, urlunparse
from flask_login.config import COOKIE_NAME, EXEMPT_METHODS
from flask_login.signals import user_logged_in, user_logged_out, user_login_confirmed

current_user = LocalProxy(lambda: _get_user())

def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in EXEMPT_METHODS:
            return func(*args, **kwargs)
        elif current_app.config.get('LOGIN_DISABLED'):
            return func(*args, **kwargs)
        elif not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return decorated_view
    
def fresh_login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in EXEMPT_METHODS:
            return func(*args, **kwargs)
        elif current_app.config.get('LOGIN_DISABLED'):
            return func(*args, **kwargs)
        elif not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        elif not login_fresh():
            return current_app.login_manager.needs_refresh()
        return func(*args, **kwargs)
    return decorated_view
    
def anonymous_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in EXEMPT_METHODS:
            return func(*args, **kwargs)
        elif current_app.config.get('LOGIN_DISABLED'):
            return func(*args, **kwargs)
        elif current_user.is_authenticated:
            return redirect(url_for('homepage.homepage'))
        return func(*args, **kwargs)
    return decorated_view
    
def set_login_view(login_view, blueprint=None):
    '''
    Sets the login view for the app or blueprint. If a blueprint is passed,
    the login view is set for this blueprint on ``blueprint_login_views``.

    :param login_view: The user object to log in.
    :type login_view: str
    :param blueprint: The blueprint which this login view should be set on.
        Defaults to ``None``.
    :type blueprint: object
    '''

    num_login_views = len(current_app.login_manager.blueprint_login_views)
    if blueprint is not None or num_login_views != 0:

        (current_app.login_manager
            .blueprint_login_views[blueprint.name]) = login_view

        if (current_app.login_manager.login_view is not None and
                None not in current_app.login_manager.blueprint_login_views):

            (current_app.login_manager
                .blueprint_login_views[None]) = (current_app.login_manager
                                                 .login_view)

        current_app.login_manager.login_view = None
    else:
        current_app.login_manager.login_view = login_view


def _get_user():
    if has_request_context() and not hasattr(_request_ctx_stack.top, 'user'):
        current_app.login_manager._load_user()

    return getattr(_request_ctx_stack.top, 'user', None)


def _cookie_digest(payload, key=None):
    key = _secret_key(key)

    return hmac.new(key, payload.encode('utf-8'), sha512).hexdigest()


def _get_remote_addr():
    address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if address is not None:
        # An 'X-Forwarded-For' header includes a comma separated list of the
        # addresses, the first address being the actual remote address.
        address = address.encode('utf-8').split(b',')[0].strip()
    return address


def _create_identifier():
    user_agent = request.headers.get('User-Agent')
    if user_agent is not None:
        user_agent = user_agent.encode('utf-8')
    base = '{0}|{1}'.format(_get_remote_addr(), user_agent)
    if str is bytes:
        base = text_type(base, 'utf-8', errors='replace')  # pragma: no cover
    h = sha512()
    h.update(base.encode('utf8'))
    return h.hexdigest()


def _user_context_processor():
    return dict(current_user=_get_user())


def _secret_key(key=None):
    if key is None:
        key = current_app.config['SECRET_KEY']

    if isinstance(key, text_type):  # pragma: no cover
        key = key.encode('latin1')  # ensure bytes

    return key