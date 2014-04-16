__author__ = 'dave'


class cliProcOrder:
    """*************************************************************************
    *  Copyright (c) 2014 - Maven Medical
    * __________________
    *
    *  Description: This class represents a procedure Order from the EMR system.
    *               It lives on the non-cloud system
    *  Author: Dave
    *  Assumes: xml Format  - Check
    *  Side Effects: None
    *  Last Modified: MAV-35
    * *************************************************************************"""
    Code = ""
    CodeType = ""
    procName = ""
    procType = ""

    def __init__(self, name, code, codetype, proctype):
        self.procName = name
        self.Code = code
        self.CodeType = codetype
        self.procType = proctype
