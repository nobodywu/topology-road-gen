# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import shutil
from pykml import parser
from tkinter import filedialog as td
from tkinter import messagebox as tm
import numpy as np
import pyproj
import tkinter as tk
import re
import webbrowser
import hashlib
import time
import subprocess
try:
    import topologicalRoadGen.setJunctions as sj
except:
    import setJunctions as sj  # for module test

try:
    import topologicalRoadGen.showLink as sl
except:
    import showLink as sl

try:
    import topologicalRoadGen.pathPlanning as pp
except:
    import pathPlanning as pp


class MakeFolder(tk.Toplevel):
    def __init__(self, master, title=None):
        tk.Toplevel.__init__(self, master)

        self.centerPos()
        self.title(title)
        self.dir_name = tk.StringVar()  # Creating the variables that will get the user's input.

        self.label = tk.Label(self, text="请输入工作空间名称，将在桌面上创建此目录 ").pack(side=tk.TOP)
        self.entry = tk.Entry(self, textvariable=self.dir_name).pack(fill=tk.BOTH, expand=1)

        self.makeButtons()
        self.grab_set()

    def centerPos(self):
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws / 2) - (300 / 2)
        y = (hs / 2) - (50 / 2)
        self.geometry('%dx%d+%d+%d' % (300, 50, x, y))
        self.wm_attributes('-topmost', 1)

    def makeButtons(self):
        tk.Button(self, text="创建/打开", command=lambda: self.openWs(
            self.dir_name.get())).pack(side=tk.BOTTOM)

    def destory(self):
        self.destroy()

    def openWs(self, dir_name):

        if not dir_name:
            tm.showinfo('提示', '请重新打开工作空间')
            self.destroy()
        else:

            home = os.path.expanduser('~')
            dir_path = os.path.join(home, 'Desktop', dir_name)

            global ws_dir
            global ws_dir_temp_seg
            global ws_dir_seg
            global file_config

            ws_dir = dir_path
            ws_dir_temp_seg = os.path.join(ws_dir, 'temp_seg')
            ws_dir_seg = os.path.join(ws_dir, 'seg')
            file_config = os.path.join(ws_dir, 'config.txt')

            try:
                # 工作空间是否存在
                if not os.path.isdir(ws_dir):
                    print('Making dir <%s>.' % ws_dir)
                    os.mkdir(ws_dir)
                else:
                    print('Dir <%s> exist.' % ws_dir)
                    text = '工作空间目录<%s>已存在' % ws_dir
                    tm.showinfo('提示', text)

                # 暂存路段的目录是否存在
                if not os.path.isdir(ws_dir_temp_seg):
                    print('Making dir <%s>.' % ws_dir_temp_seg)
                    os.mkdir(ws_dir_temp_seg)
                else:
                    print('Dir <%s> exist.' % ws_dir_temp_seg)
                    # text = '暂存路段目录<%s>已存在' % ws_dir_temp_seg
                    # tm.showinfo('提示', text)

                # 路段的目录是否存在
                if not os.path.isdir(ws_dir_seg):
                    print('Making dir <%s>.' % ws_dir_seg)
                    os.mkdir(ws_dir_seg)
                else:
                    print('Dir <%s> exist.' % ws_dir_seg)

                # config是否存在
                if not os.path.isfile(file_config):
                    print('Making file <%s>.' % file_config)
                    self.write_config(file_config)
                else:
                    print('Amending <%s>.' % file_config)
                    self.amend_config_time(file_config)

                self.destory()
                text = '工作空间<%s>已准备就绪' % dir_path
                tm.showinfo('提示', text)

            except:
                print('Please enter an dir name')
                tm.showinfo('提示', '进入工作空间失败\n请点击开始菜单-->创建/打开工作空间')
                self.destory()

    def write_config(self, file_name):
        with open(file_name, 'w') as f:
            text = []
            localtime = time.asctime(time.localtime(time.time()))
            line1 = '创建时间：' + localtime + '\n'
            text.append(line1)
            line2 = '访问时间：' + localtime + '\n'
            text.append(line2)
            line3 = 'KML文件MD5：未打开KML文件' + '\n'
            text.append(line3)
            line4 = 'KML文件路径：未打开KML文件' + '\n'
            text.append(line4)

            # Author information
            text.append('\n**********************************\n')
            info = '拓扑路网生成UI\n作者：NobodyWu\n邮箱：mengze.bit@gmail.com'
            text.append(info)

            f.writelines(text)

    def amend_config_time(self, file_name):
        with open(file_name, 'r+') as f:
            text = f.readlines()
            localtime = time.asctime(time.localtime(time.time()))
            line2 = '访问时间：' + localtime + '\n'
            text[1] = line2
            f.seek(0, 0)
            f.writelines(text)


