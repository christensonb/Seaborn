""" This will make the unity bindings using the Web API Kit
    It assumes that a list of seaborn blueprints will be passed in with route information.

    Web API Kit:
        https://www.assetstore.unity3d.com/en/#!/content/19663

    This will make the following folders:
        models - this contains all of our mapped response classes for each resource
        operations - these are akin to api call / endpoint
        behaviours - these are classes that will manage the thread of the rest call

    This will also make the following single files (see doc below):
        ApiMonitor.cs        - This tracks all api calls for statistically information
        ApiInitialize.cs     - This is like connection in that it stores the AccessToken, logging, and base uri
        Proxy.cs             - This is spawns a Operations (api_call) object for a given endpoint
        <root_namesapce>.cs  - This will contain a mono-behavior that will add all other behaviours
        CustomApi.cs         - This will contain stub code for the developer to overwrite

"""
__author__ = 'Ben Christenson'
__date__ = "10/19/15"
import os
from seaborn.logger import log
from seaborn.file import clear_path, mkdir
from seaborn.meta import class_name_to_instant_name, url_name_to_class_name
from seaborn.sorters import by_attribute, by_longest_then_by_abc, by_key, by_shortest_then_by_abc
from collections import OrderedDict

PATH = os.path.split(os.path.abspath(__file__))[0]
tab1 = '\n    '
tab2 = '\n        '
tab3 = '\n            '
tab4 = '\n                '

PYTHON_TO_C_TYPE = {'str': 'string',
                    'datetime': 'string',  # public DateTime dt = DateTime.Parse("2016-02-04 05:05:05");    # todo
                    'bool': 'bool',
                    'int': 'int',
                    'float': 'float',
                    'dict': 'dict',
                    }


def instance_name(name):
    return name[0].lower() + name[1:]


