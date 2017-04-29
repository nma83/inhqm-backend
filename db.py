import psycopg2
import psycopg2.extras

"""
india=# SELECT *
FROM planet_osm_roads
WHERE planet_osm_roads.way && ST_Transform(
  ST_MakeEnvelope(77.240721, 13.234276, 77.244783, 13.242666, 
  4326),3857)
xmin, ymin, xmax, ymax
"""

"""
 update planet_osm_roads set tags = tags || '"smoothness"=>"good"' ::hstore where osm_id = 373720476;
"""

def tagsDict(x):
    return dict(x[i:i+2] for i in range(0, len(x), 2))
    
def bbox(p1, p2):
    p = [[0, 0], [0, 0]]
    p[0][0] = min(p1[0], p2[0])
    p[0][1] = min(p1[1], p2[1])
    p[1][0] = max(p1[0], p2[0])
    p[1][1] = max(p1[1], p2[1])
    return p

class pgdb:
    _conn = None
    _cur = None
    _qualityIndex = { 'bad': 0, 'intermediate': 1, 'good': 2, 'excellent': 3, 'none': 99 }

    def __init__(self):
        try:
            self._conn = psycopg2.connect("dbname='india' user='postgres' host='localhost' password='toseetosee'")
            psycopg2.extras.register_hstore(self._conn)
            self._cur = self._conn.cursor()
        except:
            print "I am unable to connect to the database"
    
    def getNodes(self, search):
        query = """select name, st_x(st_transform(way, 4674)), st_y(st_transform(way, 4674)) 
                    from planet_osm_point where name ilike %s and place is not null limit 10;"""
        search = search + '%'
        self._cur.execute(query, (search,))
        rows = self._cur.fetchall()
        return rows

    """
    Get all the highways in the bounding box bounds
    """
    def getHighway(self, bounds):
        ret = { 'ways': [], 'quality': 'none' }
        bb = bbox(bounds[0], bounds[1])
        query = """select osm_id, highway, tags from planet_osm_roads 
                    where planet_osm_roads.way && ST_Transform( 
                    ST_MakeEnvelope(%s, %s, %s, %s, 4326), 3857) and planet_osm_roads.highway is not null""" 
        #in ('motorway', 'trunk', 'primary', 'secondary', 'tertiary')"""
        self._cur.execute(query, (bb[0][0], bb[0][1], bb[1][0], bb[1][1]))
        rows = self._cur.fetchall()
        worst = 'none'
        for row in rows:
            node = { 'id': row[0], 'highway': row[1] }
            if 'smoothness' in row[2]:
                node['smoothness'] = row[2]['smoothness']
            else:
                node['smoothness'] = 'none'
            if row[0] not in ret['ways']:
                ret['ways'].append(row[0])
            if self._qualityIndex[worst] > self._qualityIndex[node['smoothness']]:
                worst = node['smoothness']
        ret['quality'] = worst
        return ret
 
    """
    Function called from API to get highways through a route of points
    """
    def waysFromNodes(self, points):
        ways = []
        for n in range(1, len(points)):
            highway = self.getHighway([points[n - 1], points[n]])
            ways.append(highway)
        return ways

    """
    Function called from API to save highways along with quality
    """
    def saveWays(self, ways):
	quality = ways['quality']
        query = """update planet_osm_roads set tags = tags 
                   || '""" + ('"smoothness"=>"%s"' % (quality,)) + """' ::hstore where osm_id in %s"""
        #for way in ways['ways']:
        if len(ways['ways']) > 0:
            self._cur.execute(query, (tuple(ways['ways']),))
            self._conn.commit()

