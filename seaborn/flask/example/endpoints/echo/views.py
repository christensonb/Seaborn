"""
    This module sets up a series of echo endpoints to test if the server is up and responding.
"""
from settings.global_import import *
from seaborn.timestamp import datetime_to_str

log.trace("Importing endpoint echo.views")
from .models import Echo

ECHO = Blueprint('test', __name__)


@ECHO.route('/')
@ECHO.route('/timestamp')
def timestamp():
    """
    :return: str of HTML code for a simple Hello World
    """
    now = datetime_to_str(cst_now(), "%Y-%m-%d %H:%M:%S")
    log.debug("timestamp: " + now)
    return '<body><h1>Hello World:  %s/Flask  </h1>%s</body>' % (configuration.name, now)


@ECHO.route('/echo')
@api_endpoint()
def hello_world():
    """
        This will return the string "Hello World!"
    :return: str of "Hello World!"
    """
    log.debug("echo:: Hello Cruel World!")
    return 'Hello Cruel World!'


@ECHO.route('/echo/message')
@api_endpoint()
def echo(message='hello'):
    """
        Very simple endpoint that just echos your message back to you
    :param message:  str of the message to echo
    :return:         str of the message echoed
    """
    return 'ECHO: %s' % message


@ECHO.route('/echo/int')
@api_endpoint(auth='Admin')
def get_int(value=5):
    """
        Simply returns the value given as an int
    :param value: int of the value
    :return:      int of the returned value
    """
    return int(value)


@ECHO.route('/echo/string', methods=['POST', 'PUT'])
@api_endpoint(binding=False, auth='Admin')
def put_string(message):
    """
        Simply test Put a string
    :param message: str of the message
    :return:        str of the message
    """
    return message


@ECHO.route('/echo/float')
@api_endpoint(binding=False, auth='Admin')
def get_float(value=1.23):
    """
        Simply returns the value given as an int
    :param value: float of the value
    :return:      float of the returned value
    """
    return float(value)


@ECHO.route('/echo/key/post', methods=['GET'])
@ECHO.route('/echo/key', methods=['POST', 'PUT'])
@api_endpoint(commit=True, add=True, auth='Admin')
def put_message(key='hello', value='world'):
    """
        This takes two parameters a key and a value and temporarily stores them on the server
    :param key:     str of key to store the value under
    :param value:   str of the value to store
    :return:        Echo dict of the key value stored
    """
    test = Echo.get_or_create(dict(echo_value=value), echo_key=key)
    log.debug("echo DB: %s" % id(db))
    return test


@ECHO.route('/echo/key', methods=['GET'])
@api_endpoint(auth='Admin')
def get_message(key='hello'):
    """
        Returns a stored key
    :param key: str of the key
    :return:    Test dict of the key, value
    """
    test = Echo.query.filter_by(echo_key=key).first()
    if test is None:
        return '%s not found!' % key
    return test


@ECHO.route('/echo/array/string')
@api_endpoint(auth='Admin')
def get_array_string(values):
    """
        Simply returns the value given as an int
    :param values: list of str to test
    :return:      list of str ot test
    """
    assert isinstance(values, (tuple, list))
    for v in values:
        assert isinstance(v, basestring)
    return list(values)


@ECHO.route('/echo/array/string2')
@api_endpoint(auth='Admin')
def get_array_string2():
    """
        Simply returns the value given as an int
    :return:      list of str ot test
    """
    return ['a', 'b', 'c']


@ECHO.route('/echo/array/int')
@api_endpoint(auth='Admin')
def get_array_int(values):
    """
        Simply returns the value given as an int
    :param values: list of int of values to return
    :return:       list of int ot test
    """
    assert isinstance(values, (tuple, list))
    for v in values:
        assert isinstance(v, int)
    return list(values)


@ECHO.route('/echo/array/int2')
@api_endpoint(auth='Admin')
def get_array_int2():
    """
        Simply returns the value given as an int
    :return:       list of int to test
    """
    return range(3)


@ECHO.route('/echo/array/float')
@api_endpoint(auth='Admin')
def get_array_float(values):
    """
        Simply returns the value given as an int
    :param values: list of float of values to return
    :return:       list of float to test
    """
    assert isinstance(values, (tuple, list))
    for v in values:
        assert isinstance(v, float)
    return list(values)


@ECHO.route('/echo/array/float2')
@api_endpoint(auth='Admin')
def get_array_float2():
    """
        Simply returns the value given as an int
    :return:       list of float to test
    """
    return [1.1, 2.2, 3.3]
