from seaborn.rest_client.intellisense import *
from .echo import *
from .user import *


class Connection(ConnectionEndpoint):
    echo = Echo()
    user = User()
