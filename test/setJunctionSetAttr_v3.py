# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import xml.dom.minidom
import numpy as np
import seaborn
import matplotlib.pyplot as plt
import pyproj
import sys
import copy

"""
********模块功能********\n
该模块简化了Qt程序CreateXMLWithLatLon对路网的构建，并可以根据需要为路网中的点添加不同的属性。
为了检查路网中路口点是否正确设计了检查动画方便检查。
使用vel_limit、和other_attr为路点设置属性步骤：\n
1. 清空上述两个变量中的id\n
2. 运行程序生成\n
3. 使用google earth导入***_points.txt文件，查看需要设置属性点的id\n
4. 在程序中为上述两个变量添加id，重新运行程序\n
"""


class Config:

    def __init__(self, dirs_in, vel_limit, other_attr):
        """
        ********变量说明********\n
        dirs_in: 输入文件夹，文件夹中包含路段xml文件，文件中没有路口点\n
        dir_out: 输出文件夹，生成带有路口点的路段xml文件\n
        dir_points: 保存路网中所有点。保存点的经纬度和id信息，经纬度精度为小数点后8位\n
        dir_junctions: 保存路网中所有路口点。保存点的经纬度和id信息，经纬度精度为小数点后8位\n
        vel_attr: 路点的限速和属性\n
        vel_limit: 限速点id\n
        water: 水属性id\n
        smoke: 烟雾属性id\n
        dyn_ob: 动态障碍物属性id\n
        concave_ob: 凹障碍属性id\n
        other_attr: 包含水、烟雾、动态障碍物和凹障碍属性\n
        p1: 地理坐标系统WGS84，可参考https://blog.csdn.net/NobodyWu/article/details/81158298\n
        p2: 投影坐标系统\n
        dis_delta: 路口点判距\n
        output: 文件输出开关\n
        inspect: 检查开关\n
        pause: 检查中每段路显示暂停时间
        """

        self.dirs_in = dirs_in
        self.dir_out = self.dirs_in[0] + '_out'
        self.dir_points = self.dirs_in[0] + '_points.txt'
        self.dir_junctions = self.dirs_in[0] + '_junctions.txt'
        # [vel] m/s
        # {'id': 10001, 'type': 0}       0:"start_point" 1:"end_point"; 2:"way_point";
        # {'lonlat': [10024], 'type': 3} 3:"search"; 4:"scout_start"; 5:"scout_start"
        self.vel_attr = {'vel': ['3.5', '5'], 'type': [
            '0', '1', '2', '-3', '4', '5', '6', '7', '-1']}
        # [num] set (2*n+1) points around vel limited point
        # [id] which point needs vel limit
        self.vel_limit = vel_limit
        self.other_attr = other_attr

        self.p1 = pyproj.Proj(init="epsg:4326")
        self.p2 = pyproj.Proj(init="epsg:3857")
        self.dis_delta = 20
        self.output = True
        self.inspect = True
        self.pause = 0.5


def findAllPath(dirs_name):
    """
    功能：读取目录下所有路网文件，忽略空文件和文件名称不正确的文件。
    正确的文件名应为N0000.xml，N为正整数。\n
    输入：文件目录\n
    输出：目录下所有路段文件名
    """
    print("******Finding files ******")
    filepath_list = []
    for dir_name in dirs_name:
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


def parseXML(filepath, way_id, p1, p2):
    """
    功能：解析路段XML文件。
    提取标签node中的经纬度和id号，如果没有node标签，打印提示信息；
    提取way标签中的路段id号，如果没有way标签，打印提示信息。
    如果有空文件，自动按顺序排列路段id。\n
    输入：XML文件路径，路段id\n
    输出：路段中的所有点，路段id
    """
    print("******Parsing <%s>******" % filepath)
    way_id += 10000
    points = []
    DOMTree = xml.dom.minidom.parse(filepath)
    collection = DOMTree.documentElement
    if collection.getElementsByTagName('node'):
        nodes = collection.getElementsByTagName('node')

        point_id = 1
        for node in nodes:
            lon = node.getAttribute("lon")
            lat = node.getAttribute("lat")
            point = [float(lon), float(lat), way_id + point_id]
            point[0], point[1] = pyproj.transform(p1, p2, point[0], point[1])
            points.append(point)
            point_id += 1
            if point_id >= 9999:
                print("File includes too many points.")
                sys.exit()

    else:
        print("Empty file, no node.")

    return points, way_id


