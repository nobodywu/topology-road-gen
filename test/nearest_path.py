import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyproj
import xml.dom.minidom
import os
import sys


def show_road(junctions, points):
    ax.scatter(points[:, 0], points[:, 1], c='r', marker='.')
    ax.scatter(junctions[:, 0], junctions[:, 1], c='k', marker='o')
    ax.grid(True)
    ax.axis('equal')


def GCS2PCS(lon, lat, coor1="epsg:4326", coor2="epsg:3857"):
    p1 = pyproj.Proj(init=coor1)  # 定义数据地理坐标系 WGS84
    p2 = pyproj.Proj(init=coor2)  # 定义转换投影坐标系
    x, y = pyproj.transform(p1, p2, lon, lat)  # lon 和lat 可以是元组
    return x, y


def on_click(event):
    print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
          ('double' if event.dblclick else 'single', event.button,
           event.x, event.y, event.xdata, event.ydata))

    if event.button == 2:
        global ix, iy
        ix, iy = event.xdata, event.ydata
        global coords
        coords.append((ix, iy))
        if len(coords) == 2:
            fig.canvas.mpl_disconnect(cid)
            plt.close(1)


def parse_xml(filepath):
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
            point[0], point[1] = GCS2PCS(lon, lat)
            points.append(point)

    else:
        print("Empty file, no node.")

    return points


def calc_dis(point, points):
    """
    功能：计算路段多点到已知所有路口点的距离\n
    输入：路段中的所有点，已确定的路口点\n
    输出：到已知所有路口点的距离
    """
    lon_delta = np.subtract(point[0], points[:, 0])
    lat_delta = np.subtract(point[1], points[:, 1])
    dis = np.sqrt(np.multiply(lon_delta, lon_delta) + np.multiply(lat_delta, lat_delta))
    dis = dis[:, np.newaxis]

    return np.hstack([points, dis])


def find_nearest(point, points):
    points_dis = calc_dis(point, points)

    points_dis_min = points_dis.min(axis=0)
    # print(point_stack_dis_min)
    index = np.argwhere(points_dis == points_dis_min[-1])
    row = index[0][0]
    # col = index[0][1]
    # print(row, col)

    return points_dis[row]


def get_doc_paths(dir_name):
    filepath_list = []

    for maindir, subdir, file_list_str in os.walk(dir_name):
        file_list = []
        for each in file_list_str:
            try:
                file_number = int(each[:-4])
                file_list.append(file_number)
            except:
                print('Ignore <%s>' % each)

        for each in sorted(file_list):
            filename = str(each) + '.xml'
            filepath = os.path.join(maindir, filename)
            filepath_list.append(filepath)

    print("Dir <%s> has %d XML files." % (maindir, len(filepath_list)))

    return filepath_list


def build_graph(points, points_segs, graph={}):
    print('*****BUILD GRAPH*****')
    points = np.array(points)
    points_unique = pd.DataFrame(points).drop_duplicates().values

    i = 1

    for each_point in points_unique:
        point_neighbor = {str(int(each_point[2])): []}

        for each_seg in points_segs:
            each_seg = np.array(each_seg)
            find = each_seg[:, 2] == each_point[2]
            if find.any():
                same_id = each_seg[each_seg[:, 2] == each_point[2]][0, 2]
                point_index = np.argwhere(each_seg[:, 2] == same_id)[0, 0]
            else:
                # print("build_graph(): find.any() NO MATCH")
                continue

            if point_index < (each_seg.shape[0] - 1) and point_index > 0:
                # print("build_graph(): MID POINT")
                point_neighbor[str(int(each_point[2]))].append(
                    str(int(each_seg[point_index + 1][2])))
                point_neighbor[str(int(each_point[2]))].append(
                    str(int(each_seg[point_index - 1][2])))
            elif point_index == (each_seg.shape[0] - 1):
                # print("build_graph(): END POINT")
                point_neighbor[str(int(each_point[2]))].append(
                    str(int(each_seg[point_index - 1][2])))
            elif point_index == 0:
                # print("build_graph(): FIRST POINT")
                point_neighbor[str(int(each_point[2]))].append(
                    str(int(each_seg[point_index + 1][2])))
            else:
                print("build_graph(): point_neighbor[str(int(each_point[2]))].append() ERROR")

        graph = {**graph, **point_neighbor}

        if i == 200:
            break

        i = i + 1

    return graph


def find_all_paths(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return [path]
    if start not in graph:
        return []
    paths = []
    for node in graph[start]:
        if node not in path:
            newpaths = find_all_paths(graph, node, end, path)
            for newpath in newpaths:
                paths.append(newpath)
    return paths


def find_path(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return path
    if start not in graph:
        return None
    for node in graph[start]:
        if node not in path:
            newpath = find_path(graph, node, end, path)
            if newpath:
                return newpath
    return None


if __name__ == '__main__':
    # search_astar()
    id_start = 20002
    id_end = 550011
    dir_name = '/home/mengze/Desktop/test'
    doc_junctions = '/home/mengze/Desktop/test_junctions.txt'
    doc_points = '/home/mengze/Desktop/test_points.txt'

    filepaths = get_doc_paths(dir_name)

    points_segs = []
    for each in filepaths:
        points = parse_xml(each)
        points_segs.append(points)

    points_GCS = points = np.loadtxt(doc_points)
    junctions_GCS = junctions = np.loadtxt(doc_junctions)  # only for show

    points[:, 0], points[:, 1] = GCS2PCS(points[:, 0], points[:, 1])
    junctions[:, 0], junctions[:, 1] = GCS2PCS(junctions[:, 0], junctions[:, 1])

    fig = plt.figure(1)
    ax = fig.add_subplot(111)
    ax.set_title('click two points')
    show_road(junctions, points)

    coords = []
    cid = fig.canvas.mpl_connect('button_press_event', on_click)

    plt.show(1)

    if not coords:
        print("ERROR: no points are selected")
        sys.exit()

    print(coords)

    start_point = find_nearest(coords[0], points)
    end_point = find_nearest(coords[1], points)

    print(start_point[2], end_point[2])

    graph = build_graph(points, points_segs)
    print(graph)
    print("GOT graph.")
    paths = find_all_paths(graph, '10002', '100007')
    for each in paths:
        print(each)

    print("All done.")
