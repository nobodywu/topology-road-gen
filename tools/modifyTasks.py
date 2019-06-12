# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from lxml import etree
# from pykml.parser import Schema
from pykml.factory import KML_ElementMaker as KML
from pykml import parser
from tkinter import filedialog as td
import tkinter as tk
# from pykml.factory import GX_ElementMaker as GX
import os
import sys


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
    """
    功能：读取任务文件中各任务点的序号、经纬海拔高度和属性\n
    输入：任务文件路径\n
    输出：任务点列表
    """
    points = []
    with open(fileName, 'r') as f:
        for line in f.readlines():
            line = line.strip().split(' ')
            # line[0] is task point's number, multiple 10 for adding point
            # added point's name should plus 1
            point = [int(line[0]) * 10, float(line[1]),
                     float(line[2]), float(line[3]), int(line[4])]
            points.append(point)
            print(point)

    return points


def creatPlacemark(point, colorTag):
    """
    功能：生成placemar标签\n
    输入：点，点颜色标签\n
    输出：kml文件的placemark对象
    """
    defaultView = {'lon': 116.1120793889676,
                   'lat': 40.15788423720766,
                   'alt': 0,
                   'range': 3108.303488980141,
                   'tilt': 29.76964560740583,
                   'heading': 0}
    colorTag = '#' + colorTag
    name = str(point[0])
    coor = '%.8f,%.8f,%.8f' % (point[1], point[2], point[3])
    placemark = KML.Placemark(
        KML.name(name),
        KML.Lookat(
            KML.longitude(defaultView['lon']),
            KML.latitude(defaultView['lat']),
            KML.altitude(defaultView['alt']),
            KML.range(defaultView['range']),
            KML.tilt(defaultView['tilt']),
            KML.heading(defaultView['heading'])
        ),
        KML.styleUrl(colorTag),
        KML.Point(
            KML.coordinates(coor)
        )
    )

    return placemark


def creatStyle(attr, urlDic):
    """
    功能：生成style标签\n
    输入：任务文件中任务点属性，点颜色url链接\n
    输出：kml文件style对象，点颜色标签
    """
    if attr == 0:
        colorTag = 'ylw'
        url = urlDic[colorTag]
    elif attr == 1:
        colorTag = 'blue'
        url = urlDic[colorTag]
    elif attr == 2:
        colorTag = '2'
        url = urlDic[colorTag]
    elif attr == 3:
        colorTag = '3'
        url = urlDic[colorTag]
    elif attr == 4:
        colorTag = '4'
        url = urlDic[colorTag]
    elif attr == 5:
        colorTag = '5'
        url = urlDic[colorTag]
    else:
        colorTag = 'else'
        url = urlDic[colorTag]

    style = KML.Style(
        KML.IconStyle(
            KML.scale(1.2),
            KML.Icon(
                KML.href(url),
            ),
        ),
        id=colorTag
    )

    return style, colorTag


def writeKML(points, urlDic, path):
    """
    功能：生成kml文件。该kml文件由任务文件转化得来。程序自动打开google earth并加载此kml文件，用于检查任务点\n
    输入：任务点列表，点颜色url链接，任务文件所在路径\n
    输出：无。函数生成KYXZ.kml和KYXZ.txt两个文件
    """
    kmlDoc = KML.kml()
    doc = KML.Document()

    for point in points:
        style, colorTag = creatStyle(point[-1], urlDic)
        placemark = creatPlacemark(point, colorTag)
        doc.append(style)
        doc.append(placemark)

    kmlDoc.append(doc)

    print(etree.tostring(kmlDoc, pretty_print=True))

    kmlFileName = path + '/KYXZ.kml'
    kmlFileName_old = path + '/1.kml'
    txtFileName = path + '/KYXZ.txt'  # for inspect

    with open(kmlFileName, 'wb') as f:
        f.write(etree.tostring(kmlDoc, pretty_print=True))

    with open(txtFileName, 'wb') as f:
        f.write(etree.tostring(kmlDoc, pretty_print=True))  # for inspect

    command = 'rm ' + kmlFileName_old
    os.system(command)

    os.system('kill $(ps -A | grep earth | awk \'{print $1}\')')
    command = 'google-earth-pro ' + kmlFileName
    os.system(command)


def txt2kml(fileName, urlDic):
    """
    功能：txt格式任务文件转换用于检查的kml文件主函数。\n
    输入：任务文件路径，点颜色url链接\n
    输出：各个包含点name styleUrl coor的属性字典
    """
    points = readTXT(fileName)
    path = os.path.dirname(fileName)
    writeKML(points, urlDic, path)


