import cliConfig

__author__ = 'dave'
import hashlib


class obfuscator:
    """*************************************************************************
    *  Copyright (c) 2014 - Maven Medical
    * __________________
    *
    *  Description: This class contains hashing and encryption methods for
    *               de-identifying data.
    *  Author: Dave
    *  Assumes: /var/maven/clientApp/config/maven.config
    *  Side Effects: None
    *  Last Modified: MAV-35
    * *************************************************************************"""

    cfg = cliConfig.CliConfig

    def __init__(self,config):
        self.cfg = config

    def hash(self, inString):
        return hashlib.sha224(inString + self.cfg.sharedSecret).hexdigest()