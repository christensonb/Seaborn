""" This is to start the flask server when debugging """
import os
import sys
import traceback

sys.path.append(os.path.split(os.path.abspath(__file__)[0]))
from seaborn.logger import log

try:
    import settings.global_import
    from settings.global_import import setup_flask
except Exception as ex:
    log.error("Exception in importing global_import with %s\n\n%s" % (ex, traceback.format_exc()))
    print("Exception in importing global_import with %s\n\n%s" % (ex, traceback.format_exc()))
    sys.exit()

try:
    import endpoints
except Exception as ex:
    log.error("Exception in importing endpoints with %s\n\n%s" % (ex, traceback.format_exc()))
    print("Exception in importing endpoints with %s\n\n%s" % (ex, traceback.format_exc()))
    sys.exit()

try:
    run = setup_flask.setup_run(endpoints)
except Exception as ex:
    log.error("Exception in setup flask with %s\n\n%s" % (ex, traceback.format_exc()))
    print("Exception in setup flask with %s\n\n%s" % (ex, traceback.format_exc()))
    sys.exit()

if __name__ == '__main__':
    log.debug("Starting Flask Service from Run")
    run()
