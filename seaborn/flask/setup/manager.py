""" This will accept command prompt commands to do events like init db, drop db, create_endpoints.
    It will run the service but isn't the only way to run the service
"""

__author__ = 'Ben Christenson'
__date__ = "9/21/15"
import os
import sys
import traceback
from seaborn.logger import log
from flask_script import Manager, prompt_bool
from .setup_flask import *

def setup_manager(setup_app):
    manager = Manager(setup_app.app)

    @manager.command
    def init_db():
        """ This will initialize the database """
        setup_app.initialize_database()
        setup_app.initialize_users()


    @manager.command
    def drop_db():
        """ This will drop the database """
        log.warning("Dropping Database")
        if setup_app.app.debug is True or prompt_bool("Are you sure you want to lose all your data"):
            setup_app.db.drop_all()


    @manager.command
    def python_bindings():
        """ This will recreate the python bindings """
        setup_app.create_python_bindings()


    @manager.command
    def unity_bindings():
        """ This will recreate the unity bindings """
        setup_app.create_unity_bindings()


    @manager.command
    def bindings():
        setup_app.create_python_bindings()
        setup_app.create_unity_bindings()


    @manager.command
    def preload_db():
        log.debug("Preloading Database")
        # todo fill in as needed


    @manager.command
    def reset():
        """ This will reinitialize the database and the bindings """
        init_db()
        preload_db()
        bindings()


    @manager.command
    def setup_user():
        initialize_users(admin_password=configuration.ADMIN_PASSWORD, demo_password=configuration.DEMO_PASSWORD)

    return manager