class HyperlinkMessageBox(tk.Toplevel):
    '''
    HyperlinkMessageBox类的代码来自Stack Overflow的问题'tk tkMessageBox html link'
    https://stackoverflow.com/questions/13508043/tk-tkmessagebox-html-link
    '''
    hyperlinkPattern = re.compile(r'<a href="(?P<address>.*?)">(?P<title>.*?)'
                                  '</a>')

    def __init__(self, master, title=None, message=None, **options):
        tk.Toplevel.__init__(self, master)
        self.geometry("200x200")
        self.title(title or master.title())
        self.text = tk.Text(self, wrap=tk.WORD,
                            bg=master.cget('bg'), height=self.cget('height'))
        self._formatHyperLink(message)
        self.text.config(state=tk.DISABLED)
        self.text.pack(side=tk.TOP, fill=tk.X)
        self.makeButtons()

    def makeButtons(self):
        tk.Button(self, text="确定", command=lambda *a, **k: self.destroy()).pack()

    def _formatHyperLink(self, message):
        text = self.text
        start = 0
        for index, match in enumerate(self.hyperlinkPattern.finditer(message)):
            groups = match.groupdict()
            text.insert("end", message[start: match.start()])
            # insert hyperlink tag here
            text.insert("end", groups['title'])
            text.tag_add(str(index),
                         "end-%dc" % (len(groups['title']) + 1),
                         "end",)
            text.tag_config(str(index),
                            foreground="blue",
                            underline=1)
            text.tag_bind(str(index),
                          "<Enter>",
                          lambda *a, **k: text.config(cursor="hand2"))
            text.tag_bind(str(index),
                          "<Leave>",
                          lambda *a, **k: text.config(cursor="arrow"))
            text.tag_bind(str(index),
                          "<Button-1>",
                          self._callbackFactory(groups['address']))
            start = match.end()
        else:
            text.insert("end", message[start:])

    def _callbackFactory(self, url):
        return lambda *args, **kwargs: webbrowser.open(url)


