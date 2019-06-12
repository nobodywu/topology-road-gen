# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import xml.etree.ElementTree as et
import lib.addPointAttr as apoint
import lib.addSegAttr as aseg


def validateEnv(outputDir):

    if not os.path.isdir(outputDir):
        print('Make dir <%s>.' % outputDir)
        os.mkdir(outputDir)

    else:
        print('Delete and make new dir <%s>.' % outputDir)
        shutil.rmtree(outputDir)
        os.mkdir(outputDir)


def readConfig(configFile):
    tree = et.parse(configFile)
    root = tree.getroot()

    attrList = []

    for sub in root:
        subList = []
        subList.append(sub.tag)
        defaultValue = sub.attrib['default']

        subDict = {}
        subDict[defaultValue] = []
        subType = []
        for each in sub:

            # node or seg, list.append can't add same element
            subType.append(each.tag)

            subDict[each.attrib['value']] = [int(n) for n in each.text.split(',')]

        print(subType)

        if(len(set(subType)) == 1):
            print('Set attribute <%s> according to <%s>.' % (sub.tag, subType[0]))
        else:
            print("Attribute can only be added by <node> or <seg>, not mixed. Please check <%s> in config.xml" % sub.tag)

        subList.append(subType[0])
        subList.append(subDict)

        attrList.append(subList)

    return attrList


def addAttr(inputWsDir, config):
    outputDir = os.path.join(inputWsDir, 'seg_attr')

    validateEnv(outputDir)
    attrList = readConfig(config)

    for attrName, attrType, attrDict in attrList:
        print('######')
        print(attrName, attrType, attrDict)

        if attrType == 'node':
            apoint.addPointAttr(inputWsDir, outputDir, attrName, attrDict)
        elif attrType == 'seg':
            aseg.addSegAttr(inputWsDir, outputDir, attrName, attrDict)
        else:
            print('not <note> or <seg>')


if __name__ == '__main__':
    inputWsDir = '/home/mengze/Desktop/changsha_May22'
    config = '/home/mengze/Desktop/test.xml'

    outputDir = os.path.join(inputWsDir, 'seg_attr')

    validateEnv(outputDir)
    attrList = readConfig(config)

    for attrName, attrType, attrDict in attrList:
        print('######')
        print(attrName, attrType, attrDict)

        if attrType == 'node':
            apoint.addPointAttr(inputWsDir, outputDir, attrName, attrDict)
        elif attrType == 'seg':
            aseg.addSegAttr(inputWsDir, outputDir, attrName, attrDict)
        else:
            print('not <note> or <seg>')
