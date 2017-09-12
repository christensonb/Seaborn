__author__ = 'Ben Christenson'
__date__ = "8/25/15"
import sys

if sys.version_info[0] == 2:
    from .sorters_2 import *
else:
    from .sorters_3 import *
