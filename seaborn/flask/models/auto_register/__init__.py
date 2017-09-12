import sys

if sys.version_info[0] == 3:
    from .auto_register_3 import *
else:
    from .auto_register_2 import *
