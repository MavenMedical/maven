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

MavenConfig = {}

if isfile('/etc/mavenmedical/maven.config'):
    config = ConfigParser()
    config.read(['/etc/mavenmedical/maven.config'])
    for section in config.keys():
        MavenConfig[section] = dict(config.items(section))
    dbconnection = MavenConfig['global'].get('dbconnection', None)
    dbhost = MavenConfig['global'].get('dbhost', None)
    reporterhost = MavenConfig['global'].get('reporterhost', None)
    http_addr = MavenConfig['global']['http_addr']
    recaptcha_public = MavenConfig['global'].get('recaptcha_public', '')
    recaptcha_private = MavenConfig['global'].get('recaptcha_private', '')
    wrap_exception = MavenConfig['global'].get('wrap_exception', None)
    sslcrtfile = None
    sslkeyfile = None
    sslkeypassword = None
    sslcadata = None
    sslcapath = None
    sslcafile = None

else:
    dbconnection = ("dbname=%s user=%s password=%s host=%s port=%s" % ('maven', 'maven', 'temporary', 'localhost', '5432'))

    dbhost = 'localhost'
    reporterhost = None
    wrap_exception = None
    http_addr = 'http://localhost'
    recaptcha_public = '6Lcy3vwSAAAAAD0uy8wRFxf7rO60sPwx5OA5AGij'
    recaptcha_private = '6Lcy3vwSAAAAAN-X2jIbEqKh7NFwpIux8WRS8Lby'
    sslcrtfile = None
    sslkeyfile = None
    sslkeypassword = None
    sslcadata = None
    sslcapath = None
    sslcafile = None


class InvalidConfig(Exception):
    pass