def create_unity_blueprint_bindings(path, blue_prints, models, file_start='endpoints/', clear=False,
                                    only_decorated=True, namespace='', base_uri='', class_members=''):
    """
    :param path:           str of the full path to save the connection endpoint
    :param blue_prints:    list of BlueprintBinding instances with endpoints
    :param models:         list of models that could be referenced in the return doc
    :param file_start:     str of keyword to split the filename on to get the relative path to start from
    :param file_end:       str of keyword to split the filename on to get the relative path to end at
    :param clear:          bool if True will clear the folder first
    :param only_decorated: bool if True will filter out routes that are not decorated with seaborn flask decorator
    :param namespace:      str of the name space to prepend the resource path
    :param base_uri:       str of the domain server address e.g. 'api.mechanicsofplay.com:4999'
    :param class_members   list of str of custom class members to add to the CustomApi and CustomTest files
    :return:               None
    """

    def clean_filename(filename):
        return os.path.split(filename.replace('\\', '/').split(file_start)[-1])[0].replace('/', '_')

    if clear and os.path.exists(path):
        clear_path(path)

    mkdir(path)
    mkdir('%s/operations' % path)
    mkdir('%s/behaviors' % path)
    mkdir('%s/models' % path)
    base_uri = base_uri or (namespace + '.com')
    namespace = namespace or base_uri.rsplit('.', 1)[0]
    short_namespace = namespace.split('.')[-1]

    API_MONITOR_CODE = open('%s/cs_templates/api_monitor.cs' % PATH, 'r').read().split('/*$$')[0].replace('\r', '\n')
    BEHAVIORS_CODE = open('%s/cs_templates/behaviors.cs' % PATH, 'r').read().split('/*$$')[0].replace('\r', '\n')
    API_INITIALIZE_CODE = open('%s/cs_templates/api_initialize.cs' % PATH, 'r').read().split('/*$$')[0].replace('\r',
                                                                                                                '\n')
    NAMESPACE_CODE = open('%s/cs_templates/namespace.cs' % PATH, 'r').read().split('/*$$')[0].replace('\r', '\n')
    OPERATIONS_CODE = open('%s/cs_templates/operations.cs' % PATH, 'r').read().split('/*$$')[0].replace('\r', '\n')
    MODELS_CODE = open('%s/cs_templates/models.cs' % PATH, 'r').read().split('/*$$')[0].replace('\r', '\n')
    CUSTOM_API_CODE = open('%s/cs_templates/custom_api.cs' % PATH, 'r').read().split('/*$$')[0].replace('\r', '\n')
    CUSTOM_TEST_CODE = CUSTOM_API_CODE.replace('CustomApi', 'CustomTest')

    short_namespace_instance = instance_name(namespace.split('.')[-1])
    binding_parameters = dict(
        namespace=namespace,  # api.MechanicsOfPlay
        short_namespace=short_namespace,  # MechanicsOfPlay
        short_namespace_instant=short_namespace_instance,  # mechanicsOfPlay
        remote_base_uri='http://' + base_uri,  # api.MechanicsOfPlay.com
        local_base_uri='http://local.' + base_uri,  # local.api.MechanicsOfPlay.com
        debug_base_uri='http://127.0.0.1:4999',  # 127.0.0.1:4999
        name=None,  # HelloEchoGet
        name_instance=None,  # helloEchoGet
        arg_queries=None,  # [HttpFormField]\n        public string message="default";
        arg_declarations=None,  # public string key;\n
        arg_assignments=None,  # this.key = key;\n
        arg_params=None,  # key, value
        args=None,  # string key, string value
        custom_arguments=None,  # string key; // description

        response_type=None,  # api.MechancisOfPlay.models.Hello
        response_desc=None,  # // hello test application
        response_str= 'responseData.ToString()',
        model=None,  # Hello
        model_declarations=None,  # public string value;\n
        arg_string=None,  # ret += "key <"+key.ToString()+"> ";\n
        method=None,  # GET
        sub_uri=None,  # hello/echo
        response_converter=None,  # base.FromResponse(response);
        behaviors_declarations=[],  # public behaviors.HelloEchoGet helloEchoGet;\n
        behaviors_instantiation=[],  # helloEchoGet = gameObject.AddComponent<behaviors.HelloEchoGet> ();\n
        null=None,  # null
        class_members=tab2.join(class_members)  # public int game_id = 0;\n
    )
    binding_parameters['short_namespace_instance'] = instance_name(binding_parameters['short_namespace'])

    module_endpoints = dict([(clean_filename(blue_print.endpoints[0].filename), blue_print.endpoints)
                             for blue_print in blue_prints if getattr(blue_print, 'endpoints', [])])

    endpoint_modules = sorted(module_endpoints.keys(), key=by_longest_then_by_abc)
    models_needed_for_return = {}

    custom_api_file = open('%s/_%sCustomApi.cs' % (os.path.split(path)[0], short_namespace), 'w')
    custom_api_file.write(CUSTOM_API_CODE.split('/* Endpoint Code Here */')[0] % binding_parameters)

    custom_test_file = open('%s/_%sCustomTest.cs' % (os.path.split(path)[0], short_namespace), 'w')
    custom_test_file.write(CUSTOM_TEST_CODE.split('/* Endpoint Code Here */')[0] % binding_parameters)

    for module in endpoint_modules:
        operations_file = None
        behaviors_file = None
        url = None
        endpoints = sorted(module_endpoints[module], key=by_attribute('url', comp=by_longest_then_by_abc))
        for endpoint in endpoints:
            try:
                if only_decorated and (not endpoint.is_decorated or endpoint.binding == False):
                    continue
                if operations_file is None:
                    operations_file = open(os.path.join(path, 'operations', module + '.cs'), 'w')
                    operations_file.write(OPERATIONS_CODE.split('/* Endpoint Code Here */')[0] % binding_parameters)
                    behaviors_file = open(os.path.join(path, 'behaviors', module + '.cs'), 'w')
                    behaviors_file.write(BEHAVIORS_CODE.split('/* Endpoint Code Here */')[0] % binding_parameters)

                _type, _desc, return_type, return_desc = parse_arg_types(endpoint.doc)
                defaults = dict([(k, clean_default(v, _type[k])) for k, v in endpoint.arg_defaults.items()])

                for arg in defaults:
                    if _type[arg] in ['int', 'bool', 'float']:
                        _type[arg] += '?'

                models_needed_for_return[return_type.split('<')[-1].split('>')[0].replace('models.', '')] = endpoint

                assert len(_type) >= len(endpoint.args), \
                    "Endpoint: %s %s is missing a parameter in the __doc__" % (endpoint.url, endpoint.methods)

                test_for_complex_gets(endpoint, _type)
                for method in endpoint.methods:
                    if 'POST' in endpoint.methods and method != 'POST':
                        continue
                    method_type = ('GET' in endpoint.methods and 'Get' or 'DELETE' in endpoint.methods and 'Delete' or
                                   'POST' in endpoint.methods and 'Post' or 'Put')
                    binding_parameters['sub_uri'] = endpoint.url
                    binding_parameters['method'] = method

                    doc = endpoint.doc.split(':param')[0].split(':return')[0].strip().replace('\n', '\n\t\t\t')
                    binding_parameters['function_description'] = '/*\n\t\t\t%s\n\t\t\t*/' % doc if doc else ''
                    if method == 'PUT' and blue_prints[0].reroute_put_to_post:
                        binding_parameters['sub_uri'] += '/put'
                        binding_parameters['method'] = 'POST'


                    binding_parameters['name'] = (url_name_to_class_name(endpoint.url) + method_type).replace('_', '')
                    binding_parameters['name_instance'] = instance_name(binding_parameters['name'])
                    binding_parameters['args_with_comma'] = ''.join(['%s %s, ' % (_type[arg], arg) for arg in _type])
                    binding_parameters['args'] = ', '.join(['%s %s' % (_type[arg], arg) for arg in _type])
                    binding_parameters['arg_params_with_comma'] = ''.join([arg + ', ' for arg in _type])
                    binding_parameters['arg_params'] = ', '.join([arg for arg in _type])
                    binding_parameters['arg_declarations'] = tab2.join(
                        [arg_declaration(arg, _type, defaults, _desc) for arg in _type])

                    arg_declare = method == 'GET' and '[HttpQueryString] ' or '[HttpFormField] '

                    binding_parameters['arg_queries'] = tab2.join(
                        [arg_declare + arg_declaration(arg, _type, defaults, _desc) for arg in _type])
                    binding_parameters['arg_assignments'] = tab3.join(["this.%s = %s;" % (arg, arg) for arg in _type])
                    binding_parameters['custom_arguments'] = tab3.join(custom_arguments(_type, defaults, _desc))
                    binding_parameters['response_type'] = return_type
                    if(return_type.startswith('List')):
                        binding_parameters['response_str'] = '"'+return_type+' of size " + responseData.Count.ToString()'
                    else:
                        binding_parameters['response_str'] = 'responseData.ToString()'
                    binding_parameters['response_desc'] = ' ' * (18 - len(return_type)) + '// %s' % return_desc
                    binding_parameters['response_converter'] = response_converter(return_type)
                    binding_parameters['behaviors_instantiation'].append(
                        '%s = gameObject.AddComponent<behaviors.%s>();' % (binding_parameters['name_instance'],
                                                                           binding_parameters['name']))
                    binding_parameters['behaviors_declarations'].append(
                        'public behaviors.%s %s;' % (binding_parameters['name'],
                                                     binding_parameters['name_instance']))
                    binding_parameters['null'] = null_for_type(return_type)
                    binding_parameters['null_list'] = tab3.join(null_list(_type, defaults))
                    binding_parameters['request_serialization'] = arg_serialize(_type.keys(), _type)
                    binding_parameters['request_deserialization'] = arg_deserialize(_type.keys(), _type)

                    operations_file.write(OPERATIONS_CODE.split('/* Endpoint Code Here */')[1] % binding_parameters)
                    behaviors_file.write(BEHAVIORS_CODE.split('/* Endpoint Code Here */')[1] % binding_parameters)
                    custom_test_file.write(CUSTOM_TEST_CODE.split('/* Endpoint Code Here */')[1] % binding_parameters)

                    if not endpoint.url.startswith('test') and not endpoint.url.startswith('setup'):
                        custom_api_file.write(CUSTOM_API_CODE.split('/* Endpoint Code Here */')[1] % binding_parameters)
            except Exception as e:
                log.error("Exception with Endpoint %s" % endpoint)
                raise

        if operations_file:
            operations_file.write(OPERATIONS_CODE.split('/* Endpoint Code Here */')[2])
            behaviors_file.write(BEHAVIORS_CODE.split('/* Endpoint Code Here */')[2])
            operations_file.close()
            behaviors_file.close()
    binding_parameters['behaviors_declarations'] = tab2.join(binding_parameters['behaviors_declarations'])
    binding_parameters['behaviors_instantiation'] = tab4.join(binding_parameters['behaviors_instantiation'])

    custom_api_file.write(CUSTOM_API_CODE.split('/* Endpoint Code Here */')[2])
    custom_test_file.write(CUSTOM_TEST_CODE.split('/* Endpoint Code Here */')[2])

    with open(os.path.join(path, '%s.cs' % short_namespace), 'w') as namespace_file:
        namespace_file.write(NAMESPACE_CODE % binding_parameters)

    with open(os.path.join(path, '%sApiMonitor.cs' % short_namespace), 'w') as api_monitor_file:
        api_monitor_file.write(API_MONITOR_CODE % binding_parameters)

    with open(os.path.join(path, '%sApiInitialize.cs' % short_namespace), 'w') as api_initialize_file:
        api_initialize_file.write(API_INITIALIZE_CODE % binding_parameters)

    for model in models:
        if model.__name__ in models_needed_for_return:
            models_needed_for_return.pop(model.__name__)
            binding_parameters['model'] = model.__name__
            binding_parameters['arg_string'] = tab3.join(
                ['ret += "%s <\'"+%s.ToString()+"\'> ";' % (key, key) for key in model.keys()[:1]])
            binding_parameters['model_declarations'] = tab2.join(
                ['public %s %s;' % (python_to_c_type(model.key_type(key, models)), key) for key in model.keys()])

            parameter_types = {key:python_to_c_type(model.key_type(key, models)) for key in model.keys()}
            binding_parameters['arg_deserialize'] = arg_deserialize(model.keys(), parameter_types)
            binding_parameters['arg_serialize'] = arg_serialize(model.keys(), parameter_types)

            with open(os.path.join(path, 'models', model.__name__ + '.cs'), 'w') as model_file:
                model_file.write(MODELS_CODE % binding_parameters)


