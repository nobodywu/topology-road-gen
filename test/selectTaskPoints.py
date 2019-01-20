# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import seaborn
import matplotlib.pyplot as plt
import pyproj
import sys


def main():
    """
    ********模块功能********\n
    该模块为生成任务文件而设计，设置id/属性 or 经纬度/属性，即可生成任务文件。\n
    ********变量说明********\n
    SAVE_TXT_POINTS: 保存路网中所有点。保存点的经纬度和id信息，经纬度精度为小数点后8位\n
    SAVE_TXT_JUNCTIONS: 保存路网中所有路口点。保存点的经纬度和id信息，经纬度精度为小数点后8位\n
    SAVE_TASK: 生成的txt路网文件\n
    p1: 地理坐标系统WGS84，可参考https://blog.csdn.net/NobodyWu/article/details/81158298\n
    p2: 投影坐标系统\n
    TASK_POINTS: 需要设置的任务点，格式为id/属性 or 经纬度/属性
    """
    SAVE_TXT_POINTS = '/home/mengze/Desktop/test_Aug18/GPS_test_Aug18_points.txt'
    SAVE_TXT_JUNCTIONS = '/home/mengze/Desktop/test_Aug18/GPS_test_Aug18_junctions.txt'
    SAVE_TASK = '/home/mengze/Desktop/tk_ft_Nov02.txt'
    p1 = pyproj.Proj(init="epsg:4326")
    p2 = pyproj.Proj(init="epsg:3857")
    # {'id': 10001, 'type': 0}       0:"start_point" 1:"end_point"; 2:"way_point";
    # {'lonlat': [lon, lat], 'type': 3} 3:"search"; 4:"scout_start"; 5:"scout_start"
    TASK_POINTS = [{'id': 560143, 'type': 0}, {'id': 560048, 'type': 2},
                   {'lonlat': [114.388617, 37.838506], 'type': 2}, {'id': 560039, 'type': 2},
                   {'id': 560011, 'type': 2}, {'id': 560002, 'type': 2},
                   {'id': 540030, 'type': 2}, {'id': 460003, 'type': 2},
                   {'id': 220004, 'type': 2}, {'id': 150031, 'type': 2},
                   {'id': 150003, 'type': 2}]

    points_all = np.loadtxt(SAVE_TXT_POINTS)
    points_junctions = np.loadtxt(SAVE_TXT_JUNCTIONS)

    points_all = np.array(points_all)
    TASK_POINTS = np.array(TASK_POINTS)

    task = np.empty(shape=(0, 4))
    for each in TASK_POINTS:
        if 'id' in each.keys():
            try:
                find = points_all[points_all[:, 2] == each['id']]
                find = np.append(find[0], each['type'])
                task = np.vstack((task, find))
            except:
                print('ID:%d can\'t find.' % each['id'])
                sys.exit()
        elif 'lonlat' in each.keys():
            find = [each['lonlat'][0], each['lonlat'][1], 00000, each['type']]
            task = np.vstack((task, find))

    print(task)

    count = 1
    with open(SAVE_TASK, 'w') as f:
        for each in task:
            line = '%d %.8f %.8f %.8f %d\n' % (count, each[0], each[1], 0.0, each[3])
            f.write(line)
            count += 1

    points_all[:, 0], points_all[:, 1] = pyproj.transform(
        p1, p2, points_all[:, 0], points_all[:, 1])
    points_junctions[:, 0], points_junctions[:, 1] = pyproj.transform(
        p1, p2, points_junctions[:, 0], points_junctions[:, 1])
    task[:, 0], task[:, 1] = pyproj.transform(p1, p2, task[:, 0], task[:, 1])

    seaborn.set()
    plt.scatter(points_all[:, 0], points_all[:, 1], c='r', marker='o')
    plt.scatter(points_junctions[:, 0], points_junctions[:, 1], c='k', marker='o')

    i = 1
    for task_point in task:
        number = '%d(type: %d)' % (i, task_point[3])
        plt.plot(task_point[0], task_point[1], 'bo')
        plt.text(task_point[0], task_point[1], number)
        i += 1

    plt.axis('equal')
    plt.show()


if __name__ == "__main__":
    main()
