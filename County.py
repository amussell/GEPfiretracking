from CountyFireLandHelpers import intersectOrIn
from shapely.geometry import Polygon

class County:
    fires = []
    name = ""

    def __init__(self, xmlOutput):
        fires = []
        name = xmlOutput[1]['name']
        points = xmlOutput[0]
        poly = Polygon(points)

    def findFiresInCounty(self,fire_list):
        for fire in fire_list:
            if intersectOrIn(fire.poly,self.poly):
                self.fires.append(fire)