def setIntersection(points, points_stack, way_id, dis_delta):
    """
    功能：自动判断路段的端点是否为路网中的路口点。\n
    输入：路段中的所有点，已确定的路口点，路段id，路口点判断的距离依据\n
    输出：路段中的所有点，已确定的路口点
    """
    print('******Setting junction point. Way id: %d******' % way_id)

    shape = points_stack.shape
    if points:
        if not shape[0]:
            points_stack = np.vstack([points[0], points[-1]])
            print('First way, set two junction points')
        else:
            points_stack, point = stackPoint(
                points[0], points_stack, dis_delta, index_str='First point')
            points[0] = point
            points_stack, point = stackPoint(
                points[-1], points_stack, dis_delta, index_str='Last point')
            points[-1] = point

    else:
        print('no points.')

    # print(points_stack.shape)
    return points, points_stack


def calcDis(point, points_stack):
    """
    功能：计算路段多点到已知所有路口点的距离\n
    输入：路段中的所有点，已确定的路口点\n
    输出：到已知所有路口点的距离
    """
    lon_delta = np.subtract(point[0], points_stack[:, 0])
    lat_delta = np.subtract(point[1], points_stack[:, 1])
    dis = np.sqrt(np.multiply(lon_delta, lon_delta) + np.multiply(lat_delta, lat_delta))
    dis = dis[:, np.newaxis]

    return np.hstack([points_stack, dis])


def stackPoint(point, points_stack, dis_delta, index_str=''):
    """
    功能：根据路口点距离判距，保存路口点。
    找到路段端点距已知路口点的最小距离的点，如果该距离小于dis_delta，则该点为路口点
    否则为新的路口点。\n
    输入：路段中的所有点，已确定的路口点，路口点判断的距离依据\n
    输出：已确定的路口点，路段端点
    """
    points_stack_dis = calcDis(point, points_stack)
    # print(points_stack_dis)
    point_stack_dis_min = points_stack_dis.min(axis=0)
    # print(point_stack_dis_min)
    index = np.argwhere(points_stack_dis == point_stack_dis_min[-1])
    row = index[0][0]
    col = index[0][1]
    # print(row, col)

    if abs(point_stack_dis_min[-1]) < dis_delta:
        point_lon = points_stack_dis[row, 0]
        point_lat = points_stack_dis[row, 1]
        point_id = points_stack_dis[row, col - 1]
        print('%s already exits in junction points, point id: %d.' % (index_str, point_id))
        point = [point_lon, point_lat, point_id]

    else:
        points_stack = np.vstack([points_stack, point])
        print('%s stacked.' % index_str)

    return points_stack, point