def parseXML(fileName):
    """
    功能：解析kml文件。提取kml文件中所有placemark中的点。当文件路径不正确时，程序退出。\n
    输入：kml文件的路径\n
    输出：kml文件中的所有点的经纬度
    """
    path = os.path.dirname(fileName)
    kmlFileName = path + '/1.kml'

    placemarksDic = []  # each element is a dictionaty

    with open(kmlFileName, 'r') as f:
        kml = parser.parse(f).getroot()
        placemarks = kml.findall('.//{http://www.opengis.net/kml/2.2}Placemark')
        print('File <%s> has %d placemarks.' % (kmlFileName, len(placemarks)))
        for each in placemarks:
            placemark = {'name': each.name,
                         'styleUrl': each.styleUrl,
                         'coor': each.Point.coordinates}

            placemarksDic.append(placemark)

    return placemarksDic


def kml2txt(fileName):
    """
    功能：将在google earth上编辑玩任务点，并生成的kml文件转换为txt格式的任务文件。
    任务点顺序为kml点name标签的顺序，并进行无间隔重新编号\n
    输入：任务文件路径\n
    输出：无。函数生成一个新的任务文件，将覆盖原文件
    """
    placemarksDic = parseXML(fileName)

    placemarksDic = sorted(placemarksDic, key=lambda i: i['name'])
    for each in placemarksDic:
        print(each)

    count = 1
    points = []
    for each in placemarksDic:
        point = getPointWithType(each, count)
        count += 1
        points.append(point)
        print(point)

    with open(fileName, 'w') as f:
        for each in points:
            line = '%d %.8f %.8f %.8f %d\n' % (int(each[0]), float(each[1]),
                                               float(each[2]), float(each[3]), int(each[4]))
            f.write(line)


def getPointWithType(placemark, count):
    """
    功能：将kml文件中点的颜色标记转换为任务点的属性\n
    输入：每个点包含name styleUrl coor的属性字典\n
    输出：包含该点序号，经纬海拔高度，属性的列表
    """
    point = []
    point.append(count)
    pointStr = str(placemark['coor'])
    point.append(float(pointStr.split(',')[0]))
    point.append(float(pointStr.split(',')[1]))
    point.append(float(pointStr.split(',')[2]))

    key = str(placemark['styleUrl'])[1]

    if 'y' == key:
        point.append(0)
    elif 'b' == key:
        point.append(1)
    elif '2' == key:
        point.append(2)
    elif '3' == key:
        point.append(3)
    elif '4' == key:
        point.append(4)
    elif '5' == key:
        point.append(5)
    else:
        print(key)
        print('please checkout.')

    return point


def modifyTask():
    home = os.path.expanduser('~')
    desktop = os.path.join(home, 'Desktop')
    fileName = td.askopenfilename(filetypes=[("Task File", ".txt")], initialdir=desktop)

    if fileName:
        # key == type, ylw == start, blue == end
        urlDic = {'ylw': 'http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png',
                  'blue': 'http://maps.google.com/mapfiles/kml/pushpin/blue-pushpin.png',
                  '2': 'http://maps.google.com/mapfiles/kml/paddle/2.png',
                  '3': 'http://maps.google.com/mapfiles/kml/paddle/3.png',
                  '4': 'http://maps.google.com/mapfiles/kml/paddle/4.png',
                  '5': 'http://maps.google.com/mapfiles/kml/paddle/5.png',
                  'else': 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'}

        txt2kml(fileName, urlDic)
        try:
            kml2txt(fileName)
        except:
            print('please save modified points as <1.kml>')


if __name__ == '__main__':
    """
    ********模块功能********\n
    该模块为快速修改任务点而设计。程序运行是会读取txt格式任务文件中的内容并生成kml文件，自动打开google earth并加载kml文件。
    名称为任务点序号×10，任务点属性用带颜色的图片标示。对任务点进行移动、添加、修改操作之后在任务文件所在目录另存为1.kml文件。
    google earth正确退出之后将生成新的任务文件。\n
    ********变量说明********\n
    home: 获取home目录\n
    fileName: 任务文件路径\n
    urlDic: 点颜色图片url
    """
    print(sys.version)
    print('Choose a task file.')

    root = tk.Tk()
    root.title('修改任务文件')
    button = tk.Button(root, text="选择任务文件", command=modifyTask)
    button.grid()

    root.mainloop()
