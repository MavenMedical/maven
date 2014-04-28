##############################################################################
#  Copyright (c) 2014 - Maven Medical
#
#
#  Description: Searches subdirectories for files of the form unit_test_*.py
#               Runs the file, and outputs "<filename> passed"
#               or "<filename> <exception text>"
#               or "<filename> <diff>" (if s/py/output/ exists and differs)
#               
#  Author: Tom DuBois
#  Assumes: 
#  Side Effects: Creates a log of unit test results
#  Last Modified:
##############################################################################

import fnmatch
import os
import importlib
import re
import traceback
import difflib
import subprocess
import maven_config
import maven_logging
import time
from sys import exit
maven_logging.DEBUG = maven_logging.results_var_log
maven_logging.WARN = maven_logging.results_var_log
maven_logging.INFO = maven_logging.results_var_log
maven_logging.ERROR = maven_logging.results_var_log
maven_logging.PRINT = maven_logging.results_var_log_no_label


def find_files(directory, pattern):
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, pattern):
            yield os.path.join(root, filename)

passing = True

for f in find_files('.', 'unit_test_*.bash'):
    maven_logging.clear_results()
    try:
        print("TESTING: "+f)
        test_output = subprocess.check_output([f], timeout=5).decode('utf-8').strip()
        #print(test_output)
        try:
            with open(re.sub('bash$', 'output', f),'r') as golden:
                gold = golden.read().strip()
                #print("gold: "+gold+"G")
                diff = difflib.unified_diff(gold.splitlines(True), test_output.splitlines(True))
                d = ''.join(diff)
                if not d == '':
                    print(d)
                    print("FAILED: "+f)
                    passing = False
                else:
                    print("PASSED: "+f)
        except FileNotFoundError:
            print("PASSED: "+f)
            pass
    except Exception:
        traceback.print_exc()
        print("FAILED: "+f)
        #print('\n'.join(traceback.format_exc().split('\n')[14:]))
        passing = False

for f in find_files('.', 'unit_test_*.py'):
    mod = re.sub('/', '.', f[2:-3])
    maven_logging.clear_results()
    try:
        print("TESTING: "+f)
        test = importlib.import_module(mod,)
        try:
            with open(re.sub('py$', 'output', f)) as golden:
                gold = golden.read().strip()
                #print("gold: "+gold+"G")
                diff = difflib.unified_diff(gold.splitlines(True), maven_logging.get_results().splitlines(True))
                d = ''.join(diff)
                if not d == '':
                    print(d)
                    print("FAILED: "+mod)
                    passing = False
                else:
                    print("PASSED: "+mod)
        except FileNotFoundError:
            print("PASSED: "+mod)
            pass
    except Exception:
        print('\n'.join(traceback.format_exc().split('\n')[14:]))
        print("FAILED: "+mod)
        passing = False

if passing:
    exit(0)
else:
    exit(-1)
