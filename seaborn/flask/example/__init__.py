""" This is the start routine for Apache """
from .run_flask import run, log

if __name__ == '__main__':
    log.debug("Starting Flask Service from Apache")
    run()
