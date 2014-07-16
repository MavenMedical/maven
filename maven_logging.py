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

_results = io.StringIO()
def get_results():
    return _results.getvalue().strip()

def clear_results():
    _results.seek(0)
    _results.truncate(0)

def get_logger():
    modulename = inspect.getmodule(inspect.stack()[1][0]).__name__
    return logging.getLogger(modulename)

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
    log.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s     %(levelname)s\t%(process)d\t%(filename)s:%(lineno)d\t%(message)s'))
    log.addHandler(handler)
            
root = logging.root
if not 'MAVEN_TESTING' in os.environ:
    if os.path.isfile('/etc/mavenmedical/logging.config'):
        logging.config.fileConfig('/etc/mavenmedical/logging.config')
    else:
        root.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '%(asctime)s     %(levelname)s\t%(process)d\t%(filename)s:%(lineno)d\t%(message)s'))
        root.addHandler(handler)
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

