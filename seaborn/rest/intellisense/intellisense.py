"""
    This module does tricks to hide private and protected members from PyCharms intellisense.
    Import from here if you want a reduced intellisense.

    It is based on
        http://stackoverflow.com/questions/23457532/in-python-can-i-hide-a-base-class-members

"""
from seaborn.repr_wrapper import *

endpoint = __import__('seaborn.rest.connection', fromlist=['ConnectionEndpoint', 'ConnectionBasic',
                                                           'RestException', 'Endpoint'])


class Endpoint(endpoint.Endpoint):
    pass


class ConnectionBasic(endpoint.ConnectionBasic):
    def __init__(self, username=None, password=None, login_url=None, auth_url=None, api_key=None, base_uri=None,
                 proxies=None, timeout=None, headers=None, cookies=None, accepted_return=None):
        """
        :param username        : str of user's email to use for the session.
        :param password        : str of password for the user
        :param login_url       : str of the login_url, if supplied it will auto login
        :param auth_url        : str of the auth_url, if Oauth2 is used
        :param api_key         : str of api key of the client software
        :param base_uri        : str of base url of the eagle eye network server
        :param proxies         : str of proxies dictionary as used in requests
        :param timeout         : str of timeout to use for api call
        :param headers         : str of specially header to use for api calls
        :param cookies         : list of cookies to use in the http request
        :param accepted_return : str of enum ['json','text','html']
        """
        super(ConnectionBasic, self).__init__(username, password, login_url, auth_url, api_key, base_uri,
                                              proxies, timeout, headers, cookies, accepted_return)

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
        return super(ConnectionBasic, self).login(username, password, login_url, auth_url)


class ConnectionEndpoint(endpoint.ConnectionEndpoint, ConnectionBasic):
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
        super(ConnectionEndpoint, self).__init__(username, password, login_url, auth_url, api_key, base_uri,
                                                 proxies, timeout, headers, cookies, accepted_return)

    @property
    @repr_return
    def api_tree(self):
        return self._create_tree()


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

    assert conn.user.connection == conn and isinstance(conn.user, Endpoint)
    assert conn.user.login.connection == conn and isinstance(conn.user.login, Endpoint)

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
