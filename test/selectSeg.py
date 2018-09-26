import sys
import os
import shutil
from pykml import parser
from tkinter import filedialog as td
from tkinter import messagebox as tm
import numpy as np
import pyproj
import tkinter as tk
import xml.dom.minidom
import re
import webbrowser
import setJunctions as sj

# import random


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
        tk.Button(self, text="Ok", command=lambda *a, **k: self.destroy()).pack()

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
        self.filemenu.add_command(label="打开", command=self.getPoints)
        self.filemenu.add_command(label="保存", command=self.saveAllSeg)
        self.menubar.add_cascade(label="文件", menu=self.filemenu)

        self.editmenu = tk.Menu(self.menubar, tearoff=False)
        self.editmenu.add_command(label="删除路段", command=self.deleteSeg)
        self.editmenu.add_command(label="生成路网", command=self.genTopologyRoad)
        self.menubar.add_cascade(label="编辑", menu=self.editmenu)

        self.viewmenu = tk.Menu(self.menubar, tearoff=False)
        self.viewmenu.add_command(label="重置视图", command=self.initView)
        self.menubar.add_cascade(label="视图", menu=self.viewmenu)

        self.helpmenu = tk.Menu(self.menubar, tearoff=False)
        self.helpmenu.add_command(label="操作提示", command=self.helpMSG)
        self.helpmenu.add_command(label="关于", command=self.aboutMSG)
        self.menubar.add_cascade(label="帮助", menu=self.helpmenu)
        root.config(menu=self.menubar)
        self.initCanvas()

    def initCanvas(self):
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

    def printMousePosition(self, event):
        # print(event)
        pass

    def genTopologyRoad(self):
        sourcePath = td.askdirectory(title="Pick a source folder")
        print('source path <%s>' % sourcePath)
        targetPath = td.askdirectory(title="Pick a target folder")
        print('target path <%s>' % targetPath)
        shutil.rmtree(targetPath)
        os.mkdir(targetPath)
        writeTopologyRoad(sourcePath, targetPath)

    def helpMSG(self):
        print('helpMSG')
        self.helpMSG = HyperlinkMessageBox(
            root, "操作提示", '操作步骤详见 <a href="http://www.baidu.com">Baidu </a>.')

    def aboutMSG(self):
        print('aboutMSG')
        self.aboutMSG = HyperlinkMessageBox(
            root, "关于", '作者：NobodyWu，个人主页 <a href="http://www.baidu.com">Baidu </a>.')

    def saveAllSeg(self):
        '''
        保存已暂存的所有路段，通过对话框制定文件目录和文件名，默认文件后缀为'.txt'。
        '''
        try:
            if len(self.allSeg):
                fileName = td.asksaveasfilename(defaultextension='.kml',
                                                filetypes=[('All files', '*')])
                print(fileName)
                onWriteFile = writeFile(fileName, self.allSeg)
                if onWriteFile:
                    text = 'File <%s> saved, include %d segments.' % (fileName, len(self.allSeg))
                    tm.showinfo('提示', text)
                    self.allSeg = []
                else:
                    tm.showinfo('提示', '请检查文件格式')
            else:
                tm.showinfo('提示', '没有暂存的路段')

        except:
            tm.showinfo('提示', '请打开kml文件并选择路段')

    def deletePoint(self, event):
        '''
        删除当前路段上的点，每次删除一个。当前焦点需要在画布上。
        '''
        self.canvas.focus_set()
        # self.canvas.focus_lastfor()
        if len(self.itemSelected):
            item = self.itemSelected.pop()
            self.canvas.itemconfig(item, fill='red')
            # print(self.itemSelected)
            # print('deleted last point')
        else:
            tm.showinfo('提示', '当前路段没有点')

    def deleteSeg(self):
        '''
        删除上一段路，每次删除一段。当前焦点需要在画布上。
        '''
        self.canvas.focus_set()
        # self.canvas.focus_lastfor()
        if len(self.allSeg):
            self.allSeg.pop()
            items = self.allSegItem.pop()
            print(items)
            for item in items:
                self.canvas.itemconfig(item, fill='red')

            print('removed last segment')
            print('remain %d, %d segments.' % (len(self.allSeg), len(self.allSegItem)))
        else:
            tm.showinfo('提示', '没有暂存路段')

    def appendSeg(self, event):
        '''
        暂存选择的路段。当前焦点需要在画布上。
        '''
        segment = []
        self.canvas.focus_set()
        # self.canvas.focus_lastfor()
        if len(self.itemSelected):
            for item in self.itemSelected:
                segment.append(self.points[item[0] - 1])  # item start from 1
                self.canvas.itemconfig(item, fill='green')

            self.allSeg.append(segment)
            self.allSegItem.append(self.itemSelected)  # 为了知道每段点的tagsorid，在删除时更改颜色
            print(self.allSeg)
            print('%d, %d segments' % (len(self.allSeg), len(self.allSegItem)))
            print('segment appended')
            text = '已保存%d段路' % len(self.allSeg)
            tm.showinfo('提示', text)
            self.itemSelected = []
        else:
            tm.showinfo('提示', '请选择路点')

    def selectObject(self, event):
        '''
        代码参考Stack Overflow的问题'Identify object on click'
        https://stackoverflow.com/questions/38982313/python-tk-identify-object-on-click
        '''
        true_x = self.canvas.canvasx(event.x)
        true_y = self.canvas.canvasy(event.y)
        item = self.canvas.find_closest(true_x, true_y)
        print(item[0], self.points[item[0] - 1])  # item start from 1
        currentColor = self.canvas.itemcget(item, 'fill')
        if (currentColor == 'red') | (currentColor == 'green'):
            self.canvas.itemconfig(item, fill='black')
            self.itemSelected.append(item)
            print(self.itemSelected)  # for item in itemSelected: points[item[0]]

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
            # enlarge scroll area
            x0, y0, x1, y1 = self.canvas.bbox("all")
            self.canvas.configure(scrollregion=[x0 - 200, y0 - 200, x1 + 200, y1 + 200])
            self.canvasRatio *= 1.1
            # print(self.canvasRatio)
            self.reshowPoints()
        else:
            print('Please open a kml file.')

    def zoomerM(self, event):
        if self.onFileRead:
            true_x = self.canvas.canvasx(event.x)
            true_y = self.canvas.canvasy(event.y)
            self.canvas.scale("all", true_x, true_y, 0.9, 0.9)
            # x0, y0, x1, y1 = self.canvas.bbox("all")
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            self.canvasRatio *= 0.9
            # print(self.canvasRatio)
            self.reshowPoints()
        else:
            print('Please open a kml file.')

    def callback(self):
        print('hello')

    def initView(self):
        self.canvas.destroy()
        self.initCanvas()
        if self.onFileRead:
            self.showPoints(self.points)
        else:
            print('Please open a kml file.')

    def reshowPoints(self):
        '''
        根据放大缩小的比例显示点，保证点大小一致。
        '''
        for i in range(len(self.points)):
            x0, y0, x1, y1 = self.canvas.coords(i + 1)
            posX = (x1 + x0) / 2
            posY = (y1 + y0) / 2
            self.canvas.coords(i + 1, posX - 4, posY - 4, posX + 4, posY + 4)
        pass

    def showPoints(self, points):
        '''
        显示当前文件中的点。
        '''

        pointsPCS = projPoints(points)
        pointsRangePCS = getPointsRange(pointsPCS)
        # print(pointsRangePCS)
        xRange = pointsRangePCS[1] - pointsRangePCS[0]
        yRange = pointsRangePCS[3] - pointsRangePCS[2]

        xRatio = xRange / 1200
        xRatio = yRange / 800

        if xRatio <= yRange:
            xyscale = 800
        else:
            xyscale = 1200

        for i in range(pointsPCS.shape[0]):
            # print(i)

            posX = (pointsPCS[i, 0] - pointsRangePCS[0]) * xyscale / xRange
            # reverse y-axis
            posY = (1 - (pointsPCS[i, 1] - pointsRangePCS[2]) / yRange) * xyscale
            self.canvas.create_oval(posX - 4, posY - 4, posX + 4, posY + 4,
                                    fill='red', tags=i + 1)  # item start from 1

    def getPoints(self):
        '''
        读取文件中的点，每次读取文件之前首先初始化画布。
        '''
        self.canvas.destroy()
        self.initCanvas()
        self.onFileRead = False
        self.canvasRatio = 1.0
        self.points = []
        self.itemSelected = []
        self.allSeg = []
        self.allSegItem = []
        try:
            fileName = td.askopenfilename(
                filetypes=[("KML Files", ".kml"), ('All files', '*')])
        except:
            sys.exit()

        if fileName:
            print('File path <%s>.' % fileName)
            self.points = parseKML(fileName)
            self.showPoints(self.points)
            self.onFileRead = True
        else:
            tm.showinfo('提示', '请选择一个kml文件')


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