def test_for_complex_gets(endpoint, _type):
    assert not('DELETE' in endpoint.methods and 'POST' in endpoint.methods)
    if endpoint.methods == ['GET']:
        for arg, arg_type in _type.items():
            if arg_type.startswith('List'):
                raise Exception("Endpoint %s needs a POST because of variable %s" % (endpoint.url, arg))


def python_to_c_type(python_type):
    """
        This will convert the type from python to C#
    :param python_type: str of the type name in python
    :return:            str of the type name in C#
    """
    if python_type.startswith('list of '):
        ret = 'List<%s>' % (python_to_c_type(python_type[8:]))
        if ret == 'List<models.puzzle>':
            pass
        return ret

    if python_type in PYTHON_TO_C_TYPE:
        return PYTHON_TO_C_TYPE[python_type]
    if python_type in PYTHON_TO_C_TYPE.values():
        return python_type
    if python_type[0] != python_type[0].upper():
        pass
    ret = 'models.%s' % python_type
    return ret


def clean_default(v, arg_type):
    try:
        if isinstance(v, (list, tuple)) and v:
            if arg_type == 'List<string>':
                return 'new %s(new %s { "%s" })' % (arg_type, arg_type[5:-1] + '[]', '","'.join(v))
            elif arg_type == 'List<float>':
                ret = 'new %s(new %s { %sf })' % (arg_type, arg_type[5:-1] + '[]', 'f,'.join([str(f) for f in v]))
                return ret
            else:
                return 'new %s(new %s { %s })' % (arg_type, arg_type[5:-1] + '[]', str(v)[1:-1])
        if str(v) == 'False' or str(v) == 'True': v = str(v).lower()
        if arg_type == 'float' and v is not None:
            v = str(v) + 'f'
        return v
    except Exception as e:
        raise


