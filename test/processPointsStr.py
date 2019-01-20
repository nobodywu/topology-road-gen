# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from pykml import parser


def parseKML(KML_FILE):
    """
    功能：解析kml文件。提取kml文件中所有placemark中的点。当文件路径不正确时，程序退出。\n
    输入：kml文件的路径\n
    输出：kml文件中的所有点的经纬度
    """
    points_all = []
    try:
        with open(KML_FILE, 'r') as f:
            kml = parser.parse(f).getroot()
    except:
        print('Can not find % s.' % KML_FILE)
        sys.exit()

    linestrings = kml.findall('.//{http://www.opengis.net/kml/2.2}LineString')
    print('File %s has %d LineString.' % (KML_FILE, len(linestrings)))
    if len(linestrings):
        for each in linestrings:
            coords = str(each.coordinates)
            points_seg = coords.strip().split(' ')
            for each in points_seg:
                each = each.split(',')
                points_all.append(each)

    points = kml.findall('.//{http://www.opengis.net/kml/2.2}Point')
    print('File %s has %d Point.' % (KML_FILE, len(points)))
    if len(points):
        for each in points:
            coords = str(each.coordinates)
            each = coords.split(',')
            points_all.append(each)

    return points_all


def getAttr(point, points, POINT_ATTRIBUTE):
    """
    功能：设置点的属性\n
    输入：该点，所有点，预设属性\n
    输出：该点属性
    """
    attribute = POINT_ATTRIBUTE[2]

    return attribute


def main():
    """
    功能：解析google earth的kml文件，提取kml文件中所有placemark中的点，对每个点设置属性。
    保存为txt格式文件。\n
    输入：参考模块说明\n
    输出：txt文件
    """
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
    """
    ********模块功能********\n
    该模块为自动读取google earth的kml文件而设计。提取kml文件中所有placemark中的点，对每个点设置属性。
    最终保存为txt格式文件。\n
    1. 带属性的txt文件可以让无人车直接跟路点行驶；\n
    2. 生成的txt文件可被构建路网的Qt程序CreateXMLWithLatLon使用。\n
    ********变量说明********\n
    KML_FILE: kml文件路径\n
    TXT_FILE: 输出txt文件路径\n
    INTERVAL: 写入txt文件时的点间隔\n
    POINT_ATTRIBUTE: 点属性
    """
    KML_FILE = '/home/mengze/Desktop/yuanshi.kml'
    TXT_FILE = '/home/mengze/Desktop/yuanshi.txt'
    INTERVAL = 2
    POINT_ATTRIBUTE = [0, 1, 2, 3, 4]

    main()
