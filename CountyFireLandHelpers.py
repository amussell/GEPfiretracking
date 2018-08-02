import csv

def intersectOrIn(poly1,poly2):
    return poly1.overlaps(poly2) or poly1.contains(poly2) or poly1.contains(poly2)

def outputDataToCSV(counties,fires,lands):
    with open('data.csv', 'w', newline='') as f:
        w = csv.writer(f)
        for county in counties:
            w.writerow([county[1]['name']])
            for fire in county.fires:
                landsString = "["
                for land in fire.lands:
                    landsString += land.managementAgency + " " + land.fid + " acres: " + land.acres + ", "
                landsString += "]"
                w.writerow([county.name,fire.name,fire.year,fire.acres,landsString])