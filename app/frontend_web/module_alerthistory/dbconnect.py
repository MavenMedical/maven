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
# In this version, it requires to pass the Alerts level (ex: provider, department, admin) as parameter
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


    def get_pat_alerts(self, pat_id , prov, dep):
        """
        return patient alerts given pat_id , prov, dep
        """
        sql = text('SELECT * FROM alert WHERE pat_id = :id and prov= :provider and dep= :department')
        return self.conn.execute(sql, id=pat_id, provider=prov, department=dep ).fetchall()


    def get_providers_alert(self,dep):
        """
        return all providers' alerts given a department
        """
        sql = text('SELECT * FROM alert WHERE dep= :department')
        return self.conn.execute(sql, department=dep ).fetchall()

    def get_alerts(self):
        """
        return all alerts
        """
        sql = text('SELECT * FROM medorder')
        return self.conn.execute(sql).fetchall()
