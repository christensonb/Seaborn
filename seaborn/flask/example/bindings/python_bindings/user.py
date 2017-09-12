from seaborn.rest.intellisense import *


class User_Login_Email(Endpoint):

    def post(self, email, password):
        """
            This will process logging the user in
        :param email:    str of the email as an alternative to username
        :param password: str of the password
        :return:         User dict
        """
        return self.connection.post('user/login/email', data=dict(email=email,           password=password))


class User_Username(Endpoint):

    def delete(self, username):
        """
            This will delete a user from the Database
        :param username: str of the username give my the player
        :return:         User dict of the user created
        """
        return self.connection.delete('user/username', username=username)


class User_Logout(Endpoint):

    def post(self):
        """
            This will log the user out
        :return: str of a message saying success
        """
        return self.connection.post('user/logout')


class User_Signup(Endpoint):

    def put(self, username, password, email=None, full_name=None):
        """
            This will create a PnP user
        :param username:  str of the username give my the player
        :param password:  str of the password which will be hashed
        :param email:     str of the user's email address
        :param full_name: str of the full name
        :return:          User dict of the user created
        """
        return self.connection.put('user/signup',
                                   data=dict(username=username,
                                             password=password,
                                             email=email,
                                             full_name=full_name))


class User_Admin(Endpoint):

    def get(self, username, email=None, full_name=None, password=None, status=None, auth_level=None, user_id=None):
        """
        :param username:   str of the username give my the player
        :param email:      str of the user's email address
        :param full_name:  str of the full name
        :param password:   str of the encrypted password
        :param status:     str of the enum status ['Active', 'Suspended']
        :param auth_level: str of the enum auth_level ['User', 'Demo', 'Superuser', 'Admin']
        :param user_id:    int of the user_id to update
        :return:           User dict of the user updated by admin
        """
        return self.connection.get('user/admin',
                                   username=username,
                                   email=email,
                                   full_name=full_name,
                                   password=password,
                                   status=status,
                                   auth_level=auth_level,
                                   user_id=user_id)

    def put(self, username, email=None, full_name=None, password=None, status=None, auth_level=None, user_id=None):
        """
        :param username:   str of the username give my the player
        :param email:      str of the user's email address
        :param full_name:  str of the full name
        :param password:   str of the encrypted password
        :param status:     str of the enum status ['Active', 'Suspended']
        :param auth_level: str of the enum auth_level ['User', 'Demo', 'Superuser', 'Admin']
        :param user_id:    int of the user_id to update
        :return:           User dict of the user updated by admin
        """
        return self.connection.put('user/admin',
                                   data=dict(username=username,
                                             email=email,
                                             full_name=full_name,
                                             password=password,
                                             status=status,
                                             auth_level=auth_level,
                                             user_id=user_id))

    def post(self, username, email=None, full_name=None, password=None, status=None, auth_level=None, user_id=None):
        """
        :param username:   str of the username give my the player
        :param email:      str of the user's email address
        :param full_name:  str of the full name
        :param password:   str of the encrypted password
        :param status:     str of the enum status ['Active', 'Suspended']
        :param auth_level: str of the enum auth_level ['User', 'Demo', 'Superuser', 'Admin']
        :param user_id:    int of the user_id to update
        :return:           User dict of the user updated by admin
        """
        return self.connection.post('user/admin',
                                    data=dict(username=username,
                                              email=email,
                                              full_name=full_name,
                                              password=password,
                                              status=status,
                                              auth_level=auth_level,
                                              user_id=user_id))


class User_Array(Endpoint):

    def get(self, user_ids=None, usernames=None, status=None):
        """
        :param user_ids:  list of int of the user_ids to return
        :param usernames: list of str of the usernames to return
        :param status:    str of the status
        :return:          list of User
        """
        return self.connection.get('user/array',
                                   user_ids=user_ids,
                                   usernames=usernames,
                                   status=status)

    def post(self, user_ids=None, usernames=None, status=None):
        """
        :param user_ids:  list of int of the user_ids to return
        :param usernames: list of str of the usernames to return
        :param status:    str of the status
        :return:          list of User
        """
        return self.connection.post('user/array',
                                    data=dict(user_ids=user_ids,
                                              usernames=usernames,
                                              status=status))


class User_Login(Endpoint):
    email = User_Login_Email()

    def post(self, username, password, email=None):
        """
            This will process logging the user in
        :param username: str of the username
        :param password: str of the password
        :param email:    str of the email as an alternative to username
        :return:         User dict
        """
        return self.connection.post('user/login',
                                    data=dict(username=username,
                                              password=password,
                                              email=email))


class User(Endpoint):
    admin = User_Admin()
    array = User_Array()
    login = User_Login()
    logout = User_Logout()
    signup = User_Signup()
    username = User_Username()

    def get(self):
        """
        :return: User dict of the current user
        """
        return self.connection.get('user')

    def delete(self, user_id=None):
        """
            This will delete a user from the Database
        :param user_id: int of the users id
        :return:        User dict of the user created
        """
        return self.connection.delete('user', user_id=user_id)

    def post(self, username=None, email=None, full_name=None, password=None):
        """
            This will update a PnP user
        :param username:  str of the username give my the player
        :param email:     str of the user's email address
        :param full_name: str of the full name
        :param password:  str of the password which will be hashed
        :return:          User dict of the user updated
        """
        return self.connection.post('user',
                                    data=dict(username=username,
                                              email=email,
                                              full_name=full_name,
                                              password=password))
