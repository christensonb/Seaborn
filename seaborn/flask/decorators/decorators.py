__author__ = 'Ben Christenson'
__date__ = "9/22/15"
# try:    from sanic.response import json
# except: import json
import json
import inspect
import ast
import traceback

from werkzeug.local import LocalProxy
from flask import request, render_template
from flask import redirect as flask_redirect
from flask_login import current_user
from functools import wraps
from datetime import datetime

from seaborn.logger import log
from seaborn.python_2_to_3 import *
from seaborn.parse_doc import parse_arg_types
from seaborn.timestamp import str_to_datetime
from seaborn.calling_function import function_defaults, function_path, function_arguments
from seaborn.rest.errors import RestException, BadRequestException, NotFoundException, GOOD_REQUEST
from seaborn.flask.models import ApiModel
from seaborn.flask.memcache import MemCache

DEBUG = True
db = None
RELATIVE_PATH = ''

LOG_API_CALLS = False
FILE_HANDLER = LOG_API_CALLS and open('api_calls.py', 'a') or None
MEMCACHE = MemCache()


def api_endpoint(auth='Anonymous', validator=None, html=None, redirect=None, add=False, commit=False, delete=False,
                 binding=None, cache=None, cache_hours=None, cache_clear=None):
    """
        This is a decorators to pull the data, form, and request args and pass it to the function
        If an argument is not optional or provided it will throw a 500
        If and argument is provided but not given it will throw a 500
    :param auth:            str of the authentication <Anonymous, User, Patron, Demo, Superuser, Admin>
    :param validator:       obj that contains validate_* functions to validate input arguments
    :param html:            str of the html file to render if the request was for html
    :param redirect:        func to redirect the output to if the request was for html
    :param add:             bool if True will add the return value to the database session
    :param commit:          bool if True will commit the database session
    :param delete:          bool if True will delete the return value to the database session
    :param binding:         bool if True will be included when making C# bindings
    :param cache:           str if set then this call will be cached with %(arg)s replaced with request arguments
    :param cache_hours:     float of the number of hours to store the cache results, default is unlimit
    :param cache_clear:     str if set will clear the cache when this endpoint is called
    :return:                func of the decorated function
    """
    redirect_url = redirect
    commit = add or delete or commit
    assert auth in ['Anonymous', 'User', 'Patron', 'Demo', 'Superuser', 'Admin'], 'Auth: %s is not valid' % auth

    def endpoint_decorator(func):
        func_args = function_arguments(func)
        args_required = func_args[:len(func_args) - len(function_defaults(func) or [])]

        if cache:
            func_args.append("bypass_cache")
            func.__doc__ = func.__doc__.replace(
                ":return:", ":param bypass_cache: bool if True then it will bypass MemCache\n    :return:")

        arg_types = DEBUG and parse_arg_types(func.__doc__ or '', is_return_included=False) or {}
        path = function_path(func)
        func_name = func.__name__

        @wraps(func)
        def decorated_function(*args, **kwargs):
            try:
                log.trace("Api Call to %s <%s>" % (path.split(RELATIVE_PATH, 1)[-1], func_name))
                if auth != 'Anonymous' and not (current_user.is_authenticated and current_user.is_auth_level(auth)):
                    return "Insufficent Authority", 401, {'Content-Type': 'application/json'}

                response_code = 200  # OK
                kwargs = get_request_kwargs(func_args, arg_types, args, kwargs)
                next_url = kwargs.pop('next_url', redirect_url)  # this is for custom redirect

                if FILE_HANDLER:
                    record_api_call(FILE_HANDLER, kwargs)

                try:
                    validate_arguments(func_args, arg_types, args_required, validator, kwargs)
                except BadRequestException as e:
                    log.error("Api Call bad_arguments %s" % e.kwargs)
                    return e.message, BadRequestException.status_code, {'Content-Type': 'application/json'}

                if 'bypass_cache' in kwargs:
                    pass

                if cache is not None:
                    html_format = 'text/html' in request.accept_mimetypes and not request.accept_mimetypes.accept_json
                    cache_key, ret = MEMCACHE.get(cache, kwargs, html_format)
                    if ret is not None:
                        return ret

                if cache_clear is not None:
                    MEMCACHE.delete(cache_clear, kwargs)

                log.trace("Api Call kwargs: %s" % str(kwargs))
                try:
                    try:
                        ret = func(**kwargs)
                    except Exception as ex:
                        raise

                    if ret is None:
                        raise NotFoundException()

                    if add:
                        assert isinstance(ret, ApiModel) or (isinstance(ret, list) and isinstance(ret[0], ApiModel)), \
                            '%s did not return an ApiModel to commit' % func.__name__
                        if isinstance(ret, (list, tuple)):
                            db.session.add_all(ret)
                        else:
                            db.session.add(ret)

                    if delete:
                        assert isinstance(ret, ApiModel) or (isinstance(ret, list) and (
                            not ret or isinstance(ret[0], ApiModel))), \
                            '%s did not return an ApiModel to commit' % func.__name__
                        if isinstance(ret, (list, tuple)):
                            for i, r in enumerate(ret):
                                ret[i] = r.serialize()
                                db.session.delete(r)
                        else:
                            serialized_ret = ret.serialize()
                            db.session.delete(ret)
                            ret = serialized_ret

                    if commit:
                        db.session.commit()

                except Exception as e:
                    db.session.rollback()
                    # db.session.close()
                    log.critical("Api Call Exception <%s> \n%s\n\n%s" % (e.__class__, e.args, traceback.format_exc()))
                    if isinstance(e, RestException):
                        return e.message, e.status_code, {'Content-Type': 'application/json'}
                    else:
                        raise

                if isinstance(ret, tuple) and len(ret) == 2 and isinstance(ret[1], int):  # error
                    raise DeprecationWarning  # these should have been raised as Rest Exceptions

                if isinstance(ret, (ApiModel, LocalProxy)):
                    ret = ret.serialize()

                if isinstance(ret, list) and ret and isinstance(ret[0], (ApiModel, LocalProxy)):
                    ret = [row.serialize() or row for row in ret]

                if 'text/html' in request.accept_mimetypes and not request.accept_mimetypes.accept_json:
                    if response_code != GOOD_REQUEST and html:
                        return render_template(html, data=kwargs, errors=ret), response_code
                    elif next_url:
                        return flask_redirect(next_url)
                    elif html:
                        ret = render_template(html, data=kwargs, errors=ret)
                        if cache is not None:
                            MEMCACHE.set(cache_key, ret, cache_hours)
                        return ret

                ret = json.dumps(ret)
                if cache is not None:
                    MEMCACHE.set(cache_key, ret, cache_hours)

                return ret, response_code, {'Content-Type': 'application/json'}

            except Exception as e:
                log.critical("Api Call Exception %s" % traceback.format_exc())
                raise

        decorated_function._html = html
        decorated_function._redirect = redirect
        decorated_function._auth = auth
        decorated_function._validator = validator
        decorated_function._undecorated = func
        decorated_function._extra_args = [] if cache is None else ["bypass_cache"]
        decorated_function._binding = binding if binding is not None else auth != "Admin"
        return decorated_function

    return endpoint_decorator


