# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from lxml import etree
from pykml.factory import KML_ElementMaker as KML
import os
from pathlib import Path
import time


def addTitle(fileName):
    """
    功能：为任务文件的第一行添加标题栏\n
    输入：任务文件路径\n
    输出：添加标题的任务文件
    """
    with open(fileName, "r+") as f:
        old = f.read()
        f.seek(0)
        title = 'num lon lat alt attr\n'
        f.write(title)
        f.write(old)

    print('Added title')


def readTXT(fileName):

    points = []
    with open(fileName, 'r') as f:
        for line in f.readlines()[1:]:
            line = line.strip().split(',')
            # line[0] is task point's number, multiple 10 for adding point
            # added point's name should plus 1
            point = [float(line[0]),
                     float(line[1]), float(line[2])]
            points.append(point)
            print(point)

    return points


def creatPlacemark(coors_str, defaultView):

    placemark = KML.Placemark(
        KML.name('From GPS'),
        KML.Lookat(
            KML.longitude(defaultView['lon']),
            KML.latitude(defaultView['lat']),
            KML.altitude(defaultView['alt']),
            KML.range(defaultView['range']),
            KML.tilt(defaultView['tilt']),
            KML.heading(defaultView['heading'])
        ),
        KML.LineString(
            KML.coordinates(coors_str)
        )
    )

    return placemark


def writeKML(points, file_path):

    kmlDoc = KML.kml()
    doc = KML.Document()
    coors_str = ''

    for i, point in enumerate(points):
        if i == 0:
            defaultView = {'lon': float(point[1]),
                           'lat': float(point[0]),
                           'alt': 0,
                           'range': 3108.303488980141,
                           'tilt': 29.76964560740583,
                           'heading': 0}

        if i % 3 == 1:  # topic is 10Hz, only record every third point
            coors_str = coors_str + str(point[1]) + ',' + str(point[0]) + ',' + '0' + ' '

    placemark = creatPlacemark(coors_str, defaultView)
    doc.append(placemark)

    kmlDoc.append(doc)

    time_now = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    file_name = time_now + '.kml'
    kml_file_path = os.path.join(file_path, file_name)

    with open(kml_file_path, 'wb') as f:
        f.write(etree.tostring(kmlDoc, pretty_print=True))


def txt2kml(fileName):

    points = readTXT(fileName)
    file_path = os.path.dirname(fileName)
    writeKML(points, file_path)


if __name__ == '__main__':

    home = str(Path.home())
    # your file name
    fileName = os.path.join(home, 'Desktop', 'GPS_0520.txt')

    txt2kml(fileName)