def writeXML(points, way_id, limit_points, other_attr_points, config):
    """
    功能：生成带有路口点的路段XML文件，并为路段上每个点加上需要的属性。\n
    输入：路段中的所有点，路段id，路点属性，限速属性id，限速点，其他属性id，其他属性点\n
    输出：限速点，其他属性点
    """
    print('******Writing XML******')

    doc = xml.dom.minidom.Document()
    doc.appendChild(doc.createComment("Generated by python, Author: Mengze."))
    osmNode = doc.createElement("osm")
    doc.appendChild(osmNode)

    # water_id
    water_id = findAttrID(points, config.other_attr[0])
    # smoke_id
    smoke_id = findAttrID(points, config.other_attr[1])
    # dyn_ob_id
    dyn_ob_id = findAttrID(points, config.other_attr[2])
    # concave_ob_id
    concave_ob_id = findAttrID(points, config.other_attr[3])

    attr_id_all = [water_id, smoke_id, dyn_ob_id, concave_ob_id]

    # vel limit id
    limit_id = findLimitID(points, vel_limit)

    limit_points, other_attr_points = addNode(doc, osmNode, points, config.vel_attr, limit_id,
                                              limit_points, attr_id_all, other_attr_points,
                                              config.p1, config.p2)
    addWay(doc, osmNode, points, way_id,
           config.p1, config.p2)

    file_name = '%s/%d.xml' % (config.dir_out, way_id)
    print(file_name)

    with open(file_name, 'w') as f:
        doc.writexml(f, addindent="    ", newl="\n", encoding="UTF-8")

    print('Done!')

    return limit_points, other_attr_points


def findAttrID(points, EACH_ATTR):
    """
    功能：根据属性id找到对应点。\n
    输入：路段中的所有点，各个属性id\n
    输出：属性id对应路段中的点
    """
    attr_id = np.empty(shape=[0, ])
    lenth = len(points)
    points_arr = np.array(points)
    pos = EACH_ATTR['num'] + 1
    each_attr_points_id = EACH_ATTR['id']

    for each in each_attr_points_id:
        find = points_arr[:, 2] == each
        if find.any():  # 如果匹配到id
            attr_point_id = points_arr[points_arr[:, 2] == each][0, 2]
            attr_point_index = np.argwhere(points_arr == attr_point_id)[0, 0]
            if attr_point_index < pos:
                attr_id = np.concatenate([attr_id, points_arr[:attr_point_index, 2]])
                attr_id = np.concatenate(
                    [attr_id, points_arr[attr_point_index:attr_point_index + pos, 2]])
            elif lenth - attr_point_index - 1 < pos:
                attr_id = np.concatenate([attr_id, points_arr[attr_point_index:, 2]])
                attr_id = np.concatenate(
                    [attr_id, points_arr[attr_point_index - pos + 1:attr_point_index, 2]])
            else:
                attr_id = np.concatenate(
                    [attr_id, points_arr[attr_point_index - pos + 1:attr_point_index + pos, 2]])

    print('Attr point id:{0}'.format(attr_id))
    return attr_id


def findLimitID(points, vel_limit):
    """
    功能：根据速度限制id找到对应点。并且为路口附近的点进行速度限制。\n
    输入：路段中的所有点，速度限制id\n
    输出：速度限制id对应路段中的点
    """
    limit_id = np.empty(shape=[0, ])

    lenth = len(points)
    points_arr = np.array(points)
    pos = vel_limit['num'] + 1
    set_limit_points_id = vel_limit['id']

    if lenth <= vel_limit['num'] * 2 + 1:  # 每段路上点的数量 <= num*2 + 1，取所有点
        limit_id = points_arr[:, 2]
    else:  # >= num*2 + 1，取每段两端的点，查找限制速度的id
        limit_id = points_arr[0:pos, 2]
        limit_id = np.concatenate([limit_id, points_arr[-pos:, 2]])
        for each in set_limit_points_id:
            find = points_arr[:, 2] == each
            if find.any():  # 如果匹配到id
                limit_point_id = points_arr[points_arr[:, 2] == each][0, 2]
                limit_point_index = np.argwhere(points_arr == limit_point_id)[0, 0]
                if limit_point_index < pos:  # 在开头
                    limit_id = np.concatenate([limit_id, points_arr[:limit_point_index, 2]])
                    limit_id = np.concatenate(
                        [limit_id, points_arr[limit_point_index:limit_point_index + pos, 2]])
                elif lenth - limit_point_index - 1 < pos:  # 在结尾
                    limit_id = np.concatenate([limit_id, points_arr[limit_point_index:, 2]])
                    limit_id = np.concatenate(
                        [limit_id, points_arr[limit_point_index - pos + 1:limit_point_index, 2]])
                else:  # 在中间
                    limit_id = np.concatenate(
                        [limit_id, points_arr[limit_point_index - pos + 1:limit_point_index + pos, 2]])

    print('Vel limit point id:{0}'.format(limit_id))

    return limit_id


