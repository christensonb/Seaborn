""" This will make the python bindings using the seaborn rest module's connection and endpoint classes.
    It assumes that a list of seaborn blueprints will be passed in with route information.
"""
__author__ = 'Ben Christenson'
__date__ = "10/19/15"
import os
from seaborn.file import clear_path, mkdir
from seaborn.meta import class_name_to_instant_name, url_name_to_class_name, create_init_files
from seaborn.sorters import by_attribute, by_longest_then_by_abc, by_key, by_shortest_then_by_abc


def create_python_blueprint_bindings(path, blue_prints, models, file_start='endpoints/', file_end='/views.py',
                                     clear=True, only_decorated=True, namespace=''):
    """
    :param path:           str of the full path to save the connection endpoint
    :param blue_prints:    list of BlueprintBinding instances with endpoints
    :param models:         list of models that could be referenced in the return doc
    :param file_start:     str of keyword to split the filename on to get the relative path to start from
    :param file_end:       str of keyword to split the filename on to get the relative path to end at
    :param clear:          bool if True will clear the folder first
    :param only_decorated: bool if True will filter out routes that are not decorated with seaborn flask decorator
    :param namespace:      str of the name space to prepend the resource path
    :return:               None
    """
    assert namespace == '', "Create Python Blueprint Bindings' support for root_namespace doesn't exist yet"

    def clean_file(filename):
        return filename.replace('\\', '/').split(file_start)[-1].split(file_end)[0].replace('/', '_')

    if clear and os.path.exists(path):
        clear_path(path)

    mkdir(path)
    member_endpoints = {}  # keyed on the url of class to instantiate the value
    module_endpoints = dict([(clean_file(blue_print.endpoints[0].filename), blue_print.endpoints)
                             for blue_print in blue_prints if getattr(blue_print, 'endpoints', [])])

    endpoint_modules = sorted(module_endpoints.keys(), key=by_longest_then_by_abc)
    for module in endpoint_modules:
        url = None
        endpoints = sorted(module_endpoints[module], key=by_attribute('url', comp=by_longest_then_by_abc))
        for endpoint in endpoints:
            if only_decorated and not endpoint.is_decorated:
                continue
            if url is None:
                fn = create_endpoint(path, module, member_endpoints)

            if url != endpoint.url:
                url = endpoint.url
                for child_module in sorted(member_endpoints, key=by_longest_then_by_abc):
                    if child_module.startswith(url) and child_module != url:
                        # then there is a middle generation without endpoints
                        add_endpoint(fn, child_module, member_endpoints)
                add_endpoint(fn, url, member_endpoints)

            for method in endpoint.methods:
                fn.write(add_endpoint_method(url, method, endpoint.args, endpoint.arg_defaults, endpoint.doc))

        if module in member_endpoints and url is not None:
            add_endpoint(fn, module, member_endpoints)

    create_connection(path, endpoint_modules, member_endpoints)


def create_endpoint(path, module, member_endpoints):
    filename = '%s/%s.py' % (path, module)
    fn = open(filename, 'w')
    for child in member_endpoints.get(module.replace('_', '/'), []):
        if os.path.exists('%s/%s.py' % (path, child.replace('/', '_'))):
            fn.write('from .%s import *\n' % child.replace('/', '_'))
    fn.write('from seaborn.rest.intellisense import *\n')
    return fn


def add_endpoint_method(url, method, args, arg_defaults, func_desc):
    """
        This will add the get, put, post, delete function for the endpoint method
        :param url:          str of the url of the endpoint
        :param method:       str of get, put, post, or delete
        :param args:         list of str of arg
        :param arg_defaults: dict of arg default values
        :param func_desc:    str of the function description from the server doc
        :return:             str of the method function
    """
    tab = len(args) < 3 and ', ' or (',\n' + ' ' * (32 + len(method)))
    tab2 = tab + '          '
    method = method.lower()
    ret = '\n    def %s(%s' % (method, 'self')

    if url == 'pnp/game/board':
        pass

    for arg in args:
        arg_par = arg in arg_defaults and '%s=%s' % (arg, repr(arg_defaults[arg])) or arg
        if len((ret + ', ' + arg_par).split('\n')[-1]) > 120:
            ret += ',\n' + ' ' * (9 + len(method)) + arg_par
        else:
            ret += ', ' + arg_par

    ret += '):\n        """%s"""\n' % func_desc.replace('\n', '\n    ')
    ret += '        return self.connection.%s(' % method

    if method.lower() in ['get', 'delete']:
        ret += '%s)\n' % (tab.join(["'%s'" % url] + ['%s=%s' % (arg, arg) for arg in args]))
    elif args:
        ret += '%s%sdata=dict(%s))\n' % ("'%s'" % url, tab, tab2.join(['%s=%s' % (arg, arg) for arg in args]))
    else:
        ret += "'%s')\n" % url
    return ret


def create_connection(path, modules, member_endpoints):
    """
        This will write the __init__.py file and the connection module
    :param path:             str of where to put the files
    :param modules:          list of str of modules to import from
    :param member_endpoints: dict of list of classes to instantiate into the class endpoints and connection
    :return:                 None
    """
    fn = open('%s/connection.py' % path, 'w')
    fn.write('from seaborn.rest.intellisense import *\n')
    last = '__init__'
    for v in sorted(modules):
        if os.path.exists('%s/%s.py' % (path, v)) and not v.startswith(last):
            fn.write('from .%s import *\n' % v)
            last = v

    for module in sorted(member_endpoints.keys(), key=by_longest_then_by_abc)[:-1]:
        add_endpoint(fn, module, member_endpoints)

    fn.write('\n\nclass Connection(ConnectionEndpoint):\n')
    for member in member_endpoints['']:
        fn.write('    %s = %s()\n' % (member.split('/')[-1], url_name_to_class_name(member)))
    open('%s/__init__.py' % path, 'w').write('from .connection import *')


def add_endpoint(fn, url, member_endpoints):
    """
        This will add an endpoint class for a given url
        :param fn:               file pointer to write to
        :param url:              str of the endpoint to create
        :param member_endpoints: dict of parent endpoint and with a value of a list of child endpoints
        :return                  None
    """
    url = url or 'index'
    for member in sorted(list(member_endpoints.keys())):
        if member.startswith(url) and member != url:  # I am an orphan child that needs to be created
            add_endpoint(fn, member, member_endpoints)

    fn.write('\n\nclass %s(Endpoint):\n' % url_name_to_class_name(url))
    for member in sorted(set(member_endpoints.pop(url, []))):
        fn.write('    %s = %s()\n' % (member.split('/')[-1], url_name_to_class_name(member)))

    while url:
        parent = '/' in url and url.rsplit('/', 1)[0] or ''
        if not url in member_endpoints.setdefault(parent, []):
            member_endpoints[parent].append(url)
        url = parent
