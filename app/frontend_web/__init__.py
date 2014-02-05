#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
#************************
#AUTHOR:
__author__='Asmaa'
#************************
#DESCRIPTION:   This is the __init__.py file for launching the back-end webservices for Maven Medical.
#               If you create new sub-modules under the maven/app/frontend/ directory, make sure you
#               properly register the module's blueprints with the "frontend" Flask application
#************************
#ASSUMES:       configuration data from app/config.py
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-1
#*************************************************************************

from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy


# Define the WSGI application object that will handle the frontend webservice
frontend_web = Flask(__name__)

# Configurations
frontend_web.config.from_object('dbconfig')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(frontend_web)

# HTTP error handling
@frontend_web.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

#**************************************************************************
# IMPORT AND REGISTER THE BLUEPRINTS FOR NEW FRONTEND MODULE BELOW
#**************************************************************************
from frontend_web.module_alerthistory.controllers import web as web_module

frontend_web.register_blueprint(web_module)

#For testing purposes, using SQLAlchemy to create a sqlite3 database file
#db.create_all()
#db_engine = db.create_engine()