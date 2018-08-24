# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import seaborn
import matplotlib.pyplot as plt
import pyproj
import sys

SAVE_TXT_POINTS = '/home/mengze/Desktop/GPS_fengtai_Aug24_points.txt'
SAVE_TXT_JUNCTIONS = '/home/mengze/Desktop/GPS_fengtai_Aug24_junctions.txt'
SAVE_TASK = '/home/mengze/Desktop/TaskPoints_fengtai_Aug24.txt'
p1 = pyproj.Proj(init="epsg:4326")
p2 = pyproj.Proj(init="epsg:3857")
# [id, type] 0:"start_point" 1:"end_point"; 2:"way_point";
#            3:"search"; 4:"scout_start"; 5:"scout_start"
TASK_POINTS = [{'id': 10007, 'type': 0}, {'id': 30018, 'type': 2},
               {'lonlat': [116.185254, 39.824484], 'type': 3}, {'id': 160011, 'type': 2},
               {'id': 300015, 'type': 2}, {'id': 340030, 'type': 2},
               {'id': 280062, 'type': 4}, {'id': 280016, 'type': 5},
               {'id': 60004, 'type': 1}]


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

points_all[:, 0], points_all[:, 1] = pyproj.transform(p1, p2, points_all[:, 0], points_all[:, 1])
points_junctions[:, 0], points_junctions[:, 1] = pyproj.transform(
    p1, p2, points_junctions[:, 0], points_junctions[:, 1])
task[:, 0], task[:, 1] = pyproj.transform(p1, p2, task[:, 0], task[:, 1])

seaborn.set()
plt.scatter(points_all[:, 0], points_all[:, 1], c='r', marker='o')
i = 1
for task_point in task:
    number = '%d(type: %d)' % (i, task_point[3])
    plt.plot(task_point[0], task_point[1], 'bo')
    plt.text(task_point[0], task_point[1], number)
    i += 1

plt.axis('equal')
plt.show()
