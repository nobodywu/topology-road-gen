# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import seaborn
import matplotlib.pyplot as plt
import pyproj

SAVE_TXT_POINTS = '/home/mengze/Desktop/GPS_fengtai_Aug20_points.txt'
SAVE_TXT_JUNCTIONS = '/home/mengze/Desktop/GPS_fengtai_Aug20_junctions.txt'
SAVE_TASK = '/home/mengze/Desktop/TaskPoints_fengtai_Aug20.txt'
p1 = pyproj.Proj(init="epsg:4326")
p2 = pyproj.Proj(init="epsg:3857")
# [id, type] 0:"start_point" 1:"end_point"; 2:"way_point"; 3:"fork_point";
#            4:"search_in"; 5:"search_out"; 6:"cruise_start"; 7:"cruise_end"
TASK_POINTS = [[30022, 0], [350083, 2], [310006, 4], [310019, 5],
               [290010, 2], [240006, 2], [180013, 2], [60010, 1]]

points_all = np.loadtxt(SAVE_TXT_POINTS)
points_junctions = np.loadtxt(SAVE_TXT_JUNCTIONS)

points_all = np.array(points_all)
TASK_POINTS = np.array(TASK_POINTS)

task = np.empty(shape=(0, 4))
for each in TASK_POINTS:
    find = points_all[points_all[:, 2] == each[0]]
    find = np.append(find[0], each[1])

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
plt.scatter(points_junctions[:, 0], points_junctions[:, 1], c='k', marker='o')
plt.scatter(task[:, 0], task[:, 1], c='b', marker='o')
plt.axis('equal')
plt.show()
