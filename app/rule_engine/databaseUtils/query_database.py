#*************************************************************************
#Copyright (c) 2014 - Maven Medical
#
# AUTHOR: Aidan Fowler
# DESCRIPTION: class to query database
# ASSUMES: we have a valid cursor to pass into this class
# SIDE EFFECTS: None
# LAST MODIFIED FOR JIRA ISSUE: MAV-40 Wednesday February 12th
#*************************************************************************


def query_db_multiple(query,cursor,Logger):
    #Query the database, return all results
    results = []
    Logger.log("Query: " + query)
    cursor.execute(query)
    for res in cursor:
        results.append(res)
    return results