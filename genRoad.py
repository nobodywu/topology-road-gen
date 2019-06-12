# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import os
import tkinter as tk
import lib.selectSeg as ss

root_win_name = '创建拓扑路网'

print('\n######\n[Check Program Startup]')
cmd = 'wmctrl -lG | grep \'' + root_win_name + '\' | awk \'{print $1}\''
win_id = subprocess.check_output(["/bin/bash", "-c", cmd]).decode("utf-8")
win_id = win_id.split()
if len(win_id):
    print('Close former process, id: ', win_id)
    for each in win_id:
        cmd = 'wmctrl -ic ' + each
        os.system(cmd)
else:
    print('Env clean')

print('\n######\n[Program Startup]')
root = tk.Tk()
root.option_add('*Dialog.msg.font', 'Helvetica 12')
root.title(root_win_name)
# root.iconbitmap(r'full path name')
ss.App(root).pack(fill="both", expand=1)  # fill 控件的填充方向 expand 控件随着窗口的控件填充
root.mainloop()