def null_for_type(return_type):
    if return_type == 'string': return 'null'
    if return_type == 'float': return '0.0f'
    if return_type == 'int': return '0'
    if return_type == 'bool': return 'false'
    if return_type == 'datetime': return '""'
    return 'null'


def response_converter(return_type):
    if return_type == 'string':
        return 'if(response.HasError)\n            ' \
               '    return;\n            ' \
               'else\n            ' \
               '    this.responseData = response.Text.Substring(1,response.Text.Length-2);'
    elif return_type in ['int', 'float', 'int?', 'float?']:
        return 'this.responseData = %s.Parse(response.Text);' % (return_type.replace('?', ''))
    else:
        return 'base.FromResponse(response);'


def custom_arguments(_type, defaults, _desc):
    required = [arg_declaration(arg, _type, defaults, _desc, '', False) for arg in _type if arg not in defaults]
    optional = [arg_declaration(arg, _type, defaults, _desc, public='') for arg in _type if arg in defaults]
    ret = required + optional
    for i, r in enumerate(ret):
        ret[i] = r.replace(';', ',')
        if '?' in r and not '= null' in r:
            ret[i] = ret[i].replace('?', '').replace('//', ' //')  # C# sucks

    if (ret):
        ret.insert(0, '')
        ret[-1] = ret[-1].replace(',', ')')
    else:
        ret = [')']
    return ret


