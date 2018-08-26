from CountyFireLandHelpers import intersectOrIn
import pandas as pd
from shapely.geometry import Polygon

class Fire:

    def __init__(self,xmlOutput):
        def parseTableForAttribute(table,attributeString):
            for i, row in enumerate(table[0]):
                if row == attributeString:
                    return table[1][i]

        def parseDescription(desc):
            tables = pd.read_html(desc)
            self.name = xmlOutput[1]['name']
            self.year = parseTableForAttribute(tables[0],"FIRE_YEAR")
            self.acres = parseTableForAttribute(tables[0],"GIS_ACRES")

        parseDescription(xmlOutput[1]['description'])
        self.points = xmlOutput[0]
        self.poly = Polygon(self.points)
        self.lands = []


    def findLandsInFire(self,landList):
        count = 0
        for land in landList:
            if intersectOrIn(self.poly,land.poly):
                self.lands.append(land)
