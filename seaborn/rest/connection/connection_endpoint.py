""" This module extends the Connection class such that
    there are pre_processing calls, and this can accept endpoints
"""

__author__ = 'Ben Christenson'
__date__ = "10/8/15"
from .connection_basic import *
import gevent
import inspect
from seaborn.meta import instant_name_to_class_name
from seaborn.repr_wrapper import rep, repr_return
from seaborn.rest.endpoint import Endpoint, RestException
from seaborn.python_2_to_3 import *


class ConnectionEndpoint(ConnectionBasic):
    """
        This represents an authenticated connection and is similar to requests session,
        but also contains functionality for pre and post processing as well as historical
        tracking of API Calls.  This subclasses BaseConnection to hide uninteresting protected attributes.

        READ ONLY VARIABLES:
            api_tree        : str of the endpoints and methods
            status          : return the current status of login
            errors          : list of error _calls, only valid for max_history > 0
    """

    def __init__(self, username=None, password=None, login_url=None, auth_url=None, api_key=None, base_uri=None,
                 proxies=None, timeout=None, headers=None, cookies=None, accepted_return=None):
        """
        :param username        : str of user's email to use for the session.
        :param password        : str of password for the user
        :param login_url       : str of the login_url, if supplied it will auto login
        :param auth_url        : str of the auth_url, if Oauth2 is used
        :param api_key         : str of api key of the client software
        :param base_uri          : str of base url of the eagle eye network server
        :param proxies         : str of proxies dictionary as used in requests
        :param timeout         : str of timeout to use for api call
        :param headers         : str of specially header to use for api calls
        :param cookies         : list of cookies to use in the http request
        :param accepted_return : str of enum ['json','text','html']
        """
        self._call_temps = {}  # {<thread_id>:[{base_url:None, timeout:None}]}  holds temporary api call values to be popped
        super(ConnectionEndpoint, self).__init__(username, password, login_url, auth_url, api_key, base_uri,
                                                 proxies, timeout, headers, cookies, accepted_return)

        self.reinstantiate_endpoints()

    def reinstantiate_endpoints(self, endpoint=None):
        """
            This will reinstantiate the endpoints with the connection this time
        :param endpoint: Endpoint object to instantiate the sub endpoint in.
        :return:         None
        """
        endpoint = endpoint or self
        for k, v in endpoint.__class__.__dict__.items():
            if isinstance(v, Endpoint):
                setattr(endpoint, k, v.__class__(self))
            elif inspect.isclass(v) and issubclass(v, Endpoint):
                setattr(endpoint, k, v(self))

    def _pre_process_call(self, name="Unknown", endpoint_params=None):
        """
        This is called by the method_decorator within the Endpoint.
        The point is to capture a slot for the endpoint.method to put it's final _calls.
        It also allows for some special new arguments that will be extracted before the endpoint is called

        :param name: str of the name of the endpoint calling function
        :param endpoint_params: dict of the arguments passed to the endpoint method
        """
        call_temps = self._call_temps.get(self._get_thread_id(), None)
        call_params = call_temps and call_temps.pop() or {}
        default_params = dict(name=name,
                              label='ID_' + str(self._count),
                              base_uri=self.base_uri,
                              timeout=self.timeout,
                              headers={},
                              cookies={},
                              proxies=self.proxies,
                              accepted_return=self.accepted_return or 'json')

        for k, v in default_params.items():
            if call_params.get(k, None) is None:
                call_params[k] = v

        sub_base_uri = call_params.pop('sub_base_uri', None)
        if sub_base_uri:
            call_params['base_uri'] = self.clean_base_uri(sub_base_uri)

        endpoint_params = endpoint_params or {}
        for k, v in (call_temps and call_temps.pop().items() or []):
            if v is not None and k not in endpoint_params:
                endpoint_params.setdefault(k, v)

        for k, v in self.cookies.items():
            call_params['cookies'].setdefault(k, v)

        for k, v in self.headers.items():
            call_params['headers'].setdefault(k, v)

        api_call = self.ApiCall(**call_params)

        self._call_queue.setdefault(self._get_thread_id(), []).append(api_call)

        if self.max_history is not 0:
            self._count += 1  # count of _calls
            if len(self) > self.max_history:
                self._calls.popitem(0)
            self._calls[call_params['label']] = api_call
        return api_call

    def _post_process_call(self, api_call, data, method_return_types):
        """
        This will wrap the object in a thin representational object
        that will make the object still act as the original object.
        :param api_call: ApiCall of the api_call to store the results
        :param data: obj of data as return from the endpoint which can be a manipulation of the api call data
        :return: repr obj of the data as seen in the eagleeyenetworks.returns.py
        """
        if self.wrap_return_data:
            data = rep(data, **method_return_types)  # this will make it have a nice pretty repr & str

        if self.max_history:
            api_call.save_formatted_data(data)
        return data

    @staticmethod
    def _get_thread_id():
        """
        :return: str of the unique identification of the current gevent thread
        """
        return id(gevent.getcurrent())

    def _pop_api_call(self, method, _url, kwargs):
        """
        This will initialize an api_call or pop one that has already been initialized with the endpoint parameters
        :param method:  str of the html method ['GET','POST','PUT','DELETE','OPTION']
        :param _url:    str of the sub url of the api call (ex. g/device/list)
        :param kwargs:  dict of additional arguments
        :return:        ApiCall
        """
        call_queue = self._call_queue.setdefault(self._get_thread_id(), [])
        if not call_queue:  # user called request or get,put,post,delete directly from the connection
            self._pre_process_call(name='%s.%s' % (_url, method),
                                   endpoint_params=kwargs)  # this will add the api_call to the call_queue
        return call_queue.pop()

    _create_api_call = _pop_api_call  #

    def __call__(self, label=None, sub_base_uri=None, timeout=None, headers=None, cookies=None,
                 accepted_return=None, max_duration=None, max_size=None):
        """
        This will allow setting a temporary label, base_url or timeout for the next api_call
        :param label: str of the label for the api_call within the connection, i.e. conn['ID_1']
        :param sub_base_uri: str of the sub_base_uri for the server
        :param timeout: int of the number of seconds to wait before timing out
        :param headers: dict of header parameters
        :param cookies: dict of cookie parameters
        :param accepted_return: str of [json, html, ...]
        :param max_duration: max amount of time to allow for the api call, this allows for cutting an api call short
        :param max_size: max amount to download, this allows for cutting an api call short for testing
        :return: self
        """
        temp_params = dict(label=label, sub_base_uri=sub_base_uri, headers=headers, timeout=timeout, cookies=cookies,
                           accepted_return=accepted_return, max_duration=max_duration,
                           max_size=max_size)
        self._call_temps.setdefault(self._get_thread_id(), []).append(temp_params)
        return self

    def instantiate_endpoint_class(self, path, EndpointClass):
        endpoints = path.split('.')
        current_endpoint = self
        for i in xrange(len(endpoints)):
            endpoint = getattr(current_endpoint, endpoints[i], None)
            if endpoint is not None and getattr(endpoint, 'connection', -1) is -1:
                raise Exception('An endpoint has been used that looks like a method %s at %s' % (endpoints[i], path))
            if endpoint is None or endpoint.connection is not self:
                endpoint = EndpointClass(self)
                endpoint.path = '.'.join(endpoints[:i + 1])
                endpoint.__name__ = instant_name_to_class_name(endpoint.path)
                setattr(current_endpoint, endpoints[i], endpoint)

    @property
    @repr_return
    def api_tree(self):
        return self._create_tree()

    def _create_tree(self, endpoint=None, index=0):
        """
        This will return a string of the endpoint tree structure
        :param endpoint: Endpoint's Current path of the source
        :param index: int number of tabs to space over
        :return: str
        """
        tab = ''  # '\t' * index
        ret = ''
        if endpoint:
            name = endpoint.path.split('.', 1)[1].replace('.', '/') + '/'
            ret += tab + name + '\n'
            ret += endpoint.method_calls(' ' * len(tab + name))
        else:
            endpoint = self

        for child_name in endpoint._endpoints:
            child = getattr(endpoint, child_name, None)
            if child:
                ret += self._create_tree(child, index + 1)
        return ret


def smoke_test():
    from seaborn.local_data import LocalData
    local_data = LocalData()

    class User_Login(Endpoint):
        def post(self, username, password):
            """
            :param username: str of the username
            :param password: str of the password
            :return:         None
            """
            return self.connection.post('user/login', username=username, password=password)

    class User(Endpoint):
        login = User_Login()

    class Connection(ConnectionEndpoint):
        user = User()

    conn = Connection(base_uri='https://api.mechanicsofplay.com')
    try:
        conn.user.login.post(username=local_data.username, password=local_data.password)
    except Exception as e:
        if conn[-1].url == u'https://api.mechanicsofplay.com/user/login?username=%s&password=%s' % (local_data.username,
                                                                                                    local_data.password):
            print("Remote host is down, but connection_endpoint appears to be doing the right things")
        else:
            raise

    print(conn.cookies.keys())


if __name__ == '__main__':
    smoke_test()
