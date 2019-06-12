# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
import tkinter.font as tkFont
import tkinter.filedialog as tkFile
import os
import locale
import subprocess
import xml.etree.ElementTree as et
import lib.checkAttr as ca


class App(tk.Frame):
    '''
    App类Canvas中Object放大缩小的代码来自Stack Overflow的问题'Move and zoom a tk canvas with mouse'
    https://stackoverflow.com/questions/25787523/move-and-zoom-a-tk-canvas-with-mouse
    '''

    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.font = tkFont.Font(family="helvetica", size=12)

        # left
        self.frameL = tk.Frame(root)
        self.frameL.pack(side=tk.LEFT)

        self.button1 = tk.Button(self.frameL, text="输入路网", font=self.font,
                                 command=self.openDir,).pack()
        self.button2 = tk.Button(self.frameL, text="输入属性", font=self.font,
                                 command=self.openConfig).pack()
        self.button3 = tk.Button(self.frameL, text="输出路网", font=self.font,
                                 command=lambda: self.genRoadAttr(self.inputWsDir, self.config)).pack()
        self.button3 = tk.Button(self.frameL, text="退出程序", font=self.font,
                                 command=self.exit).pack()

        # right

        self.frameR = tk.Frame(root)
        self.frameR.pack(side=tk.RIGHT)

        self.tex = tk.Text(self.frameR, height=8, width=76, font=self.font)
        self.tex.pack(side=tk.RIGHT)

        self.info = '[INFO]\n路网输入为路网的工作空间文件夹，目录下必须包含seg文件夹和points.txt文件\n属性输入为config_attr.xml文件\n'
        self.tex.insert(tk.END, self.info)

        # adding a tag to a part of text specifying the indices
        self.tex.tag_add("p2.0", "2.8", "2.15")
        self.tex.tag_add("p2.1", "2.23", "2.26")
        self.tex.tag_add("p2.2", "2.30", "2.40")
        self.tex.tag_add("p3", "3.5", "3.20")
        self.tex.tag_config("p2.0", foreground="red")
        self.tex.tag_config("p2.1", foreground="red")
        self.tex.tag_config("p2.2", foreground="red")
        self.tex.tag_config("p3", foreground="red")

        self.info = '[TIP]\n1.请把工作空间中的points.txt文件导入Google Earth\n2.查找需要添加属性的路点或路段\n3.按照格式编写config_attr.xml文件\n'
        self.tex.insert(tk.END, self.info)

        # variables
        self.inputWsDir = ''
        self.config = ''

    def openDir(self):
        desktopPath = getSysDesktop()

        while True:
            inputWsDir = tkFile.askdirectory(initialdir=desktopPath, parent=root)

            if inputWsDir:
                self.inputWsDir = inputWsDir
                segDir = os.path.join(inputWsDir, 'seg')
                pointsFile = os.path.join(inputWsDir, 'points.txt')

                if os.path.isdir(segDir) and os.path.isfile(pointsFile):
                    break

            text = '[ERROR]\n%s不是工作空间，请重新选取\n' % self.inputWsDir
            self.tex.insert(tk.END, text)
            self.tex.see(tk.END)             # Scroll if necessary

        text = '[INPUT]\n输入文件夹：%s\n' % self.inputWsDir
        self.tex.insert(tk.END, text)
        self.tex.see(tk.END)

    def openConfig(self):
        desktopPath = getSysDesktop()

        while True:
            configFile = tkFile.askopenfilename(initialdir=desktopPath,
                                                filetypes=[("XML Files", ".xml"), ('All files', '*')])
            if configFile:
                self.config = configFile

                try:
                    tree = et.parse(self.config)
                    root = tree.getroot()
                except:
                    text = '[ERROR]\n%s不是有效的xml文件，请重新选取\n' % self.config
                    self.tex.insert(tk.END, text)
                    self.tex.see(tk.END)
                    continue

                if root.tag == 'attr':
                    break
                else:
                    text = '[ERROR]\n%s不是路网属性xml文件，请重新选取\n' % self.config
                    self.tex.insert(tk.END, text)
                    self.tex.see(tk.END)

        text = '[INPUT]\n属性配置文件：%s\n' % self.config
        self.tex.insert(tk.END, text)
        self.tex.see(tk.END)

    def genRoadAttr(self, inputWsDir, configFile):

        if inputWsDir and configFile:
            if self.validateConfig(configFile):
                outputDir = os.path.join(inputWsDir, 'seg_attr')
                ca.addAttr(inputWsDir, configFile)
                text = '[OUTPUT]\n属性添加成功\n输出文件夹为：%s\n' % outputDir
                self.tex.insert(tk.END, text)
                self.tex.see(tk.END)
        else:
            if not inputWsDir and not configFile:
                text = '[WARNING]\n请输入路网工作空间和属性xml文件\n'
                self.tex.insert(tk.END, text)
                self.tex.see(tk.END)
            elif not inputWsDir:
                text = '[WARNING]\n请输入路网工作空间\n'
                self.tex.insert(tk.END, text)
                self.tex.see(tk.END)
            else:
                text = '[WARNING]\n请输入属性xml文件\n'
                self.tex.insert(tk.END, text)
                self.tex.see(tk.END)

    def exit(self):
        root.destroy()

        # root.after(2000, root.destroy)

    def validateConfig(self, configFile):
        tree = et.parse(configFile)
        root = tree.getroot()

        state = True

        for sub in root:
            subType = []
            for each in sub:
                # node or seg, list.append can't add same element
                subType.append(each.tag)

            print(subType)

            if(len(set(subType)) == 1):
                text = '属性<%s>根据<%s>添加' % (sub.tag, subType[0])
                text = '[INFO]\n' + text + '\n'
                self.tex.insert(tk.END, text)
                self.tex.see(tk.END)
            else:
                text = '属性<%s>中不能同时包含<node>和<seg>，请修改属性配置xml文件' % sub.tag
                text = '[ERROR]\n' + text + '\n'
                self.tex.insert(tk.END, text)
                self.tex.see(tk.END)

                state = False
                break

        return state


def getSysDesktop():
    home = os.path.expanduser('~')
    language = locale.getdefaultlocale()[0]
    if language == 'en_US':
        print("system language is English, set desktop = \'Desktop\'")
        desktop = 'Desktop'

    elif language == 'zh_CN':
        print("system language is Chinese, set Desktop = \'桌面\'")
        desktop = '桌面'
    else:
        print("system language is neither Chinese nor English, set desktop = \'Desktop\'. This can result in error.")
        desktop = 'Desktop'

    desktopPath = os.path.join(home, desktop)

    return desktopPath


if __name__ == '__main__':
    root_win_name = '添加拓扑路网属性'

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
