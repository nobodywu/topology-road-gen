# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import shutil
import xml.dom.minidom


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


def findAllPath(dirName):
    filepathList = []

    for maindir, subdir, fileListStr in os.walk(dirName):
        fileList = []
        for each in fileListStr:
            try:
                fileNumber = int(each[:-4])
                fileList.append(fileNumber)
            except:
                print('Ignore <%s>' % each)

        for each in sorted(fileList):
            filename = str(each) + '.xml'
            filepath = os.path.join(maindir, filename)
            filepathList.append(filepath)

    print("Dir <%s> has %d XML files." % (maindir, len(filepathList)))

    return filepathList


def addPointAttr(inputWsDir, outputDir, attrName, attrDict):
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

    filepathList = findAllPath(inputSegDir)

    valueAll = []
    for key, value in attrDict.items():
        valueAll.extend(value)
        if not value:
            default = key

    for each in filepathList:
        fileName = os.path.basename(each)
        filePath = os.path.join(outputDir, fileName)
        filePathTemp = os.path.join(outputDirTemp, fileName)

        doc = xml.dom.minidom.parse(each)
        collection = doc.documentElement
        if collection.getElementsByTagName('node'):
            nodes = collection.getElementsByTagName('node')

        for node in nodes:
            if node.getAttribute("id"):
                nodeId = node.getAttribute("id")

                if int(nodeId) in valueAll:
                    print('Attribute <%s>, find node %d' % (attrName, int(nodeId)))
                    for key, value in attrDict.items():
                        if int(nodeId) in value:
                            # print(nodeId, value)
                            node.setAttribute(attrName, key)
                else:
                    node.setAttribute(attrName, default)

        with open(filePathTemp, 'w') as f:
            doc.writexml(f, addindent="    ", newl="\n", encoding="UTF-8")

        delblankline(filePathTemp, filePath)

    shutil.rmtree(outputDirTemp)
    if os.path.isdir(out2inDir):
        shutil.rmtree(out2inDir)


if __name__ == '__main__':
    dirWsPath = "/home/mengze/Desktop/changsha_May22"
    inputSegDir = os.path.join(dirWsPath, "seg")
    filepathList = findAllPath(inputSegDir)
    # print(filepathList)

    for each in filepathList:
        doc = xml.dom.minidom.parse(each)
        collection = doc.documentElement
        if collection.getElementsByTagName('node'):
            nodes = collection.getElementsByTagName('node')

        for node in nodes:
            if node.getAttribute("id"):
                print(node.getAttribute("id"))
