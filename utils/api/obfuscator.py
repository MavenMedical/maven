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

    def __init__(self, config):
        self.cfg = config

    def hash(self, inString):
        inString = inString.encode('utf-8') + self.cfg.sharedSecret.encode('utf-8')
        return hashlib.sha224(inString).hexdigest()