####################################################################################################
#  Copyright (c) 2014 - Maven Medical
#
#  Description: database connection and query utilities
#  Author: Aidan Fowler
#  Assumes: In order to connect to and query the database, the following steps
#           must be followed in order:
#
#           1. Connect to the database -> call connect()
#           2. Create a cursor -> call create_cursor()
#           3. Query the databse -> call query_database(queryText,queryMapping (optional))
#               - If you want to create an object that maps keys to result values, you can pass
#                 in a list of key values that should be in the same order as the query parameters
#                 EX: query_database("SELECT KEY1,KEY2,KEY3 FROM TABLE;",['KEY1','KEY2',"KEY3'])
#           After you are done querying and do not need the connection:
#           4. Destroy the cursor -> destroy_cursor()
#           5. Disconnect from the database -> disconnect() Note:
#
#           Note: this class mandates that there is only ever one active cursor because they are not
#                 thread safe.
#
# Side Effects:
#  Last Modified: FOR JIRA ISSUE: MAV-70 Wednesday February 19th
#####################################################################################################

import psycopg2, asyncio
from app.database_utils.dbconfig import CONNECTION_STRING

#TODO currently all of these calls are blocking
#TODO use asyncio to make non-blocking calls to db that return a future
#TODO Refactor asyncio calls on Monday February 24th with Yuki

class DatabaseUtility():

    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        if (self.connection == None):
            self.connection = psycopg2.connect(CONNECTION_STRING)
        else:
            raise RuntimeError("The connection to the database has already been established, "
                               "if you want to start a new connection, you must call disconnect()")

    def disconnect(self):
        if (self.connection != None):
            if (self.cursor != None):
                self.destroy_cursor()
            self.connection.close()
            self.connection = None
        else:
            raise RuntimeError("You are not connected to the database, "
                               "try using the connect() method before trying to disconnect")
    def create_cursor(self):
    #cursors in psycopg2 are NOT thread safe. This method makes sure that we are ever only working with one cursor
        if (self.connection != None):
            if (self.cursor == None):
                self.cursor =  self.connection.cursor()
            elif (self.cursor != None):
                raise RuntimeError("You have already created a cursor, if you want a new one, you must "
                                   "first call destroy_cursor()")
        else:
            raise RuntimeError("You are not connected to the database, "
                               "try using the connect() method before trying to create a cursor")

    def destroy_cursor(self):
        if (self.connection != None):
            if (self.cursor != None):
                self.cursor.close()
                self.cursor = None
            else:
                raise RuntimeError("The cursor you are trying to destroy is null")
        else:
            raise RuntimeError("You are not connected to the database, and therefore can not destroy a cursor")


    #Blocking read from the database
    def query_database_read_blocking(self,query,queryMap=None):
        loop = asyncio.get_event_loop()
        future = asyncio.Future()
        asyncio.Task(self.__query_database_read(future,query,queryMap))
        loop.run_until_complete(future)
        return (future.result())

    #Non Blocking read from the database
    def query_database_read_non_blocking(self,query,queryMap=None):
        #TODO implement this method
        return

    #Blocking write to the database
    def query_database_write_blocking(self,query):
        loop = asyncio.get_event_loop()
        future = asyncio.Future()
        asyncio.Task(self.__query_database_write(future,query))
        loop.run_until_complete(future)

    #Non Blocking write to the database
    def query_database_write_non_blocking(self,query):
        #TODO implement this method
        return

    #This private method gets called when we want to select from the database and return values
    @asyncio.coroutine
    def __query_database_read(self,future,query,queryMap=None):
        #queryDb has two options, one is a normal query where the results will be returned in a list
        #The other option is to call a query with a predefined mapping array so that we can
        #create a response object that maps names with results

        if (self.connection == None):
            raise RuntimeError("You are not connected to the database, try calling connect()")

        if (self.cursor == None):
            raise RuntimeError("You have not created a cursor to execute this query, try calling create_cursor()")

        results = []
        singleResult = {}

        self.cursor.execute(query)
        self.connection.commit()

        for res in self.cursor:
            if (queryMap == None):
                #Run the query without a result mapping, just send the data back in a list
                results.append(res)
            else:
                i=0
                for value in res:
                    #Predefined result mapping for query results
                    singleResult[queryMap[i]] = str(value)
                    i+=1
                results.append(singleResult)

        future.set_result(results)


    #This private method gets called when we want to execute a query with no return values (INSERT, DELETE, UPDATE)
    @asyncio.coroutine
    def __query_database_write(self,future, query):

        if (self.connection == None):
            raise RuntimeError("You are not connected to the database, try calling connect()")

        if (self.cursor == None):
            raise RuntimeError("You have not created a cursor to execute this query, try calling create_cursor()")

        self.cursor.execute(query)
        self.connection.commit()
        future.set_result('Future is done!')

    #This method allows us to generate a list of columns we would like to retrieve from a select query map (defined in dbconfig)
    #All this is really doing is generating a string that is a list of the column names we want to retrieve.
    #Example: if we have defined our result map as EXAMPLE_MAP = ["col1","col2","col3"], this method returns "col1,col2,col3"
    #And we can run query: query_database_select("SELECT %s FROM Table" % select_rows_from_map(EXAMPLE_MAP),EXAMPLE_MAP)
    #And we will get back result= [{col1: val1, col2: val2, col3: val3}]
    def select_rows_from_map(self,map):
        params = ""
        for x in range (len(map)):
            params= params+map[x]+","
        return params[:-1]


