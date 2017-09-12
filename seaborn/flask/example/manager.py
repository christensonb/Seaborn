""" This will accept command prompt commands to do events like init db, drop db, create_endpoints.
    It will run the service but isn't the only way to run the service
"""
import sys
from run_flask import setup_flask
from seaborn.flask.setup.manager import setup_manager


def main():
    if 'runserver' in sys.argv and not '--port' in sys.argv:
        sys.argv += ['--port', str(setup_flask.configuration.SERVER_PORT)]
    if len(sys.argv) < 2:
        sys.argv.append('bindings')

    manager = setup_manager(setup_flask)
    manager.run()
    print("That's All Folks")


if __name__ == '__main__':
    main()
