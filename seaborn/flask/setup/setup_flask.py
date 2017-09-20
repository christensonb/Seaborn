""" This will module contains the setup_flask function as well as registry functions """
__author__ = 'Ben Christenson'
__date__ = "9/15/15"
import os
import inspect
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import flask_login
from flask_login import LoginManager
from flask.blueprints import Blueprint

import sqlalchemy
from sqlalchemy import create_engine

from seaborn.logger import log
from seaborn.flask.models import ApiModel
from seaborn.flask.blueprint import BlueprintBinding
from seaborn.flask.blueprint.python_bindings import create_python_blueprint_bindings
from seaborn.flask.blueprint.unity_bindings import create_unity_blueprint_bindings
from seaborn.flask import decorators
from seaborn.timestamp import set_timezone_aware


class SetupFlask(object):
    def __init__(self, configuration):
        self.db = None
        self.configuration = configuration
        self.endpoints = None
        setattr(flask_login, 'COOKIE_NAME', 'token')

        self.app = Flask(__name__, template_folder=self.configuration.TEMPLATE_FOLDER,
                         static_folder=self.configuration.STATIC_FOLDER)
        self.app.config.from_object(self.configuration)
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

        set_timezone_aware(self.configuration.timezone_aware)

        self._setup_database()
        self._setup_debug_toolbar()
        decorators.register(self.db, self.configuration.debug, '%s/' % self.configuration.flask_folder)

    def setup_run(self, endpoints):
        """
            This will setup flask and all the internals
        :return:  obj of the flask run
        """
        try:
            self.setup_endpoints(endpoints)
            self._setup_login_manager()
            self._setup_proxy_conn()
            self._test_database()

            run = self._setup_gevent() or self._run_server
            log.trace("Done with App Setup")
            return run
        except Exception as ex:
            log.error("Exception:: %s" % ex)
            raise

    def _setup_database(self):
        log.trace("Creating Database Connection %s" % self.app.config['SQLALCHEMY_DATABASE_URI'])
        self.db = SQLAlchemy(self.app)

    def _setup_gevent(self):
        if self.configuration.gevent and sys.version_info[0] == 2:
            log.trace("Setup Gevents for multithreading support")
            from gevent import monkey
            monkey.patch_all()
            from gevent import wsgi
            server = wsgi.WSGIServer((self.configuration.ip_address, self.configuration.SERVER_PORT), self.app)
            return server.serve_forever

    def _test_database(self):
        User = self.endpoints.User
        if self.configuration.debug:
            log.trace("Inspected Database for tables")
            engine = create_engine(self.configuration.SQLALCHEMY_DATABASE_URI)
            inspector = sqlalchemy.inspect(engine)
            if not inspector.get_table_names():
                self.initialize_database()
                self.initialize_users()

            if User.query.all() == []:
                self.initialize_database()
                self.initialize_users()

    def _setup_proxy_conn(self):
        if self.configuration.setup_proxy_conn:
            from seaborn.flask.blueprint import ProxyEndpoint
            conn = ProxyEndpoint()
            log.trace("Setup Proxy Connection for internal api calls %s" % id(conn))
            blue_prints = [getattr(self.endpoints, name) for name in dir(self.endpoints) if
                           isinstance(getattr(self.endpoints, name), BlueprintBinding)]
            for blue_print in blue_prints:
                blue_print.add_proxy_route(conn, True)

    def _setup_login_manager(self):
        """
        :return: None
        """
        log.trace("Setup Login Manager")
        # cookies are handled in _load_user
        login_manager = LoginManager()
        login_manager.session_protection = 'strong'
        login_manager.login_view = 'login'
        login_manager.init_app(self.app)

        @login_manager.user_loader
        def load_user(user_id):
            return self.endpoints.User.query.get(user_id)

    def setup_endpoints(self, endpoints):
        """
        :param endpoints:
        :return:          None
        """
        self.endpoints = endpoints
        log.trace("Registering Blueprint Endpoints")
        for name in dir(self.endpoints):
            blue_print = getattr(self.endpoints, name)
            if isinstance(blue_print, Blueprint):
                try:
                    self.app.register_blueprint(blue_print)
                except Exception as e:
                    log.error("Problem with blueprint %s" % blue_print)
                    raise

    def _setup_debug_toolbar(self):
        if self.configuration.DEBUG_TOOLBAR:
            log.trace("Setup Debug Toolbar")
            from flask_debugtoolbar import DebugToolbarExtension
            DebugToolbarExtension(self.app)

    def _run_server(self):
        """
        :return: None
        """
        log.trace("Starting App Run")
        self.app.run(host=self.configuration.ip_address, port=self.configuration.SERVER_PORT)

    def initialize_database(self):
        """
            WARNING: This will reinitialize the database by dropping all tables and re-creating them.
        :return: None
        """
        log.warning("Initializing Database")
        try:
            self.db.drop_all()
        except:
            pass
        self.db.create_all()

    def initialize_users(self, admin_password=None, super_password=None, demo_password=None, full_name=""):
        """
        :param admin_password: str of the password for the admin account
        :param super_password: str of the password for the super-user account
        :param demo_password:  str of the password for the demo account
        :param full_name:      str of full name to give to each of the admin, super, and demo accounts
        :return:               None
        """
        admin_password = admin_password or self.configuration.admin_password
        super_password = super_password or self.configuration.super_password
        demo_password = demo_password or self.configuration.demo_password

        admin_update = self.endpoints.user.views.admin_update
        base_domain = '.'.join(self.configuration.domain.split('.')[-2:])
        demo_user = admin_update._undecorated(username='Demo-User', email='demo@%s' % base_domain,
                                              full_name=full_name, password=demo_password, auth_level='Demo')
        super_user = admin_update._undecorated(username='Super-User', email='super@%s' % base_domain,
                                               full_name=full_name, password=super_password, auth_level='Superuser')
        admin_user = admin_update._undecorated(username='Admin-User', email='admin@%s' % base_domain,
                                               full_name=full_name, password=admin_password, auth_level='Admin')
        self.db.session.add_all([demo_user, super_user, admin_user])
        self.db.session.commit()

    def create_python_bindings(self):
        """
        """
        log.warning('Creating python API bindings')
        create_python_blueprint_bindings(
            path='%s/bindings/python_bindings' % self.configuration.flask_folder,
            blue_prints=[getattr(self.endpoints, name) for name in dir(self.endpoints) if
                         isinstance(getattr(self.endpoints, name), BlueprintBinding)],
            models=[getattr(self.endpoints, name) for name in dir(self.endpoints) if
                    inspect.isclass(getattr(self.endpoints, name)) and
                    issubclass(getattr(self.endpoints, name), ApiModel)])

    def create_unity_bindings(self):
        """
        """
        log.warning('Creating unity API bindings')
        vars = dir(self.endpoints)
        for unity_path in self.configuration.unity_folder:
            if os.path.exists(unity_path):
                create_unity_blueprint_bindings(
                    path=unity_path,
                    blue_prints=[getattr(self.endpoints, name) for name in vars if
                                 isinstance(getattr(self.endpoints, name), BlueprintBinding)],
                    models=[getattr(self.endpoints, name) for name in vars if
                            inspect.isclass(getattr(self.endpoints, name)) and
                            issubclass(getattr(self.endpoints, name), ApiModel)],
                    base_uri=self.configuration.domain,
                    clear=False,
                    class_members=[])