def writeFile(fileName, allSeg):
    '''
    保存已暂存的所有路段。
    allSeg = [seg1, seg2, seg3, ...]
    eachSeg = [point1, point2, point3, ...]
    eachPoint = [lon, lat, alt]
    '''
    acronym = os.path.splitext(fileName)
    print(acronym[-1])
    if acronym[-1] == '.txt':
        writeTXT(fileName, allSeg)
        return True
        print('File <%s> saved, include %d segments.' % (fileName, len(allSeg)))
    elif acronym[-1] == '.kml':
        writeKML(fileName, allSeg)
        print('File <%s> saved, include %d segments.' % (fileName, len(allSeg)))
        return True

    return False


def writeTXT(fileName, allSeg):
    i = 1  # 每段路点的个数
    with open(fileName, 'w') as f:
        for seg in allSeg:
            f.write('***********\n')

            for point in seg:
                line = str(i) + ' ' + str(point[0]) + ' ' + \
                    str(point[1]) + ' ' + str(point[2]) + '\n'
                f.write(line)
                i += 1

            i = 1


def writeKML(fileName, allSeg):
    filePath = os.path.dirname(fileName)
    shutil.rmtree(filePath)
    os.mkdir(filePath)
    print(filePath)
    i = 10000  # 表示文件名
    print(len(allSeg))
    for seg in allSeg:
        name = os.path.join(filePath, str(i) + '.xml')
        print(name)
        doc = xml.dom.minidom.Document()
        doc.appendChild(doc.createComment("Generated by python3.x, Author: Mengze."))
        osmNode = doc.createElement("osm")
        doc.appendChild(osmNode)
        ids = addNode(doc, osmNode, seg, i)
        addWay(doc, osmNode, ids, i)
        with open(name, 'w') as f:
            doc.writexml(f, addindent="    ", newl="\n", encoding="UTF-8")

        print('File <%s> saved!' % name)

        i += 10000