def addNode(doc, osmNode, points, vel_attr, limit_id, limit_points, attr_id_all, other_attr_points, p1, p2):
    """
    功能：为输出的路段XML文件添加node标签。node标签中包含经纬度、速度属性以及其他属性\n
    输入：xml文件标签对象，node标签父对象，路段中的所有点，路点属性，速度限制id，速度限制点，其他属性id，其他属性点\n
    输出：速度限制点，其他属性点
    """
    count = 0
    for point in points:
        point[0], point[1] = pyproj.transform(p2, p1, point[0], point[1])
        count += 1
        lon = '%.8f' % point[0]
        lat = '%.8f' % point[1]
        point_id = '%d' % point[2]
        pointNode = doc.createElement("node")
        pointNode.setAttribute('id', point_id)
        pointNode.setAttribute('lat', lat)
        pointNode.setAttribute('lon', lon)
        find = limit_id == point[2]
        point[0], point[1] = pyproj.transform(p1, p2, point[0], point[1])

        # vel limit
        if find.any():
            limit_points.append(copy.deepcopy(point))
            pointNode.setAttribute('vel', vel_attr['vel'][0])
        else:
            pointNode.setAttribute('vel', vel_attr['vel'][1])

        # water
        find_water = attr_id_all[0] == point[2]
        if find_water.any():
            other_attr_points[0].append(copy.deepcopy(point))
            pointNode.setAttribute('water', '1')
        else:
            pointNode.setAttribute('water', '1')

        # smoke
        find_smoke = attr_id_all[1] == point[2]
        if find_smoke.any():
            other_attr_points[1].append(copy.deepcopy(point))
            pointNode.setAttribute('smoke', '1')
        else:
            pointNode.setAttribute('smoke', '1')

        # dyn_ob
        find_dyn_ob = attr_id_all[2] == point[2]
        if find_dyn_ob.any():
            other_attr_points[2].append(copy.deepcopy(point))
            pointNode.setAttribute('dyn_ob', '1')
        else:
            pointNode.setAttribute('dyn_ob', '1')

        # concave_ob
        find_concave_ob = attr_id_all[3] == point[2]
        if find_concave_ob.any():
            other_attr_points[3].append(copy.deepcopy(point))
            pointNode.setAttribute('concave_ob', '1')
        else:
            pointNode.setAttribute('concave_ob', '1')

        # vel_attr['type'][3]='-3'
        if (count == 1) | (count == len(points)):
            pointNode.setAttribute('type', vel_attr['type'][-1])
            point_tagNode = doc.createElement("tag")
            point_tagNode.setAttribute('k', "highway")
            point_tagNode.setAttribute('v', "traffic_signals")
            pointNode.appendChild(point_tagNode)
        else:
            pointNode.setAttribute('type', vel_attr['type'][-1])

        osmNode.appendChild(pointNode)

    return limit_points, other_attr_points


def addWay(doc, osmNode, points, way_id, p1, p2):
    """
    功能：为输出的路段XML文件添加way标签。way标签中包含路段以及路段中所有点的id。\n
    输入：xml文件标签对象，node标签父对象，路段中的所有点，路段id\n
    输出：无
    """
    way_id_str = '%d' % way_id
    wayNode = doc.createElement("way")
    wayNode.setAttribute('id', way_id_str)
    osmNode.appendChild(wayNode)

    for point in points:
        point[0], point[1] = pyproj.transform(p2, p1, point[0], point[1])
        point_id = '%d' % point[2]
        ndtNode = doc.createElement("nd")
        ndtNode.setAttribute('ref', point_id)
        wayNode.appendChild(ndtNode)

    way_tagNode = doc.createElement("tag")
    way_tagNode.setAttribute('k', "name:en")
    way_tagNode.setAttribute('v', "double way")

    wayNode.appendChild(way_tagNode)


