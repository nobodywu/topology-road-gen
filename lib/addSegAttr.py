# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import xml.dom.minidom
import shutil


def findFile(input_dir, value):
    print("******Finding files ******")
    filepath_list = []

    for maindir, subdir, file_list_str in os.walk(input_dir):
        file_list = []

        for each in file_list_str:
            file_number = int(each[:-4])

            if file_number in value:
                file_list.append(file_number)

        for each in sorted(file_list):
            filename = str(each) + '.xml'
            filepath = os.path.join(maindir, filename)
            filepath_list.append(filepath)

    print("Dir <%s> find %d mached XML files." % (maindir, len(filepath_list)))
    # print(filepath_list)

    return filepath_list


def delblankline(infile, outfile):
    infopen = open(infile, 'r', encoding="utf-8")
    outfopen = open(outfile, 'w', encoding="utf-8")

    lines = infopen.readlines()
    for line in lines:
        if line.split():
            outfopen.writelines(line)
        else:
            outfopen.writelines("")

    infopen.close()
    outfopen.close()


def writeSegAttr(outputDir, outputDirTemp, key, filePaths, attrName):

    for each in filePaths:
        file_name = os.path.basename(each)
        file_path = os.path.join(outputDir, file_name)
        file_path_temp = os.path.join(outputDirTemp, file_name)

        doc = xml.dom.minidom.parse(each)
        collection = doc.documentElement
        if collection.getElementsByTagName('node'):
            nodes = collection.getElementsByTagName('node')

            for node in nodes:
                node.setAttribute(attrName, key)

        with open(file_path_temp, 'w') as f:
            doc.writexml(f, addindent="    ", newl="\n", encoding="UTF-8")

        delblankline(file_path_temp, file_path)

        # print('Done!')


def findDefaultFile(input_dir, vel_dict):
    print("******Finding default files ******")
    file_name = []

    for each in vel_dict.values():
        file_name.extend(each)

    filepath_list = []

    for maindir, subdir, file_list_str in os.walk(input_dir):
        file_list = []

        for each in file_list_str:
            file_number = int(each[:-4])

            if file_number not in file_name:
                file_list.append(file_number)

        for each in sorted(file_list):
            filename = str(each) + '.xml'
            filepath = os.path.join(maindir, filename)
            filepath_list.append(filepath)

    print("Dir <%s> find %d mached XML files." % (maindir, len(filepath_list)))
    # print(filepath_list)

    return filepath_list


def addSegAttr(inputWsDir, outputDir, attrName, attrDict):
    out2inDir = os.path.join(inputWsDir, 'seg_attr_out2in')
    if os.path.isdir(out2inDir):
        shutil.rmtree(out2inDir)

    if os.listdir(outputDir):
        print("Dir <%s> is not empty" % outputDir)

        os.rename(outputDir, out2inDir)
        os.mkdir(outputDir)
        inputSegDir = out2inDir
    else:
        inputSegDir = os.path.join(inputWsDir, "seg")

    outputDirTemp = outputDir + "_temp"

    if not os.path.isdir(outputDirTemp):
        print('Make dir <%s>.' % outputDirTemp)
        os.mkdir(outputDirTemp)

    else:
        print('Delete and make new dir <%s>.' % outputDirTemp)
        shutil.rmtree(outputDirTemp)
        os.mkdir(outputDirTemp)

    defaultFilePaths = findDefaultFile(inputSegDir, attrDict)

    for key, value in attrDict.items():
        if not value:
            filePaths = defaultFilePaths
        else:
            filePaths = findFile(inputSegDir, value)
        writeSegAttr(outputDir, outputDirTemp, key, filePaths, attrName)

    shutil.rmtree(outputDirTemp)
    if os.path.isdir(out2inDir):
        shutil.rmtree(out2inDir)


if __name__ == "__main__":
    ws_dir_path = "/home/mengze/Desktop/changsha_May22"

    input_dir = os.path.join(ws_dir_path, "seg")
    output_dir = ws_dir_path + "_vel"

    if not os.path.isdir(output_dir):
        print('Make dir <%s>.' % output_dir)
        os.mkdir(output_dir)

    else:
        print('Delete and make new dir <%s>.' % output_dir)
        shutil.rmtree(output_dir)
        os.mkdir(output_dir)

    output_dir_temp = output_dir + "_temp"

    if not os.path.isdir(output_dir_temp):
        print('Make dir <%s>.' % output_dir_temp)
        os.mkdir(output_dir_temp)

    else:
        print('Delete and make new dir <%s>.' % output_dir_temp)
        shutil.rmtree(output_dir_temp)
        os.mkdir(output_dir_temp)

    # vel_list = {'vel1':[seg, ..., seg], 'vel2':[seg, ..., seg], ...}
    # 高速公路 60km/h, 16.7m/s
    # 乡村道路 3m/s
    # 越野道路 5m/s
    # 其他 30km/h, 8.3m/s
    list1 = [n for n in range(600000, 810000, 10000)]
    list1_rm = [600000, 610000, 710000, 720000, 730000, 800000]
    for each in list1_rm:
        list1.remove(each)

    list2 = [n for n in range(150000, 260000, 10000)]
    vel_dict = {'16.7': [810000, 830000],
                '3': list1,
                '5': list2,
                '8.3': []}

    default_file_paths = findDefaultFile(input_dir, vel_dict)

    for key, value in vel_dict.items():
        if not value:
            file_paths = default_file_paths
        else:
            file_paths = findFile(input_dir, value)
        writeSegAttr(output_dir, output_dir_temp, key, file_paths, attrName='vel')

    shutil.rmtree(output_dir_temp)
