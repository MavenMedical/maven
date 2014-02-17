#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
#************************
#AUTHOR:
__author__='Asmaa AlJuhani'
#************************
#DESCRIPTION:
#
#
#NOTES:
# When using the SQLAlchemy ORM, the public API for transaction control is via the Session object
#************************
#ASSUMES:
#We are getting the context as parameters in the URL
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-20
#*************************************************************************

# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

# Import password / encryption helper tools
from werkzeug.security import check_password_hash, generate_password_hash

# Import the temp backend database object from the main app module
from app.frontend_web import db

# Import module forms for testing
from app.frontend_web.module_alerthistory.forms import LoginForm

# Import all models
from app.frontend_web.module_alerthistory.models import *


#import DB class
from app.frontend_web.module_alerthistory.dbconnect import *

# Define the blueprint: 'webservice', set its url prefix: app.url/web
web = Blueprint('web', __name__, url_prefix='/web')

# Set the route and accepted methods
@web.route('/signin/', methods=['GET', 'POST'])
def signin():

    # If sign in form is submitted
    form = LoginForm(request.form)

    # Verify the sign in form
    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):

            session['user_id'] = user.id

            flash('Welcome %s' % user.name)

            return redirect(url_for('alerthistory.home'))

        flash('Wrong email or password', 'error-message')

    return render_template("alerthistory/retrieve_alerts.html", form=form)



@web.route('/', methods=['GET', 'POST'])
def showData():

    dbconnect = DB()
    dbconnect.connect()

    args = request.args

    alert = dbconnect.get_alerts(args)

    return render_template("alerthistory/alerthistory.html",
                           alerts = alert)