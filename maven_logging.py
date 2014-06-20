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
import time
import os

def _not_implemented(x):
    raise NotImplementedError("This type of logging was not defined in the config file")


def no_logging(x):
    pass

_results = ""

if not 'MAVEN_TESTING' in os.environ:

    def stdout_log_with_time(x):
        called_as = traceback.extract_stack()[-2]
        called_as = str((called_as[0].split('/')[-1], called_as[1], called_as[2]))
        print("%s %f: %s" % (called_as, time.time(),x))
        
    def stdout_log(x):
        called_as = traceback.extract_stack()[-2]
        called_as = str((called_as[0].split('/')[-1], called_as[1], called_as[2]))
        print("%s: %s" % (called_as, x))
        
    def stdout_log_no_label(x):
        print(x)
        
    def results_var_log(x):
        global _results
        called_as = traceback.extract_stack()[-2]
        called_as = str((called_as[0].split('/')[-1], called_as[1], called_as[2]))
        _results += "%s: %s\n" % (called_as, x)


    def results_var_log_no_label(x):
        global _results
        _results += "%s\n" % x

else:
    stdout_log_with_time=no_logging
    stdout_log_no_label=no_logging
    stdout_log=no_logging
    results_var_log_no_label=no_logging
    results_var_log=no_logging


def get_results():
    return _results.strip()


def clear_results():
    global _results
    _results = ""

def database_log(x):
    raise NotImplementedError("No database logging capability is implemented")

PRINT = stdout_log_no_label
DEBUG = no_logging
INFO = stdout_log
WARN = stdout_log
ERROR = stdout_log

