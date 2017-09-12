""" This module sets up a connection session to the server of your choice
    It handles managing the cookies, ... and storing the API Calls

    ConnectionBasic keeps track of the history of API _calls, which can be accessed by calling
    ConnectionBasic like a dictionary (with str labels) or like a list (with int indexes).
    If max_history is set to ZERO, then history will not be kept and Connections will run
    in production mode for speed and less memory.

    >>> con = ConnectionBasic('username','password','api.benchristenson.com/user/login')
    """
__author__ = 'Ben Christenson'
__date__ = "10/7/15"

import os
import glob
import logging
from collections import OrderedDict  # ConnectionBasic basically acts like an Ordered Dictionary
from seaborn.python_2_to_3 import *

log = logging.getLogger(__name__)

from seaborn.rest.api_call import ApiCall  # This is the action request call to the api
from seaborn.file import mkdir
from seaborn.calling_function import function_kwargs
from seaborn.repr_wrapper import str_name_value

STATUS_NONE = 'login not attempted'
STATUS_LOGIN_FAIL = 'failed to login'
STATUS_LOGIN_SUCCESS = 'successfully logged in'
STATUS_LOGOUT = 'logged out'


def no_history_check(func):
    """
    Decorator function to setup a check to see if history has been turned off, because
    if it has then the decorated function needs to throw an exception
    :param func: function to decorate
    :return: original results or exception
    """

    def no_history_check_decorator(self, *args, **kwargs):
        if ConnectionBasic.max_history is 0:
            raise IndexError("ConnectionBasic.max_history is set to 0, therefore this functionality is disabled")
        return func(self, *args, **kwargs)

    return no_history_check_decorator


