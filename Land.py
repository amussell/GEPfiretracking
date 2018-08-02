import pandas as pd
from shapely.geometry import Polygon
from CountyFireLandHelpers import intersectOrIn

class Land:
    managementAgency = ""
    fid = ""
    acres = ""

    def __init__(self, xmlOutput):
        def parseTableForAttribute(table,attributeString):
            for i, row in enumerate(table[0]):
                if row == attributeString:
                    return table[1][i]

        def parseDescription(desc):
            tables = pd.read_html(desc)
            self.managementAgency = parseTableForAttribute(tables[0],"MGMT_AGNCY")
            self.fid = parseTableForAttribute(tables[0],"FID")
            self.acres = parseTableForAttribute(tables[0],"GIS_ACRES_")
        parseDescription(xmlOutput[1]['description'])
        self.points = xmlOutput[0]
        self.poly = Polygon(self.points)