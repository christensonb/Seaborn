""" This simply imports the standard modules used in unit tests """
__author__ = 'Ben Christenson'
__date__ = "11/5/15"
# from gevent import monkey
# monkey.patch_all() # todo remove this

import sys
import os
import traceback
import unittest
import time
import signal
import traceback
from functools import wraps
from random import random, seed
import inspect
from seaborn.python_2_to_3 import *
from seaborn.rest_client.errors import *
from seaborn.rest_client.connection import ConnectionBasic
from seaborn.logger import log, setup_stdout_logging
from seaborn.calling_function import function_info
from seaborn.parse_doc import parse_doc_str
from seaborn.rest import api_call
from seaborn.rest import endpoint
from seaborn.rest_client.api_call import ApiError
from seaborn.local_data import LocalData
from seaborn.flask import decorators

from seaborn.skip_traceback import skip_module as traceback_skip_module
from seaborn.skip_traceback import skip_path as traceback_skip_path
traceback_skip_module(unittest.case)
# traceback_skip_path('/seaborn/',  # exclude seaborn
#                     '/Applications/PyCharm',  # exclude pycharm
#                     '/site-packages/')  # python libraries
