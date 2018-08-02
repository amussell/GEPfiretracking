from CountyFireLandHelpers import intersectOrIn
import pandas as pd
from shapely.geometry import Polygon

class Fire:
    lands = []
    year = -1
    acres = -1
    points = []

    def __init__(self,xmlOutput):
        def parseTableForAttribute(table,attributeString):
            for i, row in enumerate(table[0]):
                if row == attributeString:
                    return table[1][i]

        def parseDescription(desc):
            tables = pd.read_html(desc)
            self.year = parseTableForAttribute(tables[0],"FIRE_YEAR")
            self.acres = parseTableForAttribute(tables[0],"GIS_ACRES")

        self.lands = xmlOutput[0]
        parseDescription(xmlOutput[1]['description'])
        self.points = xmlOutput[0]
        self.poly = Polygon(self.points)


    def findLandsInFire(self,landList):
        for land in landList:
            if intersectOrIn(self.poly,land.poly):
                self.lands.append(land)