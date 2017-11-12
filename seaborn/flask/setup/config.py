# encoding=utf8
""" This module defines an object for configuring the Flask app using
        app.config.from_object

    Flask look for keyword parameters in all caps.

    In addition to the keyword parameters for Flask are other lowercase keywords
    for the seaborn Flask library.
"""
__author__ = 'Ben Christenson'
__date__ = "9/15/15"
import os
from seaborn.logger import SeabornFormatter, TraceFormatter, log
from seaborn.python_2_to_3 import *
from seaborn.file import find_file
from seaborn.local_data import LocalData
from seaborn.timestamp import set_timezone_aware

class BaseConfig(object):
    """ Base config for Flask """
    timezone_aware = True

    TESTING = False
    DEBUG = False  # uses Flake Werkzeug debug which auto reloads on code changes
    debug = False  # it to setup debug options
    DEBUG_TOOLBAR = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DB_PORT = None
    gevent = False
    SERVER_PORT = 4999
    log_file = None
    log_str_format = "%(levelname)s   %(asctime)s.%(msecs)s   %(pathname)s:%(lineno)d>> %(message)s"
    log_level = "DEBUG"  # this requires debug turned on
    log_stdout_level = "DEBUG"  # this requires debug turned on (above)
    ip_address = '127.0.0.1'
    setup_proxy_conn = True

    admin_password = ""
    super_password = ""
    demo_password = ""
    SECRET_KEY = ""
    SQLALCHEMY_DATABASE_URI = ""
    database_source = 'sqlite'

    def __init__(self, domain, name, flask_folder, data_folder=None, log_file=None, database_source=None, **kwargs):
        """
        :param domain:
        :param name:
        :param flask_folder:
        :param data_folder:
        :param log_file:
        :param database_source:  str enum of ['sqlite', 'local', 'remote']
        :return:
        """
        self.domain = domain
        self.name = name
        self.flask_folder = flask_folder
        self.data_folder = data_folder or flask_folder
        self.INSTANCE_PATH = flask_folder
        self.TEMPLATE_FOLDER = '%s/templates' % flask_folder
        self.STATIC_FOLDER = '%s/static' % flask_folder

        self.unity_folder = ['%s/bindings/unity_bindings/api'%self.flask_folder]
        self.log_file = log_file or '%s/log/%s_flask.log' % (self.data_folder, name.lower())
        self.extract_secret_information()
        self.SQLALCHEMY_DATABASE_URI = self.get_database_connection(database_source or self.database_source)
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.timezone_aware = self.database_source != 'sqlite'

    def setup_logging(self):
        SeabornFormatter(relative_pathname='/%s_flask/' % self.name, str_format=self.log_str_format,
                         date_format='%H:%M:%S'). \
            setup_logging(log_filename=self.log_file,
                          log_level=self.log_level,
                          log_restart=True,
                          log_stdout_level=None)
        log.trace("Logging setup complete")

    def extract_secret_information(self):
        # secret key, which is not part of the repository for security reasons
        secret_key_file = find_file('_secret_key.txt', self.flask_folder)
        if not secret_key_file or not os.path.exists(secret_key_file):
            secret_key_file = find_file('_secret_key.txt', self.data_folder)

        assert os.path.exists(secret_key_file), 'Missing Secret Key File %s' % secret_key_file
        admin_password, super_passwrod, demo_password, secret_key = open(secret_key_file).read().split('\n', 3)
        if isinstance(secret_key, unicode):
            secret_key = secret_key.encode('latin1', 'replace')  # ensure bytes
        self.admin_password = admin_password.strip()
        self.super_password = super_passwrod.strip()
        self.demo_password = demo_password.strip()
        self.SECRET_KEY = self.SECRET_KEY or secret_key

    def get_database_connection(self, source):
        if source == 'sqlite':
            return self.sqllite_database_connection()
        if source == 'remote':
            return self.remote_database_connection()
        if source == 'local':
            return self.local_database_connection()
        raise Exception("Unknown database connection source: %s"%source)

    def sqllite_database_connection(self):
        return 'sqlite:///%s.db' % (os.path.join(self.data_folder, self.name))

    def local_database_connection(self):
        db_info = LocalData(find_file('_db_%s.json' % self.name, self.flask_folder), no_question=True)
        os.environ['password'] = db_info['password']
        db_format = '{driver}://{user}:{password}@{host}/{dbname}'
        self.DB_PORT = int(db_info["port"])
        return db_format.format(**db_info._data)

    def remote_database_connection(self):
        db_info = LocalData(find_file('_db_remote_%s.json' % self.name, self.flask_folder), no_question=True)
        os.environ['password'] = db_info['password']
        db_format = '{driver}://{user}:{password}@{host}/{dbname}'
        self.DB_PORT = int(db_info["port"])
        return db_format.format(**db_info._data)


class LocalDebugConfig(BaseConfig):
    """ Local Debug Config for running locally so don't worry about security """
    debug = True
    log_level = 'DEBUG'


class ProductionConfig(BaseConfig):
    """ Production Config """
    debug = False
    SERVER_PORT = 80
    log_level = 'WARNING'
    database_source = 'local'
