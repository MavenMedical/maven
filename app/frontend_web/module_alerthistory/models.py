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
#************************
#ASSUMES:
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-20
#*************************************************************************

# Import the database object (db) from the backend application module
from app.frontend_web import db

# Define a base model for other database tables to inherit
class Base(db.Model):

    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())

# Basic User model for scaffolding authentication needed for the web-services
class User(Base):

    __tablename__ = 'auth_user'

    # User Name
    name    = db.Column(db.String(128),  nullable=False)

    # Identification Data: email & password
    email    = db.Column(db.String(128),  nullable=False,
                                            unique=True)
    password = db.Column(db.String(192),  nullable=False)

    # Authorisation Data: role & status
    role     = db.Column(db.SmallInteger, nullable=False)
    status   = db.Column(db.SmallInteger, nullable=False)

    # New instance instantiation procedure
    def __init__(self, name, email, password):

        self.name     = name
        self.email    = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % (self.name)


class Alert(Base):

    __tablename__ = 'alert'

    #Patient Id
    pid            = db.Column(db.String(128),  nullable=False)

    #User Id
    user_id        = db.Column(db.String(128),  nullable=False)

    #Encounter Id - primary key
    encounter_id   = db.Column(db.Integer, primary_key=True)

    #Department
    dep            = db.Column(db.String(128),  nullable=False)

    encounter_date = db.Column(db.DateTime)
    alert_date     = db.Column(db.DateTime,  default=db.func.current_timestamp())
    orderable      = db.Column(db.String(128))
    provider       = db.Column(db.String(128))
    outcome        = db.Column(db.String(128))


    # New instance instantiation procedure
    def __init__(self, pid, user_id, encounter_id, dep, encounter_date, alert_date, orderable, provider, outcome ):

        self.pid            = pid
        self.user_id        = user_id
        self.encounter_id   = encounter_id
        self.dep            = dep
        self.encounter_date = encounter_date
        self.alert_date     = alert_date
        self.orderable      = orderable
        self.provider       = provider
        self.outcome        = outcome



    def __repr__(self):
        return '<Alerts %r>' % (self.encounter_id)


class Patient(db.Model):

    __tablename__ = 'patient'

    pat_id  = db.Column(db.String(128), primary_key=True)
    birth_month = db.Column(db.String(128))
    sex     = db.Column(db.String(128))
    mrn     = db.Column(db.String(128))
    patname = db.Column(db.String(128))
    cur_pcp_prov_id = db.Column(db.String(128))

    # New instance instantiation procedure
    def __init__(self, pat_id,birth_month, sex, mrn, patname, cur_pcp_prov_id):

        self.pat_id = pat_id
        self.birth_month = birth_month
        self.sex = sex
        self.mrn = mrn
        self.patname = patname
        self.cur_pcp_prov_id = cur_pcp_prov_id

    def __repr__(self):
        return '<Patient %r>' % (self.pat_id)