def record_api_call(file_handle, kwargs, connection='self.conn'):
    """  This will record the api calls in the form that can be then used on the client with the Connection class
    :param file_handle: file handle to an open file to write to
    :param kwargs:      dict of request parameters
    :param connection:  str of the connection preheader
    :return:            None
    """
    args = ', '.join(['%s=%s' % (k, repr(v)) for k, v in kwargs.items()])
    endpoint = request.path.replace('/', '.') + '.' + request.method.lower()
    file_handle.write('%s%s(%s)\n' % (connection, endpoint, args))
    file_handle.flush()


def register(database, debug, relative_path=''):
    """
        This will store flask global variables the decorators need
    :param database:        SQLAlchemy database object
    :param debug:           bool if debug is True
    :param relative_path:   str of the relative path for reporting api call functions
    :return:                None
    """
    global db, DEBUG, RELATIVE_PATH
    db = database
    DEBUG = debug
    RELATIVE_PATH = relative_path


def convert_string_type(v, arg_type):
    if isinstance(v, basestring):
        if v == '':
            v = None
        elif arg_type is bool:
            v = v == '1' or v == 'True'
        elif arg_type is int:
            v = int(v)
        elif arg_type is float:
            v = float(v)
        elif arg_type is datetime:
            v = str_to_datetime(v.replace(' ', '_'))
    return v


def get_request_kwargs(func_args, arg_types, args, kwargs):
    """
        This will return all of the function parameters as a dict
    :param func_args: list of str of arguments
    :param arg_types: dict of argument types as extracted from the function __doc__
    :param args:      list of arguments provided from flask
    :param kwargs:    dict of arguments provided from flask
    :return:          dict of parameters and values
    """

    kwargs.update(dict([(func_args[i], args[i]) for i in xrange(len(args))]))
    kwargs.update(request.args or {})
    kwargs.update(request.data and ast.literal_eval(request.data.decode('utf-8')) or {})
    kwargs.update(request.form or {})
    deliminator = chr(30)
    for k, v in list(kwargs.items()):
        arg_type = arg_types.get(k, basestring)

        if isinstance(arg_type, tuple) and len(arg_type) > 1 and arg_type[0] is list:
            if v and isinstance(v[0], basestring) and deliminator in v[
                0]:  # this is to fix a unity problem with sending list
                v = v[0].split(deliminator)
            v = [convert_string_type(vv, arg_type[1]) for vv in v]

        elif isinstance(v, arg_type):
            pass

        elif isinstance(v, list) and len(v) == 1:
            v = convert_string_type(v[0], arg_type)  # request.data and request.form always return a diction of list

        else:
            v = convert_string_type(v, arg_type)

        if v is not None:
            kwargs[k] = v
        else:
            kwargs.pop(k)
    kwargs.pop('\x00', None)  # unity sometimes sends this
    return kwargs


def validate_arguments(func_args, arg_types, args_required, validator, kwargs):
    """
        This will test that all required ares are present and all args of the proper type
    :param func_args:     list of str of arguments
    :param arg_types:     dict of argument types as extracted from the function __doc__
    :param args_required: list of args required
    :param validator:     custom validator class that will test functions based on have a validator_.... function
    :param kwargs:        dict of arguments provided data, request, flask, ...
    :return:              dict of errors
    """
    arg_errors = {}
    for k in kwargs:
        if k == '_status':
            pass
        if not k in func_args:
            arg_errors[k] = 'Invalid extra argument'
        elif DEBUG and not isinstance(kwargs[k], arg_types.get(k, object)):
            if arg_types[k] == float and isinstance(kwargs[k], int):
                kwargs[k] = float(kwargs[k])
            elif arg_types[k] == bool and kwargs[k] in [0, 1]:
                kwargs[k] = bool(kwargs[k])
            else:
                arg_errors[k] = 'Invalid argument type %s for arg %s' % (type(kwargs[k]), k)
        elif getattr(validator, 'validator_%s' % k, None):
            try:
                cleaned = getattr(validator, 'validator_%s' % k)(**kwargs)
                if cleaned is not None:
                    kwargs[k] = cleaned
            except Exception as e:
                arg_errors[k] = e.args

    for arg in args_required:
        if not arg in kwargs:
            arg_errors[arg] = 'Missing argument'

    if arg_errors:
        raise BadRequestException(**arg_errors)
