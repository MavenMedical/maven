#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
#************************
#AUTHOR:
__author__='Asmaa AlJuhani'
#************************
#DESCRIPTION:
# This Class is to access the maven logging database and grab information
# to be displayed in the web content
#************************
#NOTES:
#
#************************
#ASSUMES:
# DB Config in maven configration file (currently on app.frontend_web.dbconfig.py)
# We are getting the context as parameters in the URL
#************************
#SIDE EFFECTS:
#************************
#LAST MODIFIED FOR JIRA ISSUE: MAV-20
#*************************************************************************


# Import DB URI
from app.dbconfig import SQLALCHEMY_DATABASE_URI as dburi
from sqlalchemy import create_engine as ce
from sqlalchemy.sql import text

class DB:
    """ Allow you to access data from maven database
    """

    # connect to db
    def connect(self):
        # create the Engine
        self.eng  = ce(dburi)
        #make the connection
        self.conn = self.eng.connect()


    # Get patient data given an ID
    def get_patient(self, pid):
        """
        return patient information
        name , sex, birth
        """
        sql = text('SELECT * FROM patient WHERE pat_id = :id')
        return self.conn.execute(sql , id=pid).fetchall()


    def get_pat_alerts(self, pat_id ):
        """
        return patient alerts given pat_id , prov, dep
        """
        #sql = text('SELECT * FROM alert WHERE pat_id = :id and prov= :provider and dep= :department')
        #return self.conn.execute(sql, id=pat_id, provider=prov, department=dep ).fetchall()
        sql = text('SELECT * FROM alert WHERE pat_id = :id')
        return self.conn.execute(sql, id=pat_id).fetchall()

    def get_prov_alerts(self,prov):
        """
        return a provider alerts given prov_id
        """
        sql = text('SELECT * FROM alert WHERE prov_id = :provider')
        return self.conn.execute(sql, provider=prov).fetchall()


    def get_dep_alerts(self,dep):
        """
        return all providers' alerts given a department
        """
        sql = text('SELECT * FROM alert WHERE dep= :department')
        return self.conn.execute(sql, department=dep ).fetchall()

    def get_all_alerts(self):
        """
        return all alerts, can be used for administrative level
        """
        sql = text('SELECT * FROM alert')
        return self.conn.execute(sql).fetchall()


    def get_alerts(self, args):
        """
        return alerts depending on the given args
        """
        if 'pat' in args:
            return self.get_pat_alerts(args['pat'])
        elif 'prov' in args:
            return self.get_prov_alerts(args['prov'])
        elif 'dep' in args:
            return self.get_dep_alerts(args['dep'])
        elif 'admin' in args:
            return self.get_all_alerts()

