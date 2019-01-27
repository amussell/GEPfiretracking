from copy import deepcopy
import County
import Fire
import Land
from CountyFireLandHelpers import outputDataToCSV
from KMLParsing import readPoly

fireFile = 'FireHistory.kml'
i = 0
fires = []
for p in readPoly(fireFile):
    fire = Fire.Fire(p)
    i += 1
    fires.append(deepcopy(fire))

countyFile = 'Counties.kml'
i = 0
counties = []
for p in readPoly(countyFile):
    i += 1
    county = County.County(p)
    counties.append(deepcopy(county))

landFile = 'landownership.kml'
lands = []
i = 0
for p in readPoly(landFile):
    i += 1
    land = Land.Land(p)
    lands.append(deepcopy(land))

i = 0
for county in counties:
    i += 1
    county.findFiresInCounty(fires)

i = 0
for fire in fires:
    i += 1
    fire.findLandsInFire(lands)

outputDataToCSV(counties, fires, lands)