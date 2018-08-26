import csv
import matplotlib.pyplot as plt
import numpy as np

def intersectOrIn(poly1,poly2):
    return poly1.overlaps(poly2) or poly1.contains(poly2) or poly2.contains(poly1)

def outputDataToCSV(counties,fires,lands):
    with open('data.csv', 'w', newline='') as f:
        w = csv.writer(f)
        count = 0;
        for county in counties:
            for fire in county.fires:
                landsString = "["
                for land in fire.lands:
                    landsString += land.managementAgency + " " + land.fid + " acres: " + land.acres + ", "
                landsString += "]"
                w.writerow([county.name,fire.name,fire.year,fire.acres,landsString])
                count += 1
                print(str(count) + " " + county.name + " " + fire.name + " " + fire.acres + " " + landsString)

def plotPoly(polyPoints):
    array = np.array(polyPoints)
    plt.plot(array[:, 0],array[:, 1], color="blue")

def plotPolyRed(polyPoints):
    array = np.array(polyPoints)
    plt.plot(array[:, 0],array[:, 1],'r')

def plotFireAndLands(fire):
    plotPolyRed(fire.points)
    for land in fire.lands:
        plotPoly(land.points)