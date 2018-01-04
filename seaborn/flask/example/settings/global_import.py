from seaborn.logger import log

log.trace("importing flask modules")
from flask import render_template, flash, session, request, abort
from flask_login import current_user, login_user
from sqlalchemy.ext.associationproxy import association_proxy

log.trace("importing seaborn modules")
from seaborn.flask.decorators import api_endpoint, MEMCACHE
from seaborn.flask.blueprint import ProxyEndpoint
from seaborn.flask.blueprint import BlueprintBinding as Blueprint
from seaborn.rest_client.errors import *
from seaborn.timestamp import cst_now
from seaborn.flask.setup.setup_flask import SetupFlask
from seaborn.flask.models import ApiModel
from seaborn.calling_function import function_kwargs
from seaborn.python_2_to_3 import *

log.trace("importing sqlalchemy modules")
from sqlalchemy import *
from sqlalchemy.orm import joinedload, backref, relationship

log.trace("importing generic modules")
import time
import datetime
import re
import random
import os
import json

log.trace("importing configuration")
from .config import configuration

configuration.setup_logging()

log.trace("setting up the flask app")
setup_flask = SetupFlask(configuration)
app = setup_flask.app
db = setup_flask.db

log.trace("creating proxy endpoint")
conn = ProxyEndpoint()
