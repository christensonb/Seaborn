import os
import sys

flask_folder = os.path.abspath(__file__).replace('\\', '/').rsplit('/test', 1)[0]
sys.path.append(flask_folder)

from test.base import *


class UserTest(BaseTest):
    def test_echo(self):
        ret = self.conn.echo.get()
        self.assertEquals(ret, "Hello Cruel World!")

    def test_database_write(self):
        ret = self.conn.echo.key.post('test', 'passed')
        self.assertEquals(ret, {"echo_key": "test", "echo_value": "passed"})
        ret = self.conn.echo.key.get('test')
        self.assertEquals(ret, {"echo_key": "test", "echo_value": "passed"})
