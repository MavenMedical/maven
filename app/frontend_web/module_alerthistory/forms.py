#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
#************************
#AUTHOR:
__author__='Asmaa'
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

# Import Form and RecaptchaField (optional)
from flask.ext.wtf import Form # , RecaptchaField

# Import Form elements such as TextField and BooleanField (optional)
from wtforms import TextField, PasswordField # BooleanField

# Import Form validators
from wtforms.validators import Required, Email, EqualTo


# Define the login form (WTForms)

class LoginForm(Form):
    email    = TextField('Email Address', [Email(),
                Required(message='Forgot your email address?')])
    password = PasswordField('Password', [
                Required(message='Must provide a password. ;-)')])