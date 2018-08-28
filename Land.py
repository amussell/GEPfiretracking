import pandas as pd
from shapely.geometry import Polygon
from CountyFireLandHelpers import intersectOrIn


class Land:

    def __init__(self, xmlOutput):
        #
        # Parses an html table for the value of a specified attribute where
        # the attribute is specified in the 0th column and the attributes
        # value is specifed in the same row in the next (1st) column
        #
        def parseTableForAttribute(table, attributeString):
            for i, row in enumerate(table[0]):
                if row == attributeString:
                    return table[1][i]

        #
        # Parses the description tag of a kml document for the given land.
        # The description tag contains an html table with the info about the land
        #
        def parseDescription(desc):
            tables = pd.read_html(desc)
            self.managementAgency = parseTableForAttribute(tables[0], "MGMT_AGNCY")
            self.fid = parseTableForAttribute(tables[0], "FID")
            self.acres = parseTableForAttribute(tables[0], "GIS_ACRES_")
        parseDescription(xmlOutput[1]['description'])
        self.points = xmlOutput[0]
        self.poly = Polygon(self.points)