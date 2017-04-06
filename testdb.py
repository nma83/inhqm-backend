#
# Small script to show PostgreSQL and Pyscopg together
#

import psycopg2

try:
    conn = psycopg2.connect("dbname='india' user='postgres' host='localhost' password='toseetosee'")
except:
    print "I am unable to connect to the database"

cur = conn.cursor()
try:
    cur.execute("""select * from planet_osm_ways where 906647023 = any(nodes)""")
except:
    print "Bad query"

rows = cur.fetchall()
print "\nRows: \n"
for row in rows:
    print "   ", row
