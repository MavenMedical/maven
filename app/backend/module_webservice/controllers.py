#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
#************************
#AUTHOR:
__author__='Yuki Uchino'
#************************
#DESCRIPTION:
#
#
#************************
#ASSUMES:
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-1
#*************************************************************************

# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

# Import password / encryption helper tools
from werkzeug.security import check_password_hash, generate_password_hash

# Import the temp backend database object from the main app module
from backend import db

# Import module forms for testing
from backend.module_webservice.forms import LoginForm

# Import module models (User)
from backend.module_webservice.models import User

# Define the blueprint: 'webservice', set its url prefix: app.url/webservice
webservice = Blueprint('webservices', __name__, url_prefix='/')

# Set the route and accepted methods
@webservice.route('/', methods=['GET', 'POST'])
def signin():

    # If sign in form is submitted
    form = LoginForm(request.form)

    # Verify the sign in form
    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):

            session['user_id'] = user.id

            flash('Welcome %s' % user.name)

            return redirect(url_for('webservice.home'))

        flash('Wrong email or password', 'error-message')

    return render_template("webservice/retrieve_cost.html", form=form)