class ConnectionBasic(object):
    """
        This represents an authenticated connection and is similar to requests session,
        but also contains functionality for pre and post processing as well as historical
        tracking of API Calls.  This subclasses BaseConnection to hide uninteresting protected attributes.

        READ ONLY VARIABLES:
            status          : return the current status of login
            errors          : list of error _calls, only valid for max_history > 0
    """
    ApiCall = ApiCall  # this is for easy overload
    OrderedDict = OrderedDict  # this is for easy overload
    _login_clears_history = False  #
    max_history = 1000  # int of number of api calls to keep in history

    _methods = ['get',
                'post',
                'delete',
                'put',
                'save'
                'login']

    def __init__(self, username=None, password=None, login_url=None, auth_url=None, api_key=None, base_uri=None,
                 proxies=None, timeout=None, headers=None, cookies=None, accepted_return=None):
        """
        :param username        : str of user's email to use for the session.
        :param password        : str of password for the user
        :param login_url       : str of the login_url, if supplied it will auto login
        :param auth_url        : str of the auth_url, if Oauth2 is used
        :param api_key         : str of api key of the client software
        :param base_uri        : str of base url of the eagle eye network server
        :param proxies         : dict of string e.g. {'http':'http://127.0.0.1:8081','https':'https://127.0.0.1:8081'}
        :param timeout         : str of timeout to use for api call
        :param headers         : str of specially header to use for api calls
        :param cookies         : list of cookies to use in the http request
        :param accepted_return : str of enum ['json','text','html'] 

        """
        self._calls = self.OrderedDict()
        self.cookies = cookies or {}
        self.headers = headers or {}
        self.login_url = login_url
        self.auth_url = auth_url
        self.user_id = None

        self.base_uri = self.clean_base_uri(base_uri or login_url)
        self.proxies = proxies or {}
        self.timeout = timeout or 30
        self.put_id = {}  # {id:path}
        self.accepted_return = accepted_return
        self.wrap_return_data = self.max_history > 0  # if history == 0 then run faster because we probably don't care

        self._status = STATUS_NONE  # status of the session
        self._username = username
        self._password = password
        self._api_key = api_key

        self._call_queue = {}  # {<thread_id>:[<api_calls>]}  holds the api_call while the endpoint method manipulates
        self._count = 0  # count of the number of _calls done
        if login_url:
            self.login()

    @property
    def status(self):
        return self._status

    def login(self, username=None, password=None, login_url=None, auth_url=None):
        """
        This will automatically log the user into the pre-defined account
        
        Feel free to overwrite this with an endpoint on endpoint load
        
        :param username:  str of the user name to login in as
        :param password:  str of the password to login as
        :param login_url: str of the url for the server's login
        :param auth_url:  str of the url for the server's authorization login
        :return: str of self._status
        """
        self._username = username or self._username
        self._password = password or self._password
        self.login_url = login_url or self.login_url
        self.auth_url = auth_url or self.auth_url
        if self._username and self._password and self.login_url:
            if '%(username)s' in self.login_url:
                ret = self.post(_url=login_url % dict(username=self._username,
                                                      password=self._password, api_key=self._api_key))
            else:
                ret = self.post(_url=self.login_url, username=self._username,
                                password=self._password, api_key=self._api_key)

            if isinstance(ret,basestring) and 'Burp' in ret:
                raise Exception("Failed to Login because the server is not responding")

            self.user_id = ret.get('user_id',None)
            if self.auth_url:
                if ('%(' + ret.keys()[0] + ')s') in self.auth_url:
                    ret = self.post(_url=self.auth_url % ret)
                else:
                    ret = self.post(_url=self.auth_url, **ret)

            log.info('Successfully logged in with response: %s' % ret)
            if self._login_clears_history:
                self.clear()
            self._status = STATUS_LOGIN_SUCCESS
        else:
            self._status = STATUS_LOGIN_FAIL
        return self._status

    @property
    def errors(self):
        """
        :return list: of api _calls with errors
        """
        return [api_call for api_call in self if api_call.error is not None]

    def report(self, start=0, end=None):
        """
        This will return a list of call reports which have the endpoint with arguments
        and a representation of the data
        :param start: int of the index to start at
        :param end: int of the index to end at
        :return: list of str
        """
        return [api_call.report for api_call in self[start:end]]

    def get(self, _url, **kwargs):
        """
        This will perform a manual GET request where the user will supply the sub_url and request params (URN)
        The connections class will add the base_uri and authentication credentials.
        GET requests read data from the server
        :param _url: str of the sub url of the api call (ex. g/device/list)
        :param kwargs: dict of the request params (URN), data can be sent as a params
        :return: obj of the response data without repr formatting
        """
        return self.request('GET', _url, **kwargs).data

    def put(self, _url, **kwargs):
        """
        This will perform a manual PUT request where the user will supply the sub_url and request params (URN)
        The connections class will add the base_uri and authentication credentials.
        PUT requests create data on the server
        :param _url: str of the sub url of the api call (ex. g/device/list)
        :param kwargs: dict of the the request params (URN), data can be sent as a params
        :return: obj of the response data without repr formatting
        """
        api_call = self.request('PUT', _url, **kwargs)
        self.cookies.update(api_call.response_cookies)
        return api_call.data

    def post(self, _url, **kwargs):
        """
        This will perform a manual POST request where the user will supply the sub_url and request params (URN)
        The connections class will add the base_uri and authentication credentials.
        POST requests update data on the server
        :param _url: str of the sub url of the api call (ex. g/device/list)
        :param kwargs: dict of the request params (URN), data can be sent as a params
        :return: obj of the response data without repr formatting
        """
        api_call = self.request('POST', _url, **kwargs)
        self.cookies.update(api_call.response_cookies)
        return api_call.data

    def delete(self, _url, **kwargs):
        """
        This will perform a manual DELETE request where the user will supply the sub_url and request params (URN)
        The connections class will add the base_uri and authentication credentials.
        DELETE requests delete data on the server (which will likely set them back to default)
        :param _url: str of the sub url of the api call (ex. g/device/list)
        :param kwargs: dict of the request params (URN), data can be sent as a params
        :return: obj of the response data without repr formatting
        """
        api_call = self.request('DELETE', _url, **kwargs)
        return api_call.data

    def request(self, method, _url, **kwargs):
        """
        This will instantiate a Request with the proper values, and then
        store it in self[label].
        :param method: str of the html method ['GET','POST','PUT','DELETE','OPTION']
        :param _url: str of the sub url of the api call (ex. g/device/list)
        :param kwargs: dict of the request params (URN), data can be sent as a params
        :return: api_call object of the response
        """
        if self.base_uri and _url.startswith(self.base_uri):
            _url = _url[len(self.base_uri):]
        api_call = self._create_api_call(method, _url, kwargs)
        data = self._clean_arguments(kwargs.pop('data', None))
        params = self._clean_arguments(kwargs)

        api_call.set_request(method=method,
                             data=data,
                             params=params,
                             sub_url=_url)

        api_call.send()
        return api_call

    def url(self, _url, **kwargs):
        """
        This will return the url for a Request instead of actually performing the request, and then store it
        in self['label'].

        * Note the API call isn't actually made but it is setup to call save or open_as_file
        :param _url:   str of the sub url of the api call (ex. g/device/list)
        :param kwargs: dict of additional arguments
        :return:       str of the url for the api_call
        """
        api_call = self._create_api_call('get', _url, kwargs)
        data = self._clean_arguments(kwargs.pop('data', None))
        params = self._clean_arguments(kwargs)

        api_call.set_request(method='GET',
                             data=data,
                             params=params,
                             sub_url=_url)
        api_call._stage = 'URL'
        return api_call.url

    def save(self, filename, _url, **kwargs):
        """
        This will stream the results to a file called <filename>
        This will return the url for a Request instead of actually performing the request, and then store it
        in self['label'].

        :param filename: str of the full path of the file to save
        :param _url:     str of the sub url of the api call (ex. g/device/list)
        :param kwargs:   dict of additional arguments
        :return:
        """
        api_call = self._create_api_call('save', _url, kwargs)
        api_call.filename = filename

        data = self._clean_arguments(kwargs.pop('data', None))
        params = self._clean_arguments(kwargs)
        mkdir(os.path.split(filename)[0])
        if os.path.exists(filename):
            os.remove(filename)

        if filename.lower().endswith('.m3u8'):  # remove old files
            mkdir(os.path.split(filename)[0])
            ts_path = api_call.get_ts_folder(filename)
            mkdir(ts_path)
            [os.remove(file_) for file_ in glob.glob(ts_path + '/*.ts')]

        api_call.set_request(method='GET',
                             data=data,
                             params=params,
                             sub_url=_url)

        api_call.send(stream_to_file=filename)

        last_repeat_needed = 0
        while last_repeat_needed < api_call.repeat_needed:
            last_repeat_needed = api_call.repeat_needed
            for remaining_repeat_attempts in range(1000, -1, -1):
                if not api_call.repeat_needed:
                    break
                api_call.send(stream_to_file=filename)
        return filename

    def _create_api_call(self, method, _url, kwargs):
        """
        This will create an APICall object and return it
        :param method:  str of the html method ['GET','POST','PUT','DELETE','OPTION']
        :param _url:    str of the sub url of the api call (ex. g/device/list)
        :param kwargs:  dict of additional arguments
        :return:        ApiCall
        """
        api_call = self.ApiCall(name='%s.%s' % (_url, method),
                                label='ID_%s' % self._count,
                                base_uri=self.base_uri,
                                timeout=self.timeout,
                                headers=self.headers,
                                cookies=self.cookies,
                                proxies=self.proxies,
                                accepted_return=self.accepted_return or 'json')
        if self.max_history:
            self._count += 1  # count of _calls
            if len(self) > self.max_history:
                self._calls.pop(0)
            self._calls['ID_%s' % self._count] = api_call
        return api_call

    @staticmethod
    def _clean_arguments(kwargs):
        """
        This is to remove None and clean other arguments
        :param kwargs:
        :return:
        """
        if not isinstance(kwargs, dict):
            return kwargs
        for k in list(kwargs.keys()):
            if kwargs[k] is None:
                kwargs.pop(k)
            elif kwargs[k] is False:
                kwargs[k] = 0
            elif kwargs[k] is True:
                kwargs[k] = 1
        return kwargs

    def time_report(self, source=None, **kwargs):
        """
        This will generate a time table for the source api_calls
        :param source: obj this can be an int(index), str(key), slice, list of api_calls or an api_call
        :return: ReprListList
        """
        if source is None:
            api_calls = [self[-1]]
        elif isinstance(source, list):
            api_calls = source
        elif source is None:
            api_calls = self.values()
        elif isinstance(source, ApiCall):
            api_calls = [source]
        else:
            api_calls = self[source]
            if not isinstance(api_calls, list):
                api_calls = [api_calls]
        return '\n\n'.join([repr(api_call.time_report(**kwargs) for api_call in api_calls)])

    def __getitem__(self, item):
        """
        This will return a single result dictionary for the given key.
        :param: item: Since the labels will always be string if an integer is supplied
                      then the key will be used as an index for the _calls as they came in (not as they returned).
        :return result: {'response':response,'request':request,'data':data,'raw_data':raw_data}
        """
        if isinstance(item, str):
            return self._calls[item]
        elif isinstance(item, int):
            return self._calls[self._calls.keys()[item]]
        elif isinstance(item, slice):
            return [self[k] for k in self.keys()[item]]
        elif item is None:
            return self[:]
        else:
            raise TypeError("Item has to be of type (str,int,slice)")

    @no_history_check
    def keys(self):
        return self._calls.keys()

    @no_history_check
    def __len__(self):
        return len(self._calls)

    @no_history_check
    def clear(self):
        self._count = 0
        return self._calls.clear()

    @no_history_check
    def has_key(self, k):
        return k in self.keys()

    @no_history_check
    def items(self):
        return self._calls.items()

    @no_history_check
    def pop(self, index):
        return self._calls.pop(index)

    @no_history_check
    def values(self):
        return self._calls.values()

    @no_history_check
    def popitem(self, last):
        return self._calls.popitem(last)

    def __repr__(self):
        return '%s :: %s <%s>' % (self.__class__.__name__, self._username, self._status)

    def __str__(self):
        values = [str_name_value(k, getattr(self, k, '')) for k in
                  ['_username', '_password', 'base_uri', '_status']]
        return '%s:\n%s' % ('ConnectionBasic', '\n'.join(values))

    @property
    def base_uri(self):
        return self._base_uri

    @base_uri.setter
    def base_uri(self, url):
        self._base_uri = self.clean_base_uri(url)
        pass

    @property
    def sub_base_uri(self):
        """ This will return the sub_base_uri parsed from the base_uri
        :return: str of the sub_base_uri
        """
        return self._base_uri and self._base_uri.split('://')[-1].split('.')[0] or self._base_uri

    @sub_base_uri.setter
    def sub_base_uri(self, url):
        self.base_uri = url

    @staticmethod
    def clean_base_uri(url):
        """
        This will clean up the url so that it is in the form:
            https://<SUB_DOMAIN>.eagleeyenetworks.com/
        :param url: str of the url
        :return: str of the clean base url
        """
        if url is None:
            return url
        if not '//' in url:
            url = 'https://' + url

        ret = url[:url.find('/', url.find('//') + 2) + 1] or url
        assert '.' in url, "<%s> is not a proper base_uri" % ret

        if not ret.endswith('/'):
            ret += '/'
        return ret


def create_connection(username=None, password=None, login_url=None, auth_url=None, api_key=None, realm=None,
                      base_uri=None, proxies=None, timeout=None, headers=None, cookies=None, accepted_return=None):
    """
        Creates and returns a connection
        :param realm:
        :param username        : str of user's email to use for the session.
        :param password        : str of password for the user
        :param login_url       : str of the login_url
        :param auth_url        : str of the auth_url, if Oauth2 is used
        :param api_key         : str of api key of the client software
        :param base_uri          : str of base url of the eagle eye network server <Not Expected>
        :param proxies         : str of proxies dictionary as used in requests
        :param timeout         : str of timeout to use for api call
        :param headers         : str of specially header to use for api calls
        :param cookies         : list of cookies to use in the http request
        :param accepted_return : str of enum ['json','text','html'] 
        """
    return ConnectionBasic(**function_kwargs())


def smoke_test():
    from seaborn.local_data import LocalData
    local_data = LocalData()

    conn = ConnectionBasic(local_data.username, local_data.password,
                           login_url='http://127.0.0.1:4999/user/login')
    # login_url = 'https://mechanicsofplay.com/user/login')
    print(conn.cookies.keys())


if __name__ == '__main__':
    smoke_test()
