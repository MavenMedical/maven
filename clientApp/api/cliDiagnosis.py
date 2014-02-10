
__author__ = 'dave'
import psycopg2
import cliConfig

class cliDiagnosis:
    """*************************************************************************
    *  Copyright (c) 2014 - Maven Medical
    * __________________
    *
    *  Description: This class represents a diagnosis record from the EMR system.
    *               It lives on the non-cloud system
    *  Author: Dave
    *  Assumes: xml Format  - Check
    *  Side Effects: None
    *  Last Modified: MAV-35
    * *************************************************************************"""

    icd9List = ""
    icd10List = ""
    snomedConcepts = ""
    name = ""
    imoId = ""
    imoTermId = ""

    def __init__(self, dxInternalId, config):
        con=None
        try:
            con = psycopg2.connect(database=config.db, user=config.dbUser, password=config.dbPassword, host=config.dbHost)
            cur = con.cursor()
            cur.execute('SELECT current_icd9_List,current_icd10_list,concept_id,dx_name,dx_imo_id,imo_term_id from diagnosis where dx_id=%s',(dxInternalId,))
            row = cur.fetchone()
            self.icd9List = row[0]
            self.icd10List = row[1]
            self.snomedConcepts = row[2]
            self.name = row[3]
            self.imoId = row[4]
            self.imoTermId = row[5]

        except psycopg2.DatabaseError as e:
            raise 'Error %s' % e

        finally:
            if con:
                con.close()

            self.icd9List = row[0]