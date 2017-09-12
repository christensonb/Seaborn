""" This module is used to subclass flask blueprints so as to store the information
    about the routes.  One of the uses of this information is to make python and unity bindings
"""
__author__ = 'Ben Christenson'
__date__ = "10/12/15"
from flask import Blueprint
from functools import wraps
from seaborn.calling_function import function_defaults, function_path, function_arguments


class EndpointFunction(object):
    TEST_PARAM_DOC = True

    def __init__(self, func, url, methods):
        self.is_decorated = bool(getattr(func, '_undecorated', None))
        extra_args = []
        if self.is_decorated:
            self.auth = getattr(func, '_auth', '')
            self.redirect = getattr(func, '_redirect', '')
            self.html = getattr(func, '_html', '')
            self.validator = getattr(func, '_validator', '')
            self.binding = getattr(func, '_binding', True)
            extra_args = getattr(func, '_extra_args', [])
            func = getattr(func, '_undecorated', func)

        self.args = function_arguments(func) + extra_args
        self.url = url
        self.filename = function_path(func)
        self.methods = methods
        self.func = func
        self.func_name = func.__name__
        self.doc = func.__doc__ or ''
        _defaults = list(function_defaults(func)) + [None] * len(extra_args)
        offset = len(self.args) - len(_defaults)
        self.arg_defaults = dict([(self.args[i + offset], _defaults[i]) for i in range(len(_defaults))])
        if not self.TEST_PARAM_DOC:
            return

        try:
            assert self.doc.split(':return:')[-1].split()[0]
        except:
            raise Exception('%s %s is missing doc for return type' % (url, methods))

        for a in self.args:
            try:
                assert ':param %s:' % a in self.doc, 'Missing Doc for Parameter %s in Function %s' % (a, self.func_name)
            except Exception as e:
                raise

    def __repr__(self):
        return 'EndpointFunction <%s [%s]>' % (self.url, ', '.join(self.methods))


class ProxyEndpoint(object):
    def __init__(self, path=None, parent=None):
        """
            This is an empty object that will be dynamically overloaded with routed methods
        :param path:   list of str of the current path
        :param parent: obj of the parent that this object is attached to
        :return:
        """
        self.path = path and '.'.join(path) or ''
        if parent:
            setattr(parent, path[-1], self)

    def __str__(self):
        return self.path

    def __repr__(self):
        return str(self)


class BlueprintBinding(Blueprint):
    """ This will subclass the Flask Blueprint class to record information about function routes """

    reroute_put_to_post = True  # if True all put methods will also be routed to sub_url+/put for the post method
    # this is because www doesn't have put

    reroute_all_to_get = False  # if True all put, post, delete methods will also be routed to sub_url+/put for the get
    # this is to make performing put in chrome easier

    unity_library = "WWW"  # if using WWW then unity put bindings will be routed to post

    # this is because www library doesn't allow put

    @classmethod
    def configuration(cls, reroute_put_to_post, reroute_all_to_get, unity_library):
        """
            This will allow you to set configuration for all Blueprint Bindings
        :param reroute_put_to_post: bool if True will add additional routing of put methods to post
        :param reroute_all_to_get:  bool if True will add additional routing of put, post, delete methods to get
        :param unity_library:       str of the library when instantiating unity bindings
        :return:                    None
        """
        cls.reroute_put_to_post = reroute_put_to_post
        cls.reroute_all_to_get = reroute_all_to_get
        cls.unity_library = unity_library

    def __init__(self, *args, **kwargs):
        self.endpoints = []
        super(BlueprintBinding, self).__init__(*args, **kwargs)

    def route(self, *args, **kwargs):
        """
            This will record the functions and routes of the blueprints for the sake of
            making auto doc features.
        :param args:    list of args for the route
        :param kwargs:  dict of keyword arguments for route
        :return:        return func for decorating
        """
        args = list(args)
        rule = args and args.pop(0) or kwargs.pop('rule')
        methods = len(args) > 1 and args[2] or kwargs.get('methods', ['Get'])
        methods = [method.upper() for method in methods]
        real_route_decorator = super(BlueprintBinding, self).route(rule, *args, **kwargs)
        if '<' in rule:
            rule = rule.replace('<', '').replace('>', '')
            backup_route_decorator = super(BlueprintBinding, self).route(rule, *args[1:], **kwargs)
        else:
            backup_route_decorator = None

        @wraps(real_route_decorator)
        def seaborn_route_decorator(func):
            if not (rule.endswith('/post') or rule.endswith('/put' or rule.endswith('/delete'))):
                self.endpoints.append(EndpointFunction(func, rule[1:], methods))

                reroute_kwargs = dict([k, v] for k, v in kwargs.items() if k != 'methods')
                if 'PUT' in methods and self.reroute_put_to_post:
                    reroute = super(BlueprintBinding, self).route(rule + '/put', *args[1:],
                                                                  methods=['POST'], **reroute_kwargs)
                    func = reroute(func)

                for method_ in ['PUT', 'POST', 'DELETE']:
                    if self.reroute_all_to_get and method_ in methods:
                        reroute = super(BlueprintBinding, self).route(rule + '/' + method_.lower(), *args[1:],
                                                                      methods=['GET'], **reroute_kwargs)
                        func = reroute(func)

            if backup_route_decorator:
                func = backup_route_decorator(func)

            return real_route_decorator(func)

        return seaborn_route_decorator

    def __repr__(self):
        name = self.endpoints and self.endpoints[0].filename.split('/endpoints/')[-1].split('/views.py')[0] or ''
        return 'BlueprintOption <%s %s>' % (name, len(self.endpoints))

    def add_proxy_route(self, obj, undecoratored=True):
        """
            This will add objects to  obj to the url substituting / for . and append with the method
            Example:
                /test/array/int could be accessed with
                obj.test.array.int.post
        :param obj:           obj to add the hierarchy too
        :param undecorated:   bool if True will add connection to the undecorated function
        :return:              None
        """
        for endpoint in self.endpoints:
            obj_end = obj
            url = endpoint.url or 'index'
            path = []
            for word in url.split('/'):
                path.append(word)
                if getattr(obj_end, word, None) is None:
                    setattr(obj_end, word, ProxyEndpoint(path, obj_end))
                obj_end = getattr(obj_end, word)

            for method in endpoint.methods:
                if undecoratored:
                    obj_end.__dict__[method.lower()] = endpoint.func
                else:
                    obj_end.__dict__[method.lower()] = endpoint.func._undecorated
