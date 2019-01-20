# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pyproj
import xml.dom.minidom
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx


def getDocPaths(dir_name):
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


def onclick(event):
    global ix, iy
    ix, iy = event.xdata, event.ydata
    print('x = %d, y = %d' % (ix, iy))

    global coords
    coords.append((ix, iy))

    if len(coords) == 2:
        fig.canvas.mpl_disconnect(cid)
        plt.close()

    return coords


def calcDis(point, points):

    lon_delta = np.subtract(point[0], points[:, 0])
    lat_delta = np.subtract(point[1], points[:, 1])
    dis = np.sqrt(np.multiply(lon_delta, lon_delta) + np.multiply(lat_delta, lat_delta))
    dis = dis[:, np.newaxis]

    return np.hstack([points, dis])


def findNearestPoint(point, points):
    points_dis = calcDis(point, points)
    point_dis_min = points_dis.min(axis=0)
    index = np.argwhere(points_dis == point_dis_min[-1])
    row = index[0][0]
    col = index[0][1]

    point_lon = points_dis[row, 0]
    point_lat = points_dis[row, 1]
    point_id = points_dis[row, col - 1]
    point = [point_lon, point_lat, int(point_id)]

    return point


def findRoadLink(end_point_id, points_all_segs):
    link_id = []
    for each_seg in points_all_segs:
        if each_seg[0][-1] == end_point_id:
            link_id.append(str(each_seg[1][-1]))
        if each_seg[-1][-1] == end_point_id:
            link_id.append(str(each_seg[-2][-1]))

    return link_id


def genDict(points_all_segs):
    roadDict = {}

    for each_seg in points_all_segs:
        i = 1
        for each_point in each_seg:
            if i == 1 or i == len(each_seg):
                roadDict[str(each_point[-1])] = []
                link_points_id = findRoadLink(each_seg[i - 1][-1], points_all_segs)
                roadDict[str(each_point[-1])].extend(link_points_id)
            else:
                roadDict[str(each_point[-1])] = [str(each_seg[i - 2][-1]), str(each_seg[i][-1])]

            i = i + 1

    return roadDict


if __name__ == '__main__':
    dir_name = '/home/mengze/Desktop/test'
    path_list = getDocPaths(dir_name)
    print(path_list)
    points_all_segs = []

    for path in path_list:
        points = parseXML(path)  # converted to PCS coord
        points_all_segs.append(points)

    ws_dirs = ['/home/mengze/Desktop']
    file_points = os.path.join(ws_dirs[0], 'test_points.txt')
    file_junctions = os.path.join(ws_dirs[0], 'test_junctions.txt')

    p1 = pyproj.Proj(init="epsg:4326")
    p2 = pyproj.Proj(init="epsg:3857")

    points_all = np.loadtxt(file_points)
    points_stack = np.loadtxt(file_junctions)
    points_all[:, 0], points_all[:, 1] = pyproj.transform(
        p1, p2, points_all[:, 0], points_all[:, 1])
    points_stack[:, 0], points_stack[:, 1] = pyproj.transform(
        p1, p2, points_stack[:, 0], points_stack[:, 1])

    coords = []
    fig = plt.figure(1)
    ax = fig.add_subplot(111)
    ax.axis('equal')
    ax.scatter(points_all[:, 0], points_all[:, 1], c='r', marker='.')
    ax.scatter(points_stack[:, 0], points_stack[:, 1], c='k', marker='o')

    cid = fig.canvas.mpl_connect('button_press_event', onclick)

    plt.show()

    point1 = findNearestPoint(coords[0], points_all)
    print(point1)
    point2 = findNearestPoint(coords[1], points_all)
    print(point2)

    roadDict = genDict(points_all_segs)

    # paths = findAllPaths(roadDict, str(point1[-1]), str(point2[-1]))
    #
    # for each in paths:
    #     print(each)
    #
    # print('done:', len(paths))

    g = nx.DiGraph()
    g.add_nodes_from(roadDict.keys())
    for k, v in roadDict.items():
        g.add_edges_from(([(k, t) for t in v]))

    # for path in nx.all_simple_paths(g, source=str(point1[-1]), target=str(point2[-1]), cutoff=None):
    #     print(path)

    shortestPath = nx.shortest_path(g, source=str(point1[-1]), target=str(point2[-1]))

    print(shortestPath)

    path_array = np.empty(shape=(0, 3))
    for each in shortestPath:
        index = np.argwhere(points_all == int(each))
        # print(points_all[index[0][0]].shape)
        path_array = np.vstack((path_array, points_all[index[0][0]]))

    print(path_array)

    fig = plt.figure(2)
    ax = fig.add_subplot(111)
    ax.axis('equal')
    ax.scatter(points_all[:, 0], points_all[:, 1], c='r', marker='.')
    ax.scatter(points_stack[:, 0], points_stack[:, 1], c='k', marker='o')
    plt.plot(path_array[:, 0], path_array[:, 1], "b-", linewidth=4)
    plt.show()
