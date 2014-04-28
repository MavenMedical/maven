
__author__ = 'dave'
import configparser
import os

class CliConfig:
    """*************************************************************************
    *  Copyright (c) 2014 - Maven Medical
    * __________________
    *
    *  Description: This class represents a the client's system configuration.
    *               It lives on the non-cloud system
    *  Author: Dave
    *  Assumes: /var/maven/clientApp/config/maven.config
    *  Side Effects: None
    *  Last Modified: MAV-35
    * *************************************************************************"""

    db = ""
    customerId = ""
    dbHost = ""
    dbUser = ""
    dbPassword = ""
    sharedSecret = ""
    dateFormat=""
    EMR=""

    def __init__(self):
        cfg = configparser.RawConfigParser()
        cfg.read(os.environ['MAVEN_ROOT']+"/clientApp/config/maven.config")
        self.customerId = cfg.get("customer", "id")
        self.db = cfg.get("database", "db")
        self.dbHost = cfg.get("database", "host")
        self.dbUser = cfg.get("database", "user")
        self.dbPassword = cfg.get("database", "pass")
        self.sharedSecret = cfg.get("customer", "sharedSecret")
        self.dateFormat = cfg.get("customer", "dateFormat")
        self.EMR=cfg.get("customer","EMR")
