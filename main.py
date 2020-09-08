import requests
import re
import json
import shapefile
from shapely.geometry import Polygon, Point, MultiPolygon
from shapely.geometry import shape, asShape
import urllib.parse


def lambda_handler(event, context):
    
    body = event['body']
    
    msg = urllib.parse.unquote(body)
    print(msg)
    
    url = re.findall("(https.+?)&",msg)
    print(url)
    if url:
        pt = createPoint(url[0])
        if pt: 
            land = getTerritory(pt)
        else:
            land = "Sorry, I couldn't find any coordinates in that link. Try selecting a different point? Or zooming in a bit further?"
    else:
        land = "Sorry, I couldn't find a Google Maps URL in that message. Make sure it doesn't have any additional text after the link."

    return {
        "statusCode": 200,
        "headers": {"content-type": "text/plain"},
        "body": land
    }

def createPoint(url):
    res = requests.get(url)
    print(res.url)
    #print(res.history[0].url)
    #print(res.history[1].url)
    #print(res.history[2].url)
    x = re.findall('(-?\d+\.\d+),(\d+\.\d+)',res.url)
    if not x:
        print("Can't find in lat,lng in URL")
        x = re.findall('(-?\d+.\d+)%2C(-?\d+.\d+)',res.text)
    if not x: 
        return False
    print(x)
    lng = float(x[0][1])
    lat = float(x[0][0])
    #Point(Lng,Lat)
    #Point(145.231132,-37.231431)
    return(Point(lng,lat))


def checkInBBox(BBox,point):
    x1 = BBox[0]
    y1 = BBox[1]
    x2 = BBox[2]
    y2 = BBox[3]
    x = point.x
    y = point.y 
    return ((x - x1) * (x2 - x) >= 0) and ((y - y1) * (y2 - y))
    
    
def getTerritory(pt):
    shp = shapefile.Reader('shape/rap')
    evry = shp.shapeRecords()

    name = False
    for rec in evry:
        #print(rec.record.SHORT_NAME)
        if checkInBBox(rec.shape.bbox,pt):
            s = asShape(rec.shape) 
            if s.contains(pt):
                name = rec.record.SHORT_NAME 
                break
            #print("The point is in", name)
    if name:
        return("That location is in the unceded territory of the " + name + " people")
    else:
        return("That location doesn't have a formally recognized traditional owner")
