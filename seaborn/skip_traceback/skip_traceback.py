"""
    This will override how traceback works so that it skips certain modules
"""

__author__ = 'Ben Christenson'
__date__ = "11/5/15"
import inspect
import linecache
import traceback
import sys

SKIPPED_PATHS = []
SKIPPED_MODULES = []
ONLY_MODULES = []


def skip_module(*modules):
    """
        This will exclude all of the "modules" from the traceback
    :param modules: list of modules to exclude
    :return:        None
    """
    modules = (modules and isinstance(modules[0], list)) and modules[0] or modules

    for module in modules:
        if not module in SKIPPED_MODULES:
            SKIPPED_MODULES.append(module)
    traceback.extract_tb = _new_extract_tb


def only_module(*modules):
    """
        This will exclude all modules from the traceback except these "modules"
    :param modules: list of modules to report in traceback
    :return:        None
    """
    modules = (modules and isinstance(modules[0], list)) and modules[0] or modules
    for module in modules:
        if not module in ONLY_MODULES:
            ONLY_MODULES.append(module)
    traceback.extract_tb = _new_extract_tb


def skip_path(*paths):
    """
        This will exclude all modules that start from this path
    :param paths: list of str of the path of modules to exclude
    :return:      None
    """
    paths = (paths and isinstance(paths[0], list)) and paths[0] or paths
    for path in paths:
        if not path in SKIPPED_PATHS:
            SKIPPED_PATHS.append(path)
    traceback.extract_tb = _new_extract_tb


def _test_skip_frame(frame):
    try:
        module = inspect.getmodule(frame)
        if ONLY_MODULES and not module in ONLY_MODULES:
            return True
        for path in SKIPPED_PATHS:
            if path in frame.f_code.co_filename.replace('\\', '/'):
                return True
        if module in SKIPPED_MODULES:
            return True
        return False
    except Exception as e:
        return False


def _tb_skipper(tbnext):
    while tbnext is not None:
        if not _test_skip_frame(tbnext.tb_frame):
            yield tbnext
        if tbnext.tb_next is tbnext: break
        tbnext = tbnext.tb_next

    yield None


def _new_extract_tb(tb, limit=None):
    if limit is None:
        if hasattr(sys, 'tracebacklimit'):
            limit = sys.tracebacklimit
    list_ = []
    n = 0
    new_tb_order = _tb_skipper(tb)  # <-- this line added
    tb = next(new_tb_order)
    while tb is not None and (limit is None or n < limit):
        f = tb.tb_frame
        lineno = tb.tb_lineno
        co = f.f_code
        filename = co.co_filename
        name = co.co_name
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        if line:
            line = line.strip()
        else:
            line = None
        list_.append((filename, lineno, name, line))
        tb = next(new_tb_order)  # <-- this line modified, was tb = tb.tb_next
        n += 1
    return list_
