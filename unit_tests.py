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


def find_files(directory,pattern):
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, pattern):
            yield os.path.join(root, filename)

for f in find_files('.', 'unit_test_*.py'):
    mod = re.sub('/', '.', f[2:-3])
    print(f)
    try:
        test = importlib.import_module(mod,)
        #print("result: "+test.result+"R")
        try:
            with open(re.sub('py$', 'output', f)) as golden:
                gold = golden.read().strip()
                #print("gold: "+gold+"G")
                diff = difflib.unified_diff(gold.splitlines(True), test.result.splitlines(True))
                d = ''.join(diff)
                if not d == '':
                    print(d)
        except FileNotFoundError:
            pass
    except Exception:
        print(traceback.format_exc())
