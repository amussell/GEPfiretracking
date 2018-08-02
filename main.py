from shapely.geometry import Polygon
from copy import deepcopy
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import csv


from io import StringIO
from xml.dom.minidom import parseString
from zipfile import ZipFile
import math

'''
This is a script to parse polygons contained in a kml or kmz file and print out statistics
about each polygon found.  Currently only simple polygons without holes are supported.

Dependencies:
    Polygon: https://github.com/jraedler/Polygon2

Just run `python polyStats.py <kml file>`.
'''

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

def printpolygon(polygon):
    polygon, desc = polygon
    stats = polyStats(polygon)
    desc.update(stats)
    print('Polygon')
    for d, v in desc.items():
        print('%16s: %s' % (d, v))
    print('')

def getfirewithname(Fires,name):
    for fire in Fires:
        if fire[1]['name'] == name:
            return fire

def getcountywithname(counties,name):
    for county in counties:
        if county[1]['name'] == name:
            return county

def checkIfFireInCountyByName(fires,counties,firename,countyname):
    fire = getfirewithname(fires,firename)
    if fire == None:
        print("ERROR: No such fire with name: " + firename)
    county = getcountywithname(counties,countyname)
    if county == None:
        print("ERROR: No such county with name: " + countyname)
    firePoints = np.array(fire[0])
    countyPoints = np.array(county[0])
    firePoly = Polygon(firePoints)
    countyPoly = Polygon(countyPoints)
    return countyPoly.overlaps(firePoly) or countyPoly.contains(firePoly) or firePoly.contains(countyPoly)

def checkIfFireInCounty(fire,county):
    firePoints = np.array(fire[0])
    countyPoints = np.array(county[0])
    firePoly = Polygon(firePoints)
    countyPoly = Polygon(countyPoints)
    return countyPoly.overlaps(firePoly) or countyPoly.contains(firePoly) or firePoly.contains(countyPoly)

def getPolygon(list,name):
    item = getfirewithname(list,name)
    itemPoints = np.array(item[0])
    return Polygon(itemPoints)

def plotFire(fire):
    firePoints = np.array(fire[0])
    plt.plot(firePoints[:, 0],firePoints[:, 1])

def getAttributeOfFire(fire,attributeString):
    metadata = fire[1]['description']
    tables = pd.read_html(metadata)  # use pandas library to read out tables from an html string to a pandas data frame
    for i, row in enumerate(tables[0][0]):
        if row == attributeString:
            return tables[0][1][i]

def getAcresOfFire(fire):
    return getAttributeOfFire(fire,"GIS_ACRES")

def getYearOfFire(fire):
    return getAttributeOfFire(fire,"FIRE_YEAR")

fname = 'C:\\Users\\AlexMussell\\Desktop\\FirePerimetersHistory- Copy.kml'
i = 0
fires = []
for p in readPoly(fname):
    fires.append(deepcopy(p))
    #printpolygon(p)


fname = 'C:\\Users\\AlexMussell\\Desktop\\counties.kml'
i = 0
counties = []
for p in readPoly(fname):
    counties.append(deepcopy(p))
    #printpolygon(p)

with open('mycsvfile.csv','w', newline='') as f:
    w = csv.writer(f)
    for county in counties:
        print(county[1]['name'])
        w.writerow([county[1]['name']])
        for fire in fires:
            if(checkIfFireInCounty(fire,county)):
                print('\t' + fire[1]['name'] + " " + getYearOfFire(fire))
                w.writerow([' ',fire[1]['name'],getYearOfFire(fire),getAcresOfFire(fire)])

print("Hello")