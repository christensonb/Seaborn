""" This will add endpoints to a connection so that the following syntax can be used
    >>> conn.endpoint.post(....)
"""
import inspect
import logging as log
import traceback
from functools import wraps

from seaborn.meta import class_name_to_instant_name
from seaborn.repr_wrapper import *
from seaborn.rest.errors import RestException
from seaborn.calling_function import function_arguments

REST_METHOD_NAMES = 'get put save delete post head option'.split()


class Endpoint(object):
    def __init__(self, connection=None):
        self.connection = connection
        if connection is not None:
            self.setup_methods()
            connection.reinstantiate_endpoints(endpoint=self)

    def setup_methods(self):
        def is_rest_method(name):
            for keyword in REST_METHOD_NAMES:
                if name.startswith(keyword): return True
            return False

        for k, v in self.__dict__.items():
            if inspect.isfunction(v) and is_rest_method(k):
                setattr(self, '_%s' % k, v)
                setattr(self, k, self.decorate_method(v))

    @property
    def path(self):
        return class_name_to_instant_name(self.__class__.__name__)

    @property
    def methods(self):
        return [k for k, v in self.__class__.__dict__.items() if getattr(v, 'rest_method', None)]

    @property
    def endpoints(self):
        return [k for k, v in self.__class__.__dict__.items() if isinstance(v, Endpoint)]

    @classmethod
    def decorate_method(cls, func):
        """
        :param func:       func to be decorated
        :return:           func that is now decorated
        """
        func_args = [arg for arg in function_arguments(func) if arg != 'self']
        method_return_types = Endpoint._parse_function_return_types_from_doc(func.__doc__)
        name = '%s.%s' % (cls.path, func.__name__)

        @wraps(func)
        def method_decorator(self, *args, **kwargs):
            kwargs.update(dict([[func_args[i], args[i]] for i in xrange(len(args))]))

            # self.test_endpoint_kwarg_types(kwargs,func_args,function_defaults) # todo implement this
            api_call = self.connection._pre_process_call(name, endpoint_params=kwargs)
            try:
                data = func(**kwargs)
            except RestException as e:
                api_call.error = e
                raise e

            except Exception as e:
                call_queue = self.connection._call_queue.get(self.connection._get_thread_id(), [])
                if api_call in call_queue:
                    call_queue.remove(api_call)
                e = RestException(original_error=e, stack=traceback.format_exc())
                log.error('ApiCall Exception: %s' % e, exc_info=True)
                raise e
            return self.connection._post_process_call(api_call, data, method_return_types)

        method_decorator.rest_method = True
        return method_decorator

    @repr_return
    def method_calls(self, tab=''):
        """
        This will return a list of the _methods with arguments and default values
        :tab str: This will tab the _calls over
        :return str:
        """
        ret = ''
        for method in self.methods:
            func = getattr(self, method)
            args, _, _, default = inspect.getargspec(func)
            default = default or []
            index = len(args) - len(default)
            args_defaults = [a for a in args[1:index]]
            for i in range(len(default)):
                args_defaults.append(args[i + index] + '=' + repr(default[i]))

            ret += '%s%s(%s)\n' % (tab, method, ', '.join(args_defaults),)
        return ret

    def __repr__(self):
        if self.connection:
            ret = "Endpoint <" + self.path + ">"
        else:
            ret = "Unconnected Endpoint <" + self.path + ">"
        if self.method_class():
            ret += " with methods: " + self.method_calls().replace('\n', ' ')
        return ret

    @repr_return
    def __str__(self):
        return "API Endpoint:: %s\n%s" % (self.path, self.__doc__.replace('\n        ', '\n'))

    @classmethod
    def _parse_function_return_types_from_doc(cls, doc):
        """
        This will extract the return type for list of lists so that the repr can display the header.
        :param doc:  str of the function doc
        :return      dict of {func.__name__:{'api_type':'type','col_name':[],'col_type':[],'repr_type':None}}
        """
        data = dict(name=None, col_types=[], col_names=[], _type=None)
        if doc:
            return_doc = __doc__.split(':return')[-1].strip()
            data['name'] = return_doc.split(':')[0]
            if data['name'].startswith('list of'):
                if data['name'].endswith('LIST'):
                    data['_type'] = 'list_list'
                    for row in return_doc.split('\n')[3:]:
                        index, col_type, col_name = row.split(None, 2)
                        assert (index == str(index))
                        data['col_types'].append(col_type)
                        data['col_names'].append(col_name.split()[0])
        return data

    @property
    @repr_return
    def api_tree(self):
        """
        This will return a string of the endpoint tree structure
        :return: str
        """
        return self.connection._create_tree(self)
