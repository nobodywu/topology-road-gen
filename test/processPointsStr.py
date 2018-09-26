# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from pykml import parser


def parseKML(KML_FILE):
    points_all = []
    try:
        with open(KML_FILE, 'r') as f:
            kml = parser.parse(f).getroot()
            placemarks = kml.findall('.//{http://www.opengis.net/kml/2.2}Placemark')
            print('File %s has %d placemarks.' % (KML_FILE, len(placemarks)))
            for each in placemarks:
                coords = str(each.LineString.coordinates)
                points_seg = coords.strip().split(' ')
                for each in points_seg:
                    each = each.split(',')
                    points_all.append(each)
    except:
        print('Can not find % s.' % KML_FILE)
        sys.exit()
    return points_all


def getAttr(point, points, POINT_ATTRIBUTE):
    attribute = POINT_ATTRIBUTE[2]

    return attribute


def main():

    points_all = parseKML(KML_FILE)
    print("From <%s> get %d point." % (KML_FILE, len(points_all)))

    if os.path.exists(TXT_FILE):
        os.remove(TXT_FILE)
        print('File %s is already existed, removed, will generate new.' % TXT_FILE)

    count = 0
    number_line = 0
    with open(TXT_FILE, 'a') as f:
        for point in points_all:
            count += 1
            lon = float(point[0])
            lat = float(point[1])
            alt = float(point[2])
            attr = getAttr(point, points_all, POINT_ATTRIBUTE)
            if count % INTERVAL == 0:
                number_line += 1
                each_line = "%d %.14f %.14f %.14f %d\n" % (number_line, lon, lat, alt, attr)
                f.write(each_line)

    print("Interval is %d, write %d points to <%s>." % (INTERVAL, number_line, TXT_FILE))


if __name__ == '__main__':
    KML_FILE = '/home/mengze/Desktop/warehouse_Aug25.kml'
    TXT_FILE = '/home/mengze/Desktop/warehouse_Aug25.txt'
    OUTPUT = True
    INTERVAL = 2
    POINT_ATTRIBUTE = [0, 1, 2, 3, 4]
    TASK_POINTS = []

    main()
