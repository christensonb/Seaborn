from __future__ import absolute_import
import logging
import sys
import os
import io
import traceback
from logging import currentframe, DEBUG

from seaborn.file import mkdir_for_file


class SeabornLogger(logging.Logger):
    TRACE = 2  # new log level
    TRACE2 = 1
    propagate = False

    # add new levels like this
    def trace(self, msg, *args, **kwargs):
        if self.isEnabledFor(self.TRACE):
            self._log(self.TRACE, msg, args, **kwargs)

    def trace2(self, msg, *args, **kwargs):
        if self.isEnabledFor(self.TRACE):
            self._log(self.TRACE2, msg, args, **kwargs)

    _srcfile = os.path.normcase(__file__)

    def __init__(self, name='seaborn'):
        if sys.version_info[0] == 2:
            logging._levelNames[self.TRACE] = 'TRACE'
            logging._levelNames['TRACE'] = self.TRACE
            logging._levelNames[self.TRACE2] = 'TRACE2'
            logging._levelNames['TRACE2'] = self.TRACE2
        else:
            logging._levelToName[self.TRACE] = 'TRACE'
            logging._levelToName['TRACE'] = self.TRACE
            logging._levelToName[self.TRACE2] = 'TRACE2'
            logging._levelToName['TRACE2'] = self.TRACE2
        setattr(logging, 'TRACE', self.TRACE)

        setattr(logging, 'TRACE2', self.TRACE2)
        super(SeabornLogger, self).__init__(name)

    def findCaller(self, stack_info=False):
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.
        """
        f = logging.currentframe()
        # On some versions of IronPython, currentframe() returns None if
        # IronPython isn't run with -X:Frames.
        if f is not None:
            f = f.f_back
        rv = "(unknown file)", 0, "(unknown function)"
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename == logging._srcfile or filename == self._srcfile:
                f = f.f_back
                continue
            rv = (co.co_filename, f.f_lineno, co.co_name)
            if stack_info:
                sio = io.StringIO()
                sio.write('Stack (most recent call last):\n')
                traceback.print_stack(f, file=sio)
                sinfo = sio.getvalue()
                if sinfo[-1] == '\n':
                    sinfo = sinfo[:-1]
                sio.close()
            break
        return rv


log = SeabornLogger()


class SeabornFormatter(logging.Formatter):
    """ This will perform the traditional format then break it on >>
        and left justify it to the header width
    """
    header_width = 80
    line_break_width = 200 # if msg is longer than this then it will get truncated
    max_width = 10000        # if msg is longer than this then it will truncate the message
    date_format = "%Y-%m-%d %H:%M:%S"
    str_format = "%(asctime)s.%(msecs)s %(module)s.%(funcName)s:%(lineno)d %(levelname)s>> %(message)s"
    relative_pathname = None

    DEFAULT_LOG_FILE = None  # no log file will be setup
    DEFAULT_LOG_LEVEL = "DEBUG"
    DEFAULT_LOG_RESTART = False
    DEFAULT_LOG_HISTORY = False
    DEFAULT_LOG_STDOUT = "DEBUG"
    DEFAULT_LOG_FILTER =  None

    def __init__(self, str_format=None, date_format=None, header_width=None, relative_pathname=None):
        """
            This will add custom logging formatting
        :param str_format:          to use for this handler
        :param date_format:         format to use for key word "date"
        :param header_width:        int of how much to ljust the text before ">>"
        :param relative_pathname:   str to split the "pathname" on to give a relative path
        """
        if header_width:      self.header_width = header_width
        if relative_pathname: self.relative_pathname = relative_pathname.replace('\\', '/')
        if str_format:        self.str_format = str_format
        if date_format:       self.date_format = date_format

        self.is_relative_needed = '%(pathname)s' in self.str_format and relative_pathname
        self.is_ljust_needed = '>>' in self.str_format
        super(SeabornFormatter, self).__init__(self.str_format, self.date_format)

    def format(self, record):
        if self.is_relative_needed:
            record.pathname = record.pathname.replace('\\', '/').split(self.relative_pathname, 1)[-1]
            if '/site-packages/' in record.pathname:
                record.pathname = 'site-packages/' + record.pathname.split('/site-packages/')[-1]
            if '/seaborn/seaborn' in record.pathname:
                record.pathname = 'seaborn' + record.pathname.split('/seaborn/seaborn')[-1]

        record.__dict__['msecs'] = str(record.__dict__['msecs']).split('.')[0].rjust(3, '0')
        ret = super(SeabornFormatter, self).format(record)
        if self.is_ljust_needed:
            header, msg = ret.split('>>', 1)
            log_type, header = header.split(None,1)
            line_break = '\n' if len(msg) > self.line_break_width else ''
            ret = '%s%s %s>>%s%s' % (line_break, log_type.ljust(8), header.ljust(self.header_width-9),
                                     msg[:self.max_width], line_break)
        return ret

    def setup_logging(self, log_filename=None, log_level=None, log_file_level=None, log_restart=None, log_history=None,
                      silence_modules=None, log_stdout_level='', log_filter=''):
        setup_logging(formatter=self,
                      log_filename=log_filename or self.DEFAULT_LOG_FILE,
                      log_level=log_level or self.DEFAULT_LOG_LEVEL,
                      log_restart=log_restart or self.DEFAULT_LOG_RESTART,
                      log_history=log_history or self.DEFAULT_LOG_HISTORY,
                      log_file_level=log_file_level or log_level or self.DEFAULT_LOG_LEVEL,
                      log_stdout_level=self.DEFAULT_LOG_STDOUT if log_stdout_level == '' else log_stdout_level,
                      log_filter = self.DEFAULT_LOG_FILTER if log_filter == '' else log_filter,
                      silence_modules=silence_modules)


class NoErrorFilter(logging.Filter):
    def filter(self, record):
        return record.levelno < logging.ERROR


class TraceFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == SeabornLogger.TRACE or \
               record.levelno == SeabornLogger.TRACE2 or \
               record.levelno >= logging.ERROR


class TraceFormatter(SeabornFormatter):
    DEFAULT_LOG_LEVEL = "TRACE"
    DEFAULT_LOG_RESTART = True
    DEFAULT_LOG_FILTER = TraceFilter()
    date_format = "%H:%M:%S"
    header_width = 60
    str_format = "%(levelname)s %(asctime)s.%(msecs)s %(pathname)s:%(lineno)d >> %(message)s"


class Trace2Formatter(SeabornFormatter):
    DEFAULT_LOG_LEVEL = "TRACE2"
    DEFAULT_LOG_RESTART = True
    date_format = "%H:%M:%S"
    header_width = 60
    str_format = "%(levelname)s %(asctime)s.%(msecs)s %(pathname)s:%(lineno)d >> %(message)s"


class DebugFormatter(SeabornFormatter):
    str_format = "%(asctime)s.%(msecs)s %(pathname)s [%(funcName)s:%(lineno)d] %(levelname)s>> %(message)s"
    date_format = "%H:%M:%S"
    DEFAULT_LOG_FILE = os.path.join(os.getcwd(), '_debug.log')
    DEFAULT_LOG_HISTORY = True
    DEFAULT_LOG_RESTART = True


class PyCharmFormatter(SeabornFormatter):  # this never did what I wanted which was to make hyperlinks for files
    str_format = '%(asctime)s.%(msecs)s File "%(pathname)s:%(lineno)d" %(funcName)s'
    date_format = "%H:%M:%S"
    DEFAULT_LOG_FILE = None


LOG_LEVEL = DEBUG


def setup_log_level(log_level):
    global LOG_LEVEL
    if LOG_LEVEL == log_level or log_level is None:
        return
    log.setLevel(log_level)


def setup_logging(log_filename=None, log_level="DEBUG", str_format=None, date_format=None, log_file_level="DEBUG",
                  log_stdout_level=None, log_restart=False, log_history=False, formatter=None, silence_modules=None,
                  log_filter=None):
    """
    This will setup logging for a single file but can be called more than once
    LOG LEVELS are "CRITICAL", "ERROR", "INFO", "DEBUG"
    :param log_filename:    str of the file location
    :param log_level:       str of the overall logging level for setLevel
    :param str_format:      str of the logging format
    :param date_format:     str of the date format
    :param log_file_level   str of the log level to use on this file
    :param log_stdout_level str of the log level to use on this file (None means no stdout logging)
    :param log_restart:     bool if True the log file will be deleted first
    :param log_history:     bool if True will save another log file in a folder called history with the datetime
    :param formatter:       logging.Format instance to use
    :param silence_modules  list of str of modules to silence
    :param log_filter:      logging.filter instance to add to handler
    :return:                None
    """
    setup_log_level(log_level)

    if log_filename:
        setup_file_logging(log_filename=log_filename, str_format=str_format, log_history=log_history,
                           formatter=formatter, log_file_level=log_file_level, log_restart=log_restart,
                           date_format=date_format, log_filter=log_filter)
    if log_stdout_level is not None:
        setup_stdout_logging(log_level=log_level, log_stdout_level=log_stdout_level, str_format=str_format,
                             date_format=date_format, formatter=formatter, log_filter=log_filter)

    silence_module_logging(silence_modules)


def setup_stdout_logging(log_level="DEBUG", log_stdout_level="DEBUG", str_format=None, date_format=None, formatter=None,
                         silence_modules=None, log_filter=None):
    """
    This will setup logging for stdout and stderr
    :param formatter:
    :param log_level:        str of the overall logging level for setLevel
    :param log_stdout_level: str of the logging level of stdout
    :param str_format:       str of the logging format
    :param date_format:      str of the date format
    :param silence_modules:  list of str of modules to exclude from logging
    :param log_filter:       logging.filter instance to add to handler
    :return:                 None
    """
    setup_log_level(log_level)
    formatter = formatter or SeabornFormatter(str_format, date_format)

    if log_stdout_level != 'ERROR':
        stdout_handler = logging.StreamHandler(sys.__stdout__)
        add_handler(log_stdout_level, stdout_handler, formatter, NoErrorFilter())

    stderr_handler = logging.StreamHandler(sys.__stderr__)
    add_handler("ERROR", stderr_handler, formatter, log_filter)

    silence_module_logging(silence_modules)


def setup_file_logging(log_filename, log_file_level="DEBUG", str_format=None, date_format=None,
                       log_restart=False, log_history=False, formatter=None, silence_modules=None, log_filter=None):
    """
    This will setup logging for a single file but can be called more than once
    LOG LEVELS are "CRITICAL", "ERROR", "INFO", "DEBUG"
    :param log_filename:    str of the file location
    :param log_file_level   str of the log level to use on this file
    :param str_format:      str of the logging format
    :param date_format:     str of the date format
    :param log_restart:     bool if True the log file will be deleted first
    :param log_history:     bool if True will save another log file in a folder called history with the datetime
    :param formatter:       logging.Format instance to use
    :param log_filter:      logging.filter instance to add to handler
    :param silence_modules  list of str of modules to silence
    :return:                None
    """
    from seaborn.timestamp import datetime_to_str
    if os.path.exists(log_filename) and log_restart:
        os.remove(log_filename)

    add_file_handler(log_file_level, log_filename, str_format=str_format, date_format=date_format,
                     formatter=formatter, log_filter=log_filter)

    if log_history:
        base_name = os.path.basename(log_filename).split('.')[0] + '_%s' % datetime_to_str(
            str_format='%Y-%m-%d_%H-%M-%S')
        history_log = os.path.join(os.path.dirname(log_filename), 'history', base_name + '.log')
        add_file_handler(log_file_level, history_log, str_format=str_format, date_format=date_format,
                         log_filter=log_filter)

    silence_module_logging(silence_modules)


def add_file_handler(log_file_level, log_filename, str_format=None, date_format=None, formatter=None, log_filter=None):
    """
    :param log_filename:
    :param log_file_level   str of the log level to use on this file
    :param str_format:      str of the logging format
    :param date_format:     str of the date format
    :param log_restart:     bool if True the log file will be deleted first
    :param log_history:     bool if True will save another log file in a folder called history with the datetime
    :param formatter:       logging.Format instance to use
    :param log_filter:      logging.filter instance to add to handler
    :return:                None
    """
    formatter = formatter or SeabornFormatter(str_format=str_format, date_format=date_format)
    mkdir_for_file(log_filename)

    handler = logging.FileHandler(log_filename)
    add_handler(log_file_level, handler, formatter, log_filter=log_filter)


def add_handler(log_handler_level, handler, formatter=None, log_filter=None):
    """
    :param log_handler_level:   str of the level to set for the handler
    :param handler:             logging.Handler handler to add
    :param formatter:           logging.Formatter instance to use
    :param log_filter:          logging.filter instance to add to handler
    :return:                    None
    """
    handler.setLevel(log_handler_level)
    if formatter is not None:
        handler.setFormatter(formatter)
    if log_filter is not None:
        handler.addFilter(log_filter)
    log.addHandler(handler)


def set_module_log_level(modules=None, log_level=logging.WARNING):
    """
        This will raise the log level for the given modules
        in general this is used to silence them
    :param modules:     list of str of module names ex. ['requests']
    :param log_level:   str of the new log level
    :return:            None
    """
    modules = modules or []
    if not isinstance(modules, list):
        modules = [modules]
    for module in modules:
        logging.getLogger(module).setLevel(logging.WARNING)


silence_module_logging = set_module_log_level


def smoke_test():
    import requests
    log_file = os.path.join(os.path.split(__file__)[0], '_test.log')
    SeabornFormatter(relative_pathname="/seaborn/seaborn/").setup_logging(log_filename=log_file,
                                                                          silence_modules=['requests'],
                                                                          log_level='TRACE',
                                                                          log_stdout_level='TRACE')
    msg = "Test: Hello World (Logger Worked)"
    log.trace(msg)
    test_exclusion = requests.get('http://google.com')
    logged_message = open(log_file, 'r').read()
    assert logged_message.strip().endswith(msg), 'Bad Log Message: %s' % logged_message


if __name__ == '__main__':
    smoke_test()