def arg_declaration(arg, _type, defaults, desc, public='public ', include_value=True):
    if arg in defaults and defaults[arg] is not None:
        if _type[arg] == 'string':
            return ('%s%s %s = "%s";  ' % (public, _type[arg], arg, defaults[arg])).ljust(40) + "// " + desc[arg]
        else:
            return ('%s%s %s = %s;  ' % (public, _type[arg], arg, defaults[arg])).ljust(40) + "// " + desc[arg]
    elif not public and include_value:
        return ('%s%s %s = %s;  ' % (public, _type[arg], arg, null_for_type(_type[arg]))).ljust(40) + "// " + desc[arg]
    else:
        return ('%s%s %s;  ' % (public, _type[arg], arg)).ljust(40) + "// " + desc[arg]


def arg_serialize(parameters, parameter_type, model=""):
    ret = []
    for key in parameters:
        _type = parameter_type[key]
        base_type = _type.split('List<')[-1][:-1]
        if _type in ['List<int>', 'List<string>', 'List<bool>', 'List<float>']:
            ret.append('crypto.AddList%s(%s,"%s");' % (base_type.capitalize(), key, key))
        elif _type.startswith('List<') and 'models.' in _type:
            ret.append('crypto.AddListObject(%s.SerializeList(%s, includeLabel: crypto.m_includeLabel));'%(
                base_type,key))
        elif _type.startswith('models.'):
            ret.append('crypto.AddObject(%s == null? Crypto.NULL: %s.Serialize('
                       'includeLabel: crypto.m_includeLabel),"%s");' % (key,key,key))
        elif _type.replace('?','') in ['int', 'float', 'string', 'double', 'bool']:
            ret.append('crypto.Add%s(%s,"%s");' % (_type.capitalize(), key, key))
        else:
            raise Exception("Unknown type %s for variable %s in model %s" % (_type, key, model))
    ret = '\n            '.join(ret)
    return ret


def arg_deserialize(parameters, parameter_type, model=""):
    ret = []
    for key in parameters:
        _type = parameter_type[key]
        base_type = _type.split('List<')[-1][:-1]
        if _type in ['List<int>', 'List<string>', 'List<bool>', 'List<float>']:
            ret.append('ret.%s = crypto.GetList%s();' % (key, base_type.capitalize()))
        elif _type.startswith('List<') and 'models.' in _type:
            ret.append('ret.%s = new %s();' % (key, _type))
            ret.append('foreach (string %s in crypto.GetListObject())' % key[:-1])
            ret.append('    ret.%s.Add(%s.Deserialize(%s, includeLabel: crypto.m_includeLabel));' % (key, base_type, key[:-1]))
        elif _type.startswith('models.'):
            ret.append('ret.%s = %s.Deserialize(crypto.GetObject(), includeLabel: crypto.m_includeLabel);' % (key, _type))
        elif _type.replace("?","") in ['int', 'float', 'string', 'double', 'bool']:
            ret.append('ret.%s = crypto.Get%s();' % (key, _type.capitalize()))
        else:
            raise Exception("Unknown type %s for variable %s in model %s" % (_type, key, model))
    return '\n            '.join(ret)


def parse_arg_types(doc):
    """
    :param doc: str to parse for types
    :return:    tuple of arg_type, arg_desc, return_type, return_desc
    """
    _type = OrderedDict()
    _desc = OrderedDict()
    doc = doc.replace(':return:', ':param return:')
    if ':param' in doc:
        for param in doc.split(':param ')[1:]:
            name, desc = param.split(':', 1)
            name = name.strip()
            _desc[name] = desc.strip()
            if desc.lstrip().startswith('list of '):
                _type[name] = 'list of %s' % desc.lstrip().split()[2]
            else:
                _type[name] = desc.split()[0]

    for k, v in _type.items():
        _type[k] = python_to_c_type(v)

    return_type, return_desc = _type.pop('return'), _desc.pop('return')
    return _type, _desc, return_type, return_desc


def null_list(_type, defaults):
    ret = []
    for arg in defaults:
        if (_type[arg].startswith('List')):
            ret.append('if(%s != null && %s.Count == 0)' % (arg, arg))
            ret.append('    %s = null;' % arg)
    return ret