def showInspect(points_stack, all_seg, points_all, pause):
    """
    功能：检查路口点与周围的路段连接关系是否正确。查找每个路口点相连的路段并用不同颜色显示。\n
    输入：已知的路口点，路网中的所有路段，路网中的所有点\n
    输出：无
    """
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


def showAnimate(points_stack, points_all, pause, range_PCS):
    """
    功能：在判断路段端点是否为已知路口点的时候用动画显示，以便检查。\n
    输入：已知的所有路口点，路网中的所有点，暂停时间，路段范围\n
    输出：无
    """
    set_xylim(range_PCS)
    plt.pause(pause)
    # plt.scatter(points_all[:, 0], points_all[:, 1], c='r', marker='o')
    plt.scatter(points_stack[:, 0], points_stack[:, 1], c='k', marker='o')
    plt.pause(pause)

    plt.clf()
    # plt.axis('equal')
    set_xylim(range_PCS)
    plt.scatter(points_all[:, 0], points_all[:, 1], c='r', marker='.')
    plt.scatter(points_stack[:, 0], points_stack[:, 1], c='k', marker='o')
    plt.pause(pause)


def showAttr(points_stack, points_all, points):
    """
    功能：用蓝色显示带有属性的点。\n
    输入：已知的所有路口点，路网中的所有点，路段中的点\n
    输出：无
    """
    points_arr = np.array(points)
    plt.scatter(points_all[:, 0], points_all[:, 1], c='r', marker='.')
    if points:
        plt.scatter(points_arr[:, 0], points_arr[:, 1], c='b', marker='.')
    plt.scatter(points_stack[:, 0], points_stack[:, 1], c='k', marker='o')
    plt.axis('equal')


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


def checkEnv(dirs_in, dir_out, output):
    """
    功能：检查输入和输出环境。
    如果输入的文件夹不存在，则打印提示并结束程序；
    如果有，删除已存在的输出文件夹，并创建一个空文件夹。\n
    输入：输入目录，输出目录\n
    输出：无
    """
    count = 0
    for dir_in in dirs_in:
        if not os.path.isdir(dir_in):
            print('DIR <%s> not exists.' % dir_in)
        else:
            print('DIR <%s> exists.' % dir_in)
            count += 1
    if count == 0:
        sys.exit()

    if output:
        if not os.path.isdir(dir_out):
            print('Making dir <%s>.' % dir_out)
            os.mkdir(dir_out)
        else:
            print('Dir <%s> exists, removing old and making new empty DIR.' % dir_out)
            cmd = "rm -rf %s" % dir_out
            os.system(cmd)
            os.mkdir(dir_out)


def saveData(points_all, points_stack, p1, p2, dir_points, dir_junctions):
    '''
    功能：保存路网中所有点，保存路网中所有路口点。保存点的经纬度和id信息，经纬度精度为小数点后8位。\n
    输入：路网中所有点，所有路口点\n
    输出：无
    '''
    points_all[:, 0], points_all[:, 1] = pyproj.transform(
        p2, p1, points_all[:, 0], points_all[:, 1])
    points_stack[:, 0], points_stack[:, 1] = pyproj.transform(
        p2, p1, points_stack[:, 0], points_stack[:, 1])
    np.savetxt(dir_points, points_all, fmt='%.8f %.8f %d')
    np.savetxt(dir_junctions, points_stack, fmt='%.8f %.8f %d')


