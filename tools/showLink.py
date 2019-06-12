# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import xml.dom.minidom
import numpy as np
import seaborn
import matplotlib.pyplot as plt
import pyproj
import sys


def getDocPaths(dir_name):
    # xml file

    filepathList = []

    for maindir, subdir, fileListStr in os.walk(dir_name):
        fileList = []
        for each in fileListStr:
            try:
                file_number = int(each[:-4])
                fileList.append(file_number)
            except:
                print('Ignore <%s>' % each)

        for each in sorted(fileList):
            filename = str(each) + '.xml'
            filepath = os.path.join(maindir, filename)
            filepathList.append(filepath)

    print("Dir <%s> has %d files." % (maindir, len(filepathList)))

    return filepathList


def parseXML(filepath):
    # 读取具有连接关系路段中的点并进行坐标转换，转换到投影坐标系中
    p1 = pyproj.Proj(init="epsg:4326")
    p2 = pyproj.Proj(init="epsg:3857")

    points = []
    DOMTree = xml.dom.minidom.parse(filepath)
    collection = DOMTree.documentElement
    if collection.getElementsByTagName('node'):
        nodes = collection.getElementsByTagName('node')

        for node in nodes:
            lon = node.getAttribute("lon")
            lat = node.getAttribute("lat")
            point_id = node.getAttribute("id")
            point = [float(lon), float(lat), int(point_id)]
            point[0], point[1] = pyproj.transform(p1, p2, point[0], point[1])
            points.append(point)

    else:
        print("Empty file, no node.")

    return points


def showInspect(points_stack, all_seg, points_all, pause):
    for junction_point in points_stack:
        relevant_seg = np.empty(shape=[0, 3])

        for seg in all_seg:
            seg = np.array(seg)
            first = junction_point[2] == seg[0][2]
            last = junction_point[2] == seg[-1][2]

            if first | last:
                relevant_seg = np.vstack([relevant_seg, seg])

        range_PCS = calcRange(relevant_seg)

        set_xylim(range_PCS)
        plt.pause(pause)
        plt.scatter(relevant_seg[:, 0], relevant_seg[:, 1], c='g', marker='.')
        plt.scatter(points_stack[:, 0], points_stack[:, 1], c='k', marker='o')
        plt.scatter(junction_point[0], junction_point[1], c='b', marker='o')
        plt.pause(pause * 2)
        plt.clf()
        # plt.axis('equal')
        set_xylim(range_PCS)
        plt.scatter(points_all[:, 0], points_all[:, 1], c='r', marker='.')
        plt.scatter(points_stack[:, 0], points_stack[:, 1], c='k', marker='o')
        plt.pause(pause * 2)


def set_xylim(range_PCS):
    """
    功能：根据路点范围计算坐标轴范围。\n
    输入：路段中点的范围\n
    输出：无
    """
    range_xscale = range_PCS[1] - range_PCS[0]
    range_xmid = (range_PCS[1] + range_PCS[0]) / 2
    range_yscale = (range_PCS[3] - range_PCS[2])
    range_ymid = (range_PCS[3] + range_PCS[2]) / 2

    if range_xscale >= range_yscale:
        plt.xlim((range_xmid - range_xscale * 2, range_xmid + range_xscale * 2))
        plt.ylim((range_ymid - range_xscale, range_ymid + range_xscale))
    else:

        plt.ylim((range_ymid - range_yscale, range_ymid + range_yscale))
        plt.xlim((range_xmid - range_yscale * 2, range_xmid + range_yscale * 2))


def calcRange(points):
    """
    功能：计算路段中点的范围\n
    输入：路段中的点\n
    输出：路段中点的范围
    """
    points_arr = np.array(points)
    lon_max = points_arr[:, 0].max()
    lon_min = points_arr[:, 0].min()
    lat_max = points_arr[:, 1].max()
    lat_min = points_arr[:, 1].min()
    range_PCS = [lon_min, lon_max, lat_min, lat_max]

    return range_PCS


def inspect(input_dir):

    p1 = pyproj.Proj(init="epsg:4326")
    p2 = pyproj.Proj(init="epsg:3857")

    seaborn.set()
    filepath_in = getDocPaths(ws_dirs[1])  # dir_out

    file_points = os.path.join(ws_dirs[0], 'points.txt')
    file_junctions = os.path.join(ws_dirs[0], 'junctions.txt')

    points_all = np.loadtxt(file_points)
    points_stack = np.loadtxt(file_junctions)
    points_all[:, 0], points_all[:, 1] = pyproj.transform(
        p1, p2, points_all[:, 0], points_all[:, 1])
    points_stack[:, 0], points_stack[:, 1] = pyproj.transform(
        p1, p2, points_stack[:, 0], points_stack[:, 1])

    all_seg = []
    for each in filepath_in:
        points_each_file = []
        points_each_file = parseXML(each)
        all_seg.append(points_each_file)

    print('Inspecting ...')
    plt.figure(1)
    mng_figure1 = plt.get_current_fig_manager()
    mng_figure1.resize(1600, 800)
    plt.axis('equal')
    plt.scatter(points_all[:, 0], points_all[:, 1], c='r', marker='.')
    plt.scatter(points_stack[:, 0], points_stack[:, 1], c='k', marker='o')
    showInspect(points_stack, all_seg, points_all, 0.5)
    plt.clf()
    plt.axis('equal')
    plt.scatter(points_all[:, 0], points_all[:, 1], c='r', marker='.')
    plt.scatter(points_stack[:, 0], points_stack[:, 1], c='k', marker='o')
    print('Inspect display over.')

    plt.show()


if __name__ == '__main__':
    print(sys.version)
    home = os.path.expanduser('~')

    desktop_ws = os.path.join(home, 'Desktop', 'changsha_May22')

    input_seg = os.path.join(desktop_ws, 'seg')

    ws_dirs = [desktop_ws, input_seg]
    inspect(ws_dirs)