def addNode(doc, osmNode, seg, i):
    ids = []
    ii = i + 1  # 表示这段路上的点序号
    for point in seg:
        lon = '%.8f' % point[0]
        lat = '%.8f' % point[1]
        alt = '%d' % point[2]
        nodeID = '%d' % ii
        pointNode = doc.createElement("node")
        pointNode.setAttribute('id', nodeID)
        pointNode.setAttribute('lon', lon)
        pointNode.setAttribute('lat', lat)
        pointNode.setAttribute('alt', alt)
        osmNode.appendChild(pointNode)
        ids.append(ii)

        ii += 1

    return ids


def addWay(doc, osmNode, ids, i):
    wayNode = doc.createElement("way")
    wayNode.setAttribute('id', str(i))
    osmNode.appendChild(wayNode)

    for each in ids:
        ndtNode = doc.createElement("nd")
        ndtNode.setAttribute('ref', str(each))
        wayNode.appendChild(ndtNode)

    way_tagNode = doc.createElement("tag")
    way_tagNode.setAttribute('k', "name:en")
    way_tagNode.setAttribute('v', "double way")

    wayNode.appendChild(way_tagNode)


def writeTopologyRoad(sourcePath, targetPath):
    try:
        sj.main(sourcePath, targetPath)
    except:
        text = '请检查目录<%s>下的xml文件' % sourcePath
        tm.showinfo('提示', text)


if __name__ == "__main__":
    root = tk.Tk()
    root.title('Select Segment')
    # root.iconbitmap(r'full path name')
    App(root).pack(fill="both", expand=1)  # fill 控件的填充方向 expand 控件随着窗口的控件填充
    root.mainloop()
