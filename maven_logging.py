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

import inspect
import time

def _not_implemented(x):
    raise NotImplementedError("This type of logging was not defined in the config file")


def stdout_log_with_time(x):
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    called_as = calframe[1][4][1]
    called_as = called_as[:(called_as.index('('))]
    print("%s %f: %s" % (called_as, time.time(),x))

def stdout_log(x):
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    called_as = calframe[1][4][1]
    called_as = called_as[:(called_as.index('('))]
    print("%s: %s" % (called_as, x))


def stdout_log_no_label(x):
    print(x)


def no_logging(x):
    pass

_results = ""


def results_var_log(x):
    global _results
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    called_as = calframe[1][4][1]
    called_as = called_as[:(called_as.index('('))]
    _results += "%s: %s\n" % (called_as, x)


def results_var_log_no_label(x):
    global _results
    _results += "%s\n" % x


def get_results():
    return _results.strip()


def clear_results():
    global _results
    _results = ""


def database_log(x):
    raise NotImplementedError("No database logging capability is implemented")


PRINT = stdout_log_no_label
DEBUG = no_logging
INFO = no_logging
WARN = no_logging
ERROR = no_logging

