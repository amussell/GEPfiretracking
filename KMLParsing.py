from shapely.geometry import Polygon
from io import StringIO
from xml.dom.minidom import parseString
from zipfile import ZipFile
import math

#
# Author: jbeezley
# Source: https://gist.github.com/jbeezley/3442777
# Contributors: amussell, noahpoulin
#
# This code parses kml documents to read polygon GIS data into a python object
# the readPoly(filename) function can be used to get a generator of polygon info from
# a kml file.
#
# For GEP fire tracking this code was modified to use the shapely library for Polygons
#

kmlstr = \
    '''<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://earth.google.com/kml/2.0">
    <Document>
    <name>Polygon: %s</name>
      <open>1</open>
      %s
    </Document>
    </kml>'''

polystr = \
    '''     <Placemark>
             <name>%i</name>
             <Polygon>
               <altitudeMode>clampedToGround</altitudeMode>
               <outerBoundaryIs>
               <LinearRing>
                 <coordinates>
                 %s
                 </coordinates>
               </LinearRing>
               </outerBoundaryIs>
             </Polygon>
           </Placemark>'''


def openKMZ(filename):
    zip = ZipFile(filename)
    for z in zip.filelist:
        if z.filename[-4:] == '.kml':
            fstring = zip.read(z)
            break
    else:
        raise Exception("Could not find kml file in %s" % filename)
    return fstring


def openKML(filename):
    try:
        fstring = openKMZ(filename)
    except Exception:
        fstring = open(filename, 'r').read()
    return parseString(fstring)

#
# Reads out placemark info from kml in the following format (polygonPoints, tags)
# where polygonPoints is a list the points that define the landmark boundary. Tags
# is a dictionary that maps the each subtags name to the string it surrounds. The sub
# tags read are: <name>, <description>, <TimeSpan> (actually two subtags of TimeSpan: <begin> and <end>), and <TimeStamp>.
#
# For GEPFiretracking the only tags needed is <description> and <name>
#
def readPoly(filename):
    def parseData(d):
        dlines = d.split()
        poly = []
        for l in dlines:
            l = l.strip()
            if l:
                point = []
                for x in l.split(','):
                    point.append(float(x))
                poly.append(point[:2])
        return poly

    xml = openKML(filename)
    nodes = xml.getElementsByTagName('Placemark')
    desc = {}
    for n in nodes:
        names = n.getElementsByTagName('name')
        try:
            desc['name'] = names[0].childNodes[0].data.strip()
        except Exception:
            pass

        descriptions = n.getElementsByTagName('description')
        try:
            desc['description'] = descriptions[0].childNodes[0].data.strip()
        except Exception:
            pass

        times = n.getElementsByTagName('TimeSpan')
        try:
            desc['beginTime'] = times[0].getElementsByTagName('begin')[0].childNodes[0].data.strip()
            desc['endTime'] = times[0].getElementsByTagName('end')[0].childNodes[0].data.strip()
        except Exception:
            pass

        times = n.getElementsByTagName('TimeStamp')
        try:
            desc['timeStamp'] = times[0].getElementsByTagName('when')[0].childNodes[0].data.strip()
        except Exception:
            pass

        polys = n.getElementsByTagName('Polygon')
        for poly in polys:
            invalid = False
            c = n.getElementsByTagName('coordinates')
            if len(c) != 1:
                #print('invalid polygon found')
                continue
            if not invalid:
                c = c[0]
                d = c.childNodes[0].data.strip()
                data = parseData(d)
                yield (data, desc)


def latlon2meters(p):
    pi2 = 2. * math.pi
    reradius = 1. / 6370000
    alat = 0
    alon = 0
    for i in p:
        alon = alon + i[0]
        alat = alat + i[1]
    lon_ctr = alon / len(p)
    lat_ctr = alat / len(p)
    unit_fxlat = pi2 / (360. * reradius)
    unit_fxlon = math.cos(lat_ctr * pi2 / 360.) * unit_fxlat

    q = []
    olon = p[0][0]
    olat = p[0][1]
    for i in p:
        q.append(((i[0] - olon) * unit_fxlon, \
                  (i[1] - olat) * unit_fxlat))
    return q

def squaredmeterstoacres(meterssquared):
    meterssquaredperacre = 4046.8564224000
    return meterssquared/meterssquaredperacre

def polyStats(p):
    pm = Polygon(latlon2meters(p))
    area = squaredmeterstoacres(pm.area)
    numpts = len(p)
    pl = Polygon(p)
    center = pl.centroid

    stat = \
        {'vertices': '%i' % numpts,
         'center': '(%f , %f)' % (center.x, center.y),
         'area': '%f acre' % (area)}
    return stat


def makepoly(p):
    return Polygon(p)


def intersect(p1, p2):
    q1 = makepoly(p1)
    q2 = makepoly(p2)

    q = q1 & q2

    return q


def get_area(p):
    q = makepoly(p)
    return p.area()


def write_poly(p, fname):
    if isinstance(fname, str):
        f = open(fname, 'w')
    else:
        f = fname
    for i in p:
        f.write('%19.16f,%19.16f,0.\n' % (i[0], i[1]))
    f.flush()


def read_poly(fname):
    if isinstance(fname, str):
        f = open(fname, 'r')
    else:
        f = fname
    s = f.readlines()
    p = []
    for i in s:
        i = i.strip()
        j = i.split(',')
        p.append((float(j[0]), float(j[1])))
    return p


def poly2kmz(pp, fname):
    strs = []
    i = 0
    for p in pp:
        i = i + 1
        f = StringIO()
        write_poly(p, f)
        strs.append(polystr % (i, f.getvalue()))
    s = '\n'.join(strs)
    s = kmlstr % (fname, s)
    open(fname, 'w').write(s)