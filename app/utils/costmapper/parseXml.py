from xml.dom import minidom
import psycopg2
import sys

def parseXML():
	con = None
	
	try:
		con = psycopg2.connect(database='maven01', user='maven', password='whoanelly')
		cur = con.cursor()
		cur.execute('SELECT version()')
		ver = cur.fetchone()
		print ver
	except psycopg2.DatabaseError, e:
		print 'Error %s' % e
		sys.exit(1)
	
	finally:
		if con:
			con.close()	
	#import xml doc
	xmldoc = minidom.parse('GetEncounterCharges_Response.xml');
	#create list of elements with tag 'BillAreaID'
	id = xmldoc.getElementsByTagName('BillAreaID');
	#print the value inside the first BillAreaID element
	print id[0].childNodes[0].nodeValue 
parseXML()
