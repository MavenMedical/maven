##############################################################################
#  Copyright (c) 2014 - Maven Medical
#
#
#  Description: Empty module to hold global state as maven_config.MavenConfig
#               accessible by get(instance name, parameter)
#               
#  Author: Tom DuBois
#  Assumes: 
#  Side Effects: 
#  Last Modified:
##############################################################################
from configparser import ConfigParser
from os.path import isfile
MavenConfig={}

if isfile('/etc/mavenmedical/maven.config'):
    config = ConfigParser()
    config.read(['/etc/mavenmedical/maven.config'])
    for section in config.keys():
        MavenConfig[section] = dict(config.items(section))
    dbconnection = MavenConfig['global']['dbconnection']
    http_addr = MavenConfig['global']['http_addr']
else:
    dbconnection = ("dbname=%s user=%s password=%s host=%s port=%s" % ('maven', 'maven', 'temporary', 'localhost', '5432'))
    
    http_addr = 'http://localhost'


class InvalidConfig(Exception):
    pass

