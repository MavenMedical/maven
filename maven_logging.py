##############################################################################
#  Copyright (c) 2014 - Maven Medical
#
#
#  Description: Supports different types of logging
#
#  Author: Tom DuBois
#  Assumes:
#  Side Effects:
#  Last Modified:
##############################################################################

import traceback
import inspect
import os
import os.path
import logging
import logging.config
import sys
import io
import time
import asyncio

_results = io.StringIO()


def get_results():
    return _results.getvalue().strip()


def clear_results():
    _results.seek(0)
    _results.truncate(0)


def set_debug(filename=None):
    modulename = inspect.getmodule(inspect.stack()[1][0]).__name__
    if modulename == '__main__':
        log = logging.root
    else:
        log = logging.getLogger(modulename)
    if filename:
        handler = logging.FileHandler(filename)
    else:
        handler = logging.StreamHandler(sys.stderr)
    log.setLevel(root.getEffectiveLevel())
    handler.setFormatter(logging.Formatter(
        '%(asctime)s     %(levelname)s\t%(process)d\t%(filename)s:%(lineno)d\t%(message)s'))
    log.addHandler(handler)


def trace(write=print, initial=False, timing=False):

    """
    Decorator to log the inputs and results of a function.  After the function completes, it
    will output the function, its arguments, and its return value
    :param write: the function to send the strings containing logging information
                  the default value is "print" however "logging.root.debug" or similar
                  are also good choices
    :param initial: a boolean, if true it will log when the function starts as well
                    as when it finishes
    :param timing: a boolean, if true the function and return value will be printed
                   along with the amount
                   of wall clock time it took in seconds
    usage is: @trace()
              def somefunc(arg):
                  return True

    when calling somefunc(1), it will print "somefunc((1,), {}) -> True"
    """
    def trace_inner(func):
        def inner(*args, **kwargs):
            if initial:
                write("%s(%s, %s) started" % (func.__name__, args, kwargs))
            if timing:
                starttime = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                resultstring = str(result)
                ret = lambda: result
            except Exception as e:
                resultstring = "exception:\n" + traceback.format_exc()
                ex = e

                def ret():
                    raise ex
            if timing:
                totaltime = time.perf_counter() - starttime
                write("%s(%s, %s) -> %s took %s" % (func.__name__, args, kwargs,
                                                    resultstring, totaltime))
            else:
                write("%s(%s, %s) -> %s" % (func.__name__, args, kwargs, resultstring))
            return ret()
        return inner
    return trace_inner


def coroutine_trace(write, initial=None, timing=False):
    """
    The semantics are the same as trace, but for coroutines
    """
    def trace_inner(func):
        co_func = asyncio.coroutine(func)

        @asyncio.coroutine
        def inner(*args, **kwargs):
            if initial:
                write("%s(%s, %s) started" % (func.__name__, args, kwargs))
            if timing:
                starttime = time.perf_counter()
            try:
                result = yield from co_func(*args, **kwargs)
                resultstring = str(result)
                ret = lambda: result
            except Exception as e:
                resultstring = "exception:\n" + traceback.format_exc()
                ex = e

                def ret():
                    raise ex
            if timing:
                totaltime = time.perf_counter() - starttime
                write("%s(%s, %s) -> %s took %s" % (func.__name__, args, kwargs,
                                                    resultstring, totaltime))
            else:
                write("%s(%s, %s) -> %s" % (func.__name__, args, kwargs, resultstring))
            return ret()

        return inner
    return trace_inner

root = logging.root
if 'MAVEN_TESTING' not in os.environ:

    exename = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    if os.path.isfile('/etc/mavenmedical/logging-%s.config' % (exename,)):
        logging.config.fileConfig('/etc/mavenmedical/logging-%s.config' % (exename,))
    elif os.path.isfile('/etc/mavenmedical/logging.config'):
        logging.config.fileConfig('/etc/mavenmedical/logging.config')
    else:
        root.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '%(asctime)s     %(levelname)s\t%(process)d\t%(filename)s:%(lineno)d\t%(message)s'))
        root.addHandler(handler)
    root.debug('maven_logging started up')
else:
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(_results)
    handler.setFormatter(logging.Formatter('%(message)s'))
    root.addHandler(handler)

PRINT = root.info
DEBUG = root.debug
INFO = root.info
WARN = root.warn
ERROR = root.error
EXCEPTION = root.exception


def get_logger(name=None):
    if name is None:
        modulename = inspect.getmodule(inspect.stack()[1][0]).__name__
        name = modulename

    try:
        logger = logging.getLogger(name=name)
        level = root.getEffectiveLevel()
        logger.setLevel(level)
        return logger
    except:
        raise Exception("Logger needs a configuration record with that name")


def TASK(coroutine):
    stack = [s[1:4] for s in inspect.stack()[1:]]

    @asyncio.coroutine
    def wrapper():
        try:
            yield from coroutine
        except asyncio.CancelledError:
            pass
        except:
            EXCEPTION('Error in asyncio.Task %s' % stack)

    return asyncio.Task(wrapper())


def report(message):
    pass


def wrap_exception():
    global EXCEPTION
    last_exception_map = {}

    url = 'https://hooks.slack.com/services/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'

    import aiohttp
    from datetime import datetime, timedelta
    import socket
    import json
    import sys

    hostname = socket.gethostname() + ' ' + sys.argv[0] + ": "
    old_exception = EXCEPTION

    @asyncio.coroutine
    def msg_to_slack(x):
        resp = yield from aiohttp.request('POST',
                                          url,
                                          data=json.dumps({"text": hostname + x}))
        resp.close()

    def handle_exception(x, post=True):
        old_exception(x)
        if not post:
            return
        if type(x) == list:
            x = tuple(x)
        last = last_exception_map.get(x, datetime.min)
        now = datetime.now()
        if now - last > timedelta(minutes=5):
            last_exception_map[x] = now
            print('firing off message')
            TASK(msg_to_slack(x))
    EXCEPTION = handle_exception
