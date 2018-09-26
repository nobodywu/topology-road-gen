# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# import pygame
# import sys
# import pygame.locals as cons
# import numpy as np
# from pathlib import Path  # Python 3.5+
#
# HOME = str(Path.home())
# FILE_NAME_POINTS = HOME + '/Desktop/selectSeg.txt'
# print(FILE_NAME_POINTS)
#
#
# points = np.loadtxt(FILE_NAME_POINTS)
# print(points)

import tkinter as tk
import random


class Example(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.canvas = tk.Canvas(self, width=400, height=400, background="bisque")  # bisque 红黄色
        self.xsb = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.ysb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.ysb.set, xscrollcommand=self.xsb.set)
        # A tuple (w, n, e, s) that defines over how large an area the canvas can be scrolled, where w is the left side, n the top, e the right side, and s the bottom.
        self.canvas.configure(scrollregion=(0, 0, 1000, 1000))

        self.xsb.grid(row=1, column=0, sticky="ew")
        self.ysb.grid(row=0, column=1, sticky="ns")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        # 第一行第一列分配全部空间
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Plot some rectangles
        for n in range(50):
            x0 = random.randint(0, 900)
            y0 = random.randint(50, 900)
            x1 = x0 + random.randint(50, 100)
            y1 = y0 + random.randint(50, 100)
            color = ("red", "orange", "yellow", "green", "blue")[random.randint(0, 4)]
            self.canvas.create_oval(x0, y0, x1, y1, outline="black",
                                    fill=color, activefill="black", tags=n)
        self.canvas.create_text(50, 10, anchor="nw",
                                text="Click and drag to move the canvas\nScroll to zoom.")

        # This is what enables using the mouse:
        self.canvas.bind("<ButtonPress-1>", self.move_start)
        self.canvas.bind("<B1-Motion>", self.move_move)
        # linux scroll
        self.canvas.bind("<Button-4>", self.zoomerP)
        self.canvas.bind("<Button-5>", self.zoomerM)

        # print mouse position
        self.canvas.bind("<Motion>", self.print_mouse_position)
        # select object
        self.canvas.bind("<Control-ButtonPress-1>", self.select_object)

    def print_mouse_position(self, event):
        # print(event.x, event.y)
        pass

    def select_object(self, event):
        item = self.canvas.find_closest(event.x, event.y)
        print(self.canvas.bbox(item))

    # move
    def move_start(self, event):
        self.canvas.scan_mark(event.x, event.y)
        self.canvas.focus_set()  # security, set the focus on the Canvas

    def move_move(self, event):

        self.canvas.scan_dragto(event.x, event.y, gain=1)

    # linux zoom
    def zoomerP(self, event):
        true_x = self.canvas.canvasx(event.x)
        true_y = self.canvas.canvasy(event.y)
        self.canvas.scale("all", true_x, true_y, 1.1, 1.1)

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def zoomerM(self, event):
        true_x = self.canvas.canvasx(event.x)
        true_y = self.canvas.canvasy(event.y)
        self.canvas.scale("all", true_x, true_y, 0.9, 0.9)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


if __name__ == "__main__":
    root = tk.Tk()
    Example(root).pack(fill="both", expand=1)  # fill 控件的填充方向 expand 控件随着窗口的控件填充
    root.mainloop()
