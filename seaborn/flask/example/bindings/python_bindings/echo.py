from seaborn.rest_client.intellisense import *


class Echo_Array_String2(Endpoint):

    def get(self):
        """
            Simply returns the value given as an int
        :return:      list of str ot test
        """
        return self.connection.get('echo/array/string2')


class Echo_Array_Float2(Endpoint):

    def get(self):
        """
            Simply returns the value given as an int
        :return:       list of float to test
        """
        return self.connection.get('echo/array/float2')


class Echo_Array_String(Endpoint):

    def get(self, values):
        """
            Simply returns the value given as an int
        :param values: list of str to test
        :return:      list of str ot test
        """
        return self.connection.get('echo/array/string', values=values)


class Echo_Array_Float(Endpoint):

    def get(self, values):
        """
            Simply returns the value given as an int
        :param values: list of float of values to return
        :return:       list of float to test
        """
        return self.connection.get('echo/array/float', values=values)


class Echo_Array_Int2(Endpoint):

    def get(self):
        """
            Simply returns the value given as an int
        :return:       list of int to test
        """
        return self.connection.get('echo/array/int2')


class Echo_Array_Int(Endpoint):

    def get(self, values):
        """
            Simply returns the value given as an int
        :param values: list of int of values to return
        :return:       list of int ot test
        """
        return self.connection.get('echo/array/int', values=values)


class Echo_Message(Endpoint):

    def get(self, message='hello'):
        """
            Very simple endpoint that just echos your message back to you
        :param message:  str of the message to echo
        :return:         str of the message echoed
        """
        return self.connection.get('echo/message', message=message)


class Echo_String(Endpoint):

    def post(self, message):
        """
            Simply test Put a string
        :param message: str of the message
        :return:        str of the message
        """
        return self.connection.post('echo/string', data=dict(message=message))

    def put(self, message):
        """
            Simply test Put a string
        :param message: str of the message
        :return:        str of the message
        """
        return self.connection.put('echo/string', data=dict(message=message))


class Echo_Float(Endpoint):

    def get(self, value=1.23):
        """
            Simply returns the value given as an int
        :param value: float of the value
        :return:      float of the returned value
        """
        return self.connection.get('echo/float', value=value)


class Echo_Int(Endpoint):

    def get(self, value=5):
        """
            Simply returns the value given as an int
        :param value: int of the value
        :return:      int of the returned value
        """
        return self.connection.get('echo/int', value=value)


class Echo_Key(Endpoint):

    def post(self, key='hello', value='world'):
        """
            This takes two parameters a key and a value and temporarily stores them on the server
        :param key:     str of key to store the value under
        :param value:   str of the value to store
        :return:        Echo dict of the key value stored
        """
        return self.connection.post('echo/key', data=dict(key=key,           value=value))

    def put(self, key='hello', value='world'):
        """
            This takes two parameters a key and a value and temporarily stores them on the server
        :param key:     str of key to store the value under
        :param value:   str of the value to store
        :return:        Echo dict of the key value stored
        """
        return self.connection.put('echo/key', data=dict(key=key,           value=value))

    def get(self, key='hello'):
        """
            Returns a stored key
        :param key: str of the key
        :return:    Test dict of the key, value
        """
        return self.connection.get('echo/key', key=key)


class Echo_Array(Endpoint):
    float = Echo_Array_Float()
    float2 = Echo_Array_Float2()
    int = Echo_Array_Int()
    int2 = Echo_Array_Int2()
    string = Echo_Array_String()
    string2 = Echo_Array_String2()


class Echo(Endpoint):
    array = Echo_Array()
    float = Echo_Float()
    int = Echo_Int()
    key = Echo_Key()
    message = Echo_Message()
    string = Echo_String()

    def get(self):
        """
            This will return the string "Hello World!"
        :return: str of "Hello World!"
        """
        return self.connection.get('echo')
