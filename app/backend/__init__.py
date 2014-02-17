#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
#************************
#AUTHOR:
__author__='Yuki Uchino'
#************************
#DESCRIPTION:   This is the __init__.py file for launching the back-end webservices for Maven Medical.
#               If you create new sub-modules under the maven/app/backend/ directory, make sure you
#               properly register the module's blueprints with the "backend" Flask application
#************************
#ASSUMES:       configuration data from app/config.py
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-1
#*************************************************************************

from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from app.configs import devel_config as config
from werkzeug.contrib.fixers import ProxyFix

# Define the WSGI application object that will handle the backend webservice
backend = Flask(__name__)

# Configurations
backend.config.from_object(config)

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(backend)

# HTTP error handling
@backend.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

#**************************************************************************
# IMPORT AND REGISTER THE BLUEPRINTS FOR NEW BACKEND MODULE BELOW
#**************************************************************************
from app.backend.module_webservice.controllers import webservice as webservice_module
backend.register_blueprint(webservice_module)

#For testing purposes, using SQLAlchemy to create a sqlite3 database file
db.create_all()