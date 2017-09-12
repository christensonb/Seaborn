import os
import sys

flask_folder = os.path.abspath(__file__).replace('\\', '/').rsplit('/test', 1)[0]
sys.path.append(flask_folder)

from test.base import *


class UserTest(BaseTest):
    def test_user_signup(self, username="Ben", password=None, email=None, delete_if_exists=True):
        password = password or self.local_data.user_password

        if delete_if_exists:
            try:
                old = self.conn.user.get(username=username)
                self.conn.user.delete(old['user_id'])
            except Exception as e:
                pass

        user_conn = Connection(username, password, base_uri=self.SERVER, timeout=self.TIMEOUT)
        ret = user_conn.user.signup.put(username=username, password=password, email=email)

        user_conn.user_id = ret['user_id']
        user_conn._status = "logged in from signup"
        return user_conn

    def test_user_update_email(self, email=None):
        email = email or 'update@%s' % '.'.join(self.configuration.domain.split('.')[-2:])
        ben = self.test_user_signup()
        user = ben.user.post(email=email)
        self.assertEqual(user['email'], email, 'Failed to set the email')
        user = ben.user.get()
        self.assertEqual(user['email'], email, 'Failed to get the email')
        ben.user.login.email.post(email, ben._password)

    def test_user_update_username(self, username='ben'):
        ben = self.test_user_signup(username)
        updated_name = '%s_updated' % username
        user = ben.user.post(username=updated_name)
        self.assertEqual(user['username'], updated_name, 'Failed to set the username')
        user = ben.user.get()
        self.assertEqual(user['username'], updated_name, 'Failed to get the username')
        ben.user.login.post(updated_name, ben._password)
        user = ben.user.post(username=username)

    def test_user_update_password(self, username='password_update'):
        updated_password = '%s_updated' % self.local_data.user_password
        conn = self.test_user_signup(username, self.local_data.user_password)
        user = conn.user.post(password=updated_password)
        conn.user.login.post(user['username'], updated_password)
        user = conn.user.post(password=self.local_data.user_password)

    def test_user_logout(self):
        conn = Connection('Demo-User', self.local_data.user_password, base_uri=self.SERVER, timeout=self.TIMEOUT,
                          login_url='user/login')
        user = conn.user.get()
        self.assertEqual(conn.user_id, user['user_id'], 'Failed to make sure we started out logged in')

        conn.user.logout.post()

        try:
            user = conn.user.get()  # this is suppose to fail because we are logged out
        except Exception as ex:
            return

        raise BaseException("Failed to fail at getting user info while logged out")