def genRoad(config):
    """
    功能：读取没有路口点的路段XML文件，输出带有路口点的路段XML文件\n
    输入：参考模块说明\n
    输出：生成带有路口点的路段XML文件并保存路网中所有点、所有路口点为txt
    """
    seaborn.set()
    checkEnv(config.dirs_in, config.dir_out, config.output)

    filepath_in = findAllPath(config.dirs_in)

    all_seg = []
    limit_points = []
    water = []
    smoke = []
    dyn_ob = []
    concave_ob = []
    other_attr_points = [water, smoke, dyn_ob, concave_ob]

    points_all = np.empty(shape=[0, 3])
    points_stack = np.empty(shape=[0, 3])
    way_id = 0
    for each in filepath_in:
        points_each_file = []
        points_each_file, way_id = parseXML(each, way_id, config.p1, config.p2)

        points_each_file, points_stack = setIntersection(
            points_each_file, points_stack, way_id, config.dis_delta)

        if len(points_each_file):
            range_PCS = calcRange(points_each_file)

            points_all = np.vstack([points_all, points_each_file])
            all_seg.append(copy.deepcopy(points_each_file))
            if config.output:
                limit_points, other_attr_points = writeXML(
                    points_each_file, way_id, limit_points, other_attr_points, config)

            if config.inspect:
                plt.figure(0)
                mng_figure0 = plt.get_current_fig_manager()
                mng_figure0.resize(1600, 800)
                # plt.axis("equal")
                showAnimate(points_stack, points_all, config.pause, range_PCS)

    plt.clf()
    plt.axis('equal')
    plt.scatter(points_all[:, 0], points_all[:, 1], c='r', marker='.')
    plt.scatter(points_stack[:, 0], points_stack[:, 1], c='k', marker='o')
    plt.pause(2)
    print('Done! Set %d junction points.' % points_stack.shape[0])

    if config.inspect:
        print('Inspecting ...')
        plt.figure(1)
        mng_figure1 = plt.get_current_fig_manager()
        mng_figure1.resize(1600, 800)
        # plt.axis('equal')
        plt.scatter(points_all[:, 0], points_all[:, 1], c='r', marker='.')
        showInspect(points_stack, all_seg, points_all, config.pause)
        plt.clf()
        plt.axis('equal')
        plt.scatter(points_all[:, 0], points_all[:, 1], c='r', marker='.')
        plt.scatter(points_stack[:, 0], points_stack[:, 1], c='k', marker='o')
        plt.pause(2)
        print('Inspect display over.')

        print('Show attribute.')
        # vel limit
        plt.figure(2)
        mng_figure2 = plt.get_current_fig_manager()
        mng_figure2.window.showMaximized()
        showAttr(points_stack, points_all, limit_points)

        plt.figure(3)
        mng_figure3 = plt.get_current_fig_manager()
        mng_figure3.window.showMaximized()
        # water
        plt.subplot(2, 2, 1)
        showAttr(points_stack, points_all, other_attr_points[0])
        # smoke
        plt.subplot(2, 2, 2)
        showAttr(points_stack, points_all, other_attr_points[1])
        # dyn_ob
        plt.subplot(2, 2, 3)
        showAttr(points_stack, points_all, other_attr_points[2])
        # concave_ob
        plt.subplot(2, 2, 4)
        showAttr(points_stack, points_all, other_attr_points[3])

    plt.show()

    if config.output:
        saveData(points_all, points_stack, config.p1, config.p2,
                 config.dir_points, config.dir_junctions)
        print('Data <%s> and <%s> have saved.' % (config.dir_points, config.dir_junctions))


if __name__ == '__main__':

    print(sys.version)
    # dir_in is a list, could have many dirs
    dirs_in = ['/home/mengze/Desktop/test']

    vel_limit = {'num': 2, 'id': []}
    water = {'num': 2, 'id': []}
    smoke = {'num': 2, 'id': []}
    dyn_ob = {'num': 2, 'id': []}
    concave_ob = {'num': 2, 'id': []}
    other_attr = [water, smoke, dyn_ob, concave_ob]

    config = Config(dirs_in, vel_limit, other_attr)
    # config.inspect = False

    genRoad(config)
