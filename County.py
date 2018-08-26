from CountyFireLandHelpers import intersectOrIn
from shapely.geometry import Polygon

class County:

    def __init__(self, xmlOutput):
        self.fires = []
        self.name = xmlOutput[1]['name']
        self.points = xmlOutput[0]
        self.poly = Polygon(self.points)

    def findFiresInCounty(self, fire_list):
        count = 0
        for fire in fire_list:
            if intersectOrIn(fire.poly, self.poly):
                self.fires.append(fire)