class App(tk.Frame):
    '''
    App类Canvas中Object放大缩小的代码来自Stack Overflow的问题'Move and zoom a tk canvas with mouse'
    https://stackoverflow.com/questions/25787523/move-and-zoom-a-tk-canvas-with-mouse
    '''

    def __init__(self, root):

        tk.Frame.__init__(self, root)
        # menubar
        self.menubar = tk.Menu(root)
        self.filemenu = tk.Menu(self.menubar, tearoff=False)
        self.filemenu.add_command(label="创建/打开工作空间", command=self.openWorkspace)
        self.filemenu.add_command(label="打开kml文件", command=self.openFile)
        self.filemenu.add_command(label="保存暂存路段", command=self.saveAllSeg)
        self.menubar.add_cascade(label="文件", menu=self.filemenu)

        self.editmenu = tk.Menu(self.menubar, tearoff=False)
        self.editmenu.add_command(label="删除路段", command=self.deleteSeg)
        self.editmenu.add_command(label="生成路网", command=self.genTopologyRoad)
        self.menubar.add_cascade(label="编辑", menu=self.editmenu)

        self.viewmenu = tk.Menu(self.menubar, tearoff=False)
        self.viewmenu.add_command(label="重置视图", command=self.openFile)
        self.viewmenu.add_command(label="检查路网", command=self.inspectRoad)
        self.viewmenu.add_command(label="最短路径", command=self.getshortestPath)
        self.menubar.add_cascade(label="视图", menu=self.viewmenu)

        self.helpmenu = tk.Menu(self.menubar, tearoff=False)
        self.helpmenu.add_command(label="操作提示", command=self.helpMSG)
        self.helpmenu.add_command(label="关于", command=self.aboutMSG)
        self.menubar.add_cascade(label="帮助", menu=self.helpmenu)
        root.config(menu=self.menubar)
        self.initCanvas()

        # open workspace

        self.openWorkspace()

    def initCanvas(self):
        # 端点提示范围
        self.radius = 14  # distance m
        self.scalePC = 0
        # canvas
        # bisque, a pink to yellowish tan colour
        self.canvas = tk.Canvas(self, width=1200, height=800, background="white")
        self.xsb = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.ysb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.ysb.set, xscrollcommand=self.xsb.set)
        # A tuple (w, n, e, s) that defines over how large an area the canvas can be scrolled, where w is the left side, n the top, e the right side, and s the bottom.
        self.canvas.configure(scrollregion=(-100, -100, 1300, 900))

        self.xsb.grid(row=1, column=0, sticky="ew")
        self.ysb.grid(row=0, column=1, sticky="ns")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        # 第一行第一列分配全部空间
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # This is what enables using the mouse:
        self.canvas.bind("<ButtonPress-1>", self.moveStart)
        self.canvas.bind("<B1-Motion>", self.moveMove)
        # linux scroll
        self.canvas.bind("<Button-4>", self.zoomerP)
        self.canvas.bind("<Button-5>", self.zoomerM)

        # print mouse position
        self.canvas.bind("<Motion>", self.printMousePosition)
        # select object
        self.canvas.bind("<ButtonPress-3>", self.selectObject)
        self.canvas.bind("<Escape>", self.deletePoint)
        self.canvas.bind("<Return>", self.appendSeg)

    # menubar start
    def openWorkspace(self):
        MakeFolder(self, '创建/打开工作空间')

    def openFile(self):

        if 'ws_dir' not in globals():
            self.openWorkspace()
        else:
            self.canvas.destroy()
            self.initCanvas()
            self.onFileRead = False
            self.points = []
            self.itemSelected = []
            self.allSeg = []
            self.allSegItem = []
            self.endPointsItemSelected = []
            self.config_info = []
            self.all_temp_seg_items = []
            self.config_info = self.get_config(file_config)
            self.canvas_scale = 1

            # 如果config文件中有kml文件
            if self.config_info:
                ws_kml_file = self.config_info[1].strip()
                self.getPointsOld(ws_kml_file)

            else:
                self.getPoints()

            # 如果有暂存的路段
            path_list = getDocPaths(ws_dir_temp_seg)
            if len(path_list):
                end_items = self.get_temp_node_items(path_list)
                for each in self.all_temp_seg_items:
                    self.canvas.itemconfig((int(each),), fill='black', outline='black')
                    self.canvas.tag_raise((int(each),))

                for each in end_items:
                    self.showEndPointRange((int(each),))  # no need return value

    def get_temp_node_items(self, path_list):
        self.all_temp_seg_items = []
        end_items = []
        for each in path_list:
            nodes = np.loadtxt(each, skiprows=(1))
            seg_items = nodes[:, 4]
            self.all_temp_seg_items = np.concatenate((self.all_temp_seg_items, seg_items))
            end_items.append(seg_items[0])
            end_items.append(seg_items[-1])

        return end_items

    def getPointsOld(self, fileName):
        print('File %s exist.' % fileName)

        self.points = parseKML(fileName)
        self.showPoints(self.points)
        self.onFileRead = True

    def getPoints(self):
        '''
        读取文件中的点，每次读取文件之前首先初始化画布。
        '''
        print('Choose a new kml file.')

        try:
            fileName = td.askopenfilename(
                filetypes=[("KML Files", ".kml"), ('All files', '*')])
        except:
            sys.exit()

        if fileName:
            with open(fileName, 'rb') as f:
                md5 = self.get_file_md5(f)

            self.amend_config_md5(file_config, md5)

            print('File path <%s>.' % fileName)
            cmd = 'cp %s %s' % (fileName, ws_dir)
            os.system(cmd)
            print('System: %s' % cmd)

            kml_file_name = os.path.basename(fileName)
            kml_file_path = os.path.join(ws_dir, kml_file_name)
            self.amend_config_path(file_config, kml_file_path)

            self.points = parseKML(fileName)
            self.showPoints(self.points)
            self.onFileRead = True
        else:
            tm.showinfo('提示', '请选择一个kml文件')

    def saveAllSeg(self):
        '''
        保存已暂存的所有路段，通过对话框制定文件目录和文件名，默认文件后缀为'.txt'。
        '''
        if 'ws_dir' not in globals():
            self.openWorkspace()
        else:

            filePathList = getDocPaths(ws_dir_temp_seg)
            if len(filePathList):
                lastFile = filePathList[-1]
                lastFileName = os.path.basename(lastFile)
                lastNumber = int(lastFileName[:-4])
                print('File: the last is %s.' % lastFileName)
                i = lastNumber + 10000
            else:
                i = 10000

            try:
                if len(self.allSeg):
                    for seg in self.allSeg:
                        fileName = str(i) + '.txt'
                        filePath = os.path.join(ws_dir_temp_seg, fileName)
                        writeTXT(filePath, seg)
                        print('File <%s> generated.' % filePath)
                        i = i + 10000

                    text = '暂存的路段文件已保存在目录 <%s> 下，\n本次保存%d个路段。' \
                        % (ws_dir_temp_seg, len(self.allSeg))
                    tm.showinfo('提示', text)
                    self.allSeg = []

                else:
                    tm.showinfo('提示', '没有暂存的路段')

            except:
                tm.showinfo('提示', '请打开kml文件并选择路段')

    # menubar edit
    def deleteSeg(self):
        '''
        删除上一段路，每次删除一段。当前焦点需要在画布上。
        '''
        if 'ws_dir' not in globals():
            self.openWorkspace()
        else:

            self.canvas.focus_set()
            # self.canvas.focus_lastfor()
            if len(self.allSeg):
                self.allSeg.pop()
                items = self.allSegItem.pop()
                print(items)
                allSegItemInOne = []
                for each in self.allSegItem:
                    allSegItemInOne.extend(each)

                for item in items:
                    # 如果点以保存的暂存路段temp_seg中变为黑色，否则变为红色
                    if item in self.all_temp_seg_items:
                        self.canvas.itemconfig(item, fill='black', outline='black')
                        self.canvas.tag_raise(item)
                    elif item in allSegItemInOne:
                        self.canvas.itemconfig(item, fill='green', outline='green')
                        self.canvas.tag_raise(item)
                    else:
                        self.canvas.itemconfig(item, fill='red', outline='red')

                # delete end points
                item1 = self.endPointsItemSelected.pop()
                item2 = self.endPointsItemSelected.pop()
                self.canvas.delete(item1)
                self.canvas.delete(item2)

                print('removed last segment')
                print('remain %d, %d segments.' % (len(self.allSeg), len(self.allSegItem)))
            else:
                tm.showinfo('提示', '没有暂存路段')

    def getshortestPath(self):
        if 'ws_dir' not in globals():
            self.openWorkspace()
        else:
            file_config = os.path.join(ws_dir, 'config.txt')
            file_points = os.path.join(ws_dir, 'points.txt')
            file_junctions = os.path.join(ws_dir, 'junctions.txt')

            ws_dirs = [ws_dir, ws_dir_temp_seg, ws_dir_seg,
                       file_config, file_points, file_junctions]
            pp.get_shorest_path(ws_dirs)

    def inspectRoad(self):
        if 'ws_dir' not in globals():
            self.openWorkspace()
        else:
            ws_dirs = [ws_dir, ws_dir_temp_seg, ws_dir_seg]
            sl.inspect(ws_dirs)

    def genTopologyRoad(self):
        if 'ws_dir' not in globals():
            self.openWorkspace()
        else:
            print('source path <%s>' % ws_dir_temp_seg)
            print('target path <%s>' % ws_dir_seg)
            shutil.rmtree(ws_dir_seg)
            os.mkdir(ws_dir_seg)

            ws_dirs = [ws_dir, ws_dir_temp_seg, ws_dir_seg]
            sj.genRoad(ws_dirs)

    def helpMSG(self):
        self.helpMSG = HyperlinkMessageBox(
            self, "操作提示", '操作步骤详见 <a href="https://github.com/nobodywu/topology_road_gen">Github </a>。')

    def aboutMSG(self):
        print('aboutMSG')
        self.aboutMSG = HyperlinkMessageBox(
            self, "关于", '版本：v4.0.20190120。作者：NobodyWu。')

    # mouse event
    def printMousePosition(self, event):
        # print(event)
        pass

    def deletePoint(self, event):
        '''
        删除当前路段上的点，每次删除一个。当前焦点需要在画布上。
        '''
        self.canvas.focus_set()

        allSegItemInOne = []
        for each in self.allSegItem:
            allSegItemInOne.extend(each)

        # self.canvas.focus_lastfor()
        if len(self.itemSelected):
            item = self.itemSelected.pop()
            # 如果点以保存的暂存路段temp_seg中变为黑色，否则变为红色
            if item in self.all_temp_seg_items:
                self.canvas.itemconfig(item, fill='black', outline='black')
                self.canvas.tag_raise(item)
            elif item in allSegItemInOne:
                self.canvas.itemconfig(item, fill='green', outline='green')
                self.canvas.tag_raise(item)
            else:
                self.canvas.itemconfig(item, fill='red', outline='red')
            # print(self.itemSelected)
            # print('deleted last point')
        else:
            tm.showinfo('提示', '当前路段没有点')

    def appendSeg(self, event):
        '''
        暂存选择的路段。当前焦点需要在画布上。
        '''
        segment = []
        self.canvas.focus_set()
        # self.canvas.focus_lastfor()
        if len(self.itemSelected) >= 3:
            for item in self.itemSelected:
                itemPoint = self.points[item[0] - 1]
                itemPoint.append(item[0])
                segment.append(itemPoint)  # item start from 1
                self.canvas.itemconfig(item, fill='green', outline='green')

            self.allSeg.append(segment)
            self.allSegItem.append(self.itemSelected)  # 为了知道每段点的tags or id，在删除时更改颜色
            # print(self.allSeg)
            # print('%d, %d segments' % (len(self.allSeg), len(self.allSegItem)))

            # show segment end points range, selected seg
            item1 = self.showEndPointRange(self.itemSelected[0])
            item2 = self.showEndPointRange(self.itemSelected[-1])
            self.endPointsItemSelected.append(item1)
            self.endPointsItemSelected.append(item2)

            print('new item', item1, item2)

            print('%d segment appended' % len(self.allSeg))
            text = '已确认%d段路' % len(self.allSeg)
            tm.showinfo('提示', text)
            self.itemSelected = []
        else:
            tm.showinfo('提示', '路点数量小于3')

    def showEndPointRange(self, item):
        # use item to calc position, creat a dash circle, return new object item
        x0, y0, x1, y1 = self.canvas.coords(item)
        posX = (x1 + x0) / 2
        posY = (y1 + y0) / 2
        rScale = self.radius * self.canvas_scale / self.scalePC

        # stay original size when zoomerM or zoomerP
        item_new = self.canvas.create_oval(posX - rScale, posY - rScale,
                                           posX + rScale, posY + rScale, dash=(5, 5))

        return item_new

    def selectObject(self, event):
        '''
        代码参考Stack Overflow的问题'Identify object on click'
        https://stackoverflow.com/questions/38982313/python-tk-identify-object-on-click
        '''
        true_x = self.canvas.canvasx(event.x)
        true_y = self.canvas.canvasy(event.y)
        item = self.canvas.find_closest(true_x, true_y)
        # item start from 1, python lists start from 0, item structure: (n,)
        if item[0] <= len(self.points):
            print(item[0])
            print(item[0], self.points[item[0] - 1])
            currentColor = self.canvas.itemcget(item, 'fill')
            # 红色：未选中 绿色：已暂存 黑色：打开工作空间时显示temp_seg路段中的点
            if (currentColor == 'red') | (currentColor == 'green') | (currentColor == 'black'):
                self.canvas.itemconfig(item, fill='#2F4F4F', outline='#2F4F4F')  # 墨绿色
                self.canvas.tag_raise(item)
                self.itemSelected.append(item)
                print(self.itemSelected)  # for item in itemSelected: points[item[0]]
        else:
            tm.showinfo('提示', '请将鼠标靠近路点，远离虚线范围提示框')

    # move
    def moveStart(self, event):
        self.canvas.scan_mark(event.x, event.y)
        self.canvas.focus_set()  # security, set the focus on the Canvas

    def moveMove(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    # zoom
    def zoomerP(self, event):
        if self.onFileRead:
            true_x = self.canvas.canvasx(event.x)
            true_y = self.canvas.canvasy(event.y)
            self.canvas.scale("all", true_x, true_y, 1.1, 1.1)
            self.canvas_scale = self.canvas_scale * 1.1
            # print(self.canvas_scale)
            # enlarge scroll area
            x0, y0, x1, y1 = self.canvas.bbox("all")
            self.canvas.configure(scrollregion=[x0 - 200, y0 - 200, x1 + 200, y1 + 200])
            self.reshowPoints()
        else:
            print('Please open a kml file.')

    def zoomerM(self, event):
        if self.onFileRead:
            true_x = self.canvas.canvasx(event.x)
            true_y = self.canvas.canvasy(event.y)
            self.canvas.scale("all", true_x, true_y, 0.9, 0.9)
            self.canvas_scale = self.canvas_scale * 0.9
            # print(self.canvas_scale)
            # x0, y0, x1, y1 = self.canvas.bbox("all")
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            self.reshowPoints()

        else:
            print('Please open a kml file.')

    # other

    def reshowPoints(self):
        '''
        根据放大缩小的比例显示点，保证点大小一致。
        '''
        for i in range(len(self.points)):
            x0, y0, x1, y1 = self.canvas.coords(i + 1)
            posX = (x1 + x0) / 2
            posY = (y1 + y0) / 2
            self.canvas.coords(i + 1, posX - 4, posY - 4, posX + 4, posY + 4)

    def showPoints(self, points):
        '''
        显示当前文件中的点。
        '''

        pointsPCS = projPoints(points)
        pointsRangePCS = getPointsRange(pointsPCS)
        # print(pointsRangePCS)
        xRange = pointsRangePCS[1] - pointsRangePCS[0]
        yRange = pointsRangePCS[3] - pointsRangePCS[2]

        print('Points xyRange: ', xRange, yRange)
        print('Canvas xyRange: ', 1200, 800)
        xRatio = xRange / 1200
        yRatio = yRange / 800

        print('xyRatio: ', xRatio, yRatio)

        if xRatio <= yRatio:
            self.scalePC = yRatio
        else:
            self.scalePC = xRatio

        print('max(Points xyR / Canvas xyR) = scalePC: ', self.scalePC)
        for i in range(pointsPCS.shape[0]):

            posX = (pointsPCS[i, 0] - pointsRangePCS[0]) / self.scalePC
            # reverse y-axis
            posY = 800 - (pointsPCS[i, 1] - pointsRangePCS[2]) / self.scalePC

            self.canvas.create_oval(posX - 4, posY - 4, posX + 4, posY + 4,
                                    fill='red', outline='red', tags=i + 1)  # item start from 1

    def get_file_md5(self, f):
        m = hashlib.md5()
        while True:
            # 如果不用二进制打开文件，则需要先编码
            # data = f.read(1024).encode('utf-8')
            data = f.read(1024)  # 为避免文件过大分块读取
            if not data:
                break
            m.update(data)
        return m.hexdigest()

    def amend_config_md5(self, file_config, md5):
        with open(file_config, 'r+') as f:
            text = f.readlines()
            line3 = 'KML文件MD5：' + md5 + '\n'
            text[2] = line3
            f.seek(0, 0)
            f.writelines(text)

    def amend_config_path(self, file_config, file_kml):
        with open(file_config, 'r+') as f:
            text = f.readlines()
            line4 = 'KML文件路径：' + file_kml + '\n'
            text[3] = line4
            f.seek(0, 0)
            f.writelines(text)

    def get_config(self, file_config):
        with open(file_config, 'r') as f:
            text = f.readlines()
            line3 = text[2]
            config_md5 = line3[9:]
            line4 = text[3]
            kml_path = line4[8:]

        if config_md5 == '未打开KML文件\n' and kml_path == '未打开KML文件\n':
            config_info = []
            return config_info
        else:
            config_info = [config_md5, kml_path]
            return config_md5, kml_path


def parseKML(file):
    '''
    接收kml文件路径，解析kml文件,返回文件中的所有点。
    全局变量points包含kml文件中的所有点，每个点由经度，纬度和海拔高度表示。精度为小数点后8位。
    points = [[lon, lat, alt], [lon, lat, alt], ...]
    '''
    points = []
    try:
        with open(file, 'r') as f:
            kml = parser.parse(f).getroot()
            placemarks = kml.findall('.//{http://www.opengis.net/kml/2.2}Placemark')

            for each in placemarks:
                coords = str(each.LineString.coordinates)
                points_seg = coords.strip().split(' ')
                for each in points_seg:
                    each = each.split(',')
                    each = [float(each[0]), float(each[1]), float(each[2])]
                    points.append(each)

        print('File <%s> has %d placemarksc and %d points.' % (file, len(placemarks), len(points)))
        return points

    except:
        tm.showinfo('提示', '请检查kml文件')


def projPoints(pointsGPS):
    '''
    坐标系转换，把地理坐标系上的点转换到投影坐标系上。
    '''
    pointsGPS = np.array(pointsGPS)

    p1 = pyproj.Proj(init="epsg:4326")
    p2 = pyproj.Proj(init="epsg:3857")
    pointsGPS[:, 0], pointsGPS[:, 1], pointsGPS[:, 2] = pyproj.transform(
        p1, p2, pointsGPS[:, 0], pointsGPS[:, 1], pointsGPS[:, 2])

    pointsPCS = pointsGPS
    # print(pointsPCS)
    return pointsPCS


def getPointsRange(pointsPCS):
    '''
    获得投影坐标系上点的范围。
    返回一个列表[最小x，最大x, 最小y, 最大y, 最小z, 最大z]
    '''
    pointsPCS = np.array(pointsPCS)
    xyzmin = pointsPCS.min(axis=0)
    xyzmax = pointsPCS.max(axis=0)

    return [xyzmin[0], xyzmax[0], xyzmin[1], xyzmax[1], xyzmin[2], xyzmax[2]]


def writeTXT(fileName, seg):
    '''
    保存已暂存的所有路段。
    allSeg = [seg1, seg2, seg3, ...]
    eachSeg = [point1, point2, point3, ...]
    eachPoint = [lon, lat, alt]
    '''

    i = 1  # line number
    with open(fileName, 'w') as f:
        f.write('num lon lat alt item\n')  # 'item' used for showing point in canvas

        for point in seg:
            line = str(i) + ' ' + str(point[0]) + ' ' + \
                str(point[1]) + ' ' + str(point[2]) + ' ' + str(point[3]) + '\n'
            f.write(line)
            i += 1

        i = 1


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
            filename = str(each) + '.txt'
            filepath = os.path.join(maindir, filename)
            filepathList.append(filepath)

    print("Dir <%s> has %d files." % (maindir, len(filepathList)))

    return filepathList


if __name__ == "__main__":
    root_win_name = '创建拓扑路网'

    cmd = 'wmctrl -lG | grep \'' + root_win_name + '\' | awk \'{print $1}\''
    win_id = subprocess.check_output(["/bin/bash", "-c", cmd]).decode("utf-8")
    win_id = win_id.split()
    if len(win_id):
        print('Close former process, id: ', win_id)
        for each in win_id:
            cmd = 'wmctrl -ic ' + each
            os.system(cmd)

    root = tk.Tk()
    root.title(root_win_name)
    # root.iconbitmap(r'full path name')
    App(root).pack(fill="both", expand=1)  # fill 控件的填充方向 expand 控件随着窗口的控件填充
    root.mainloop()
