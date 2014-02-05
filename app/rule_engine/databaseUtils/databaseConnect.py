import psycopg2


def connectToDb(conn_string):
	print ("Connecting to database\n ->%s" % conn_string)
	conn = psycopg2.connect(conn_string)
	cursor = conn.cursor()
	print ("Connected!\n")
	return cursor