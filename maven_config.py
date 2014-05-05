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

MavenConfig={}

dbconnection = ("dbname=%s user=%s password=%s host=%s port=%s" % ('maven', 'maven', 'temporary', 'localhost', '5432')),

http_addr = 'http://localhost'

class InvalidConfig(Exception):
    pass

