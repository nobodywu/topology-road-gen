### Dependences
Env: Ubuntu 16.04, Python3.6.3

Dependences：
- [tkinter](https://wiki.python.org/moin/TkInter)
- [pykml](https://pythonhosted.org/pykml/installation.html) 
- [numpy](http://www.numpy.org/), 1.14.2
- [seaborn](https://seaborn.pydata.org/installing.html), 0.9.0
- [matplotlib](https://matplotlib.org/users/installing.html), 2.2.2
- [pyproj](https://jswhit.github.io/pyproj/)，1.9.5.1
- [networkx](https://networkx.github.io/), 2.2

Python standard lib: os, sys, time, subprocess, hashlib, shutil, re, webbrowser, xml

Ubuntu terminal:  
`$ sudo apt-get install wmctrl` 


**Note:** The GUI tool language is temporarily Chinese.

**Trouble shot:** when import pykml in python: 
- No module named 'urllib2'. Open file `.../python3.6/site-packages/pykml/parser.py` repalce line 8 with `from urllib.request import urlopen`
- Module factor. Last line should be `print(write_python_script_for_kml_document(doc))`.

### Usage

There is a video available on [Bilibili](https://www.bilibili.com/video/av42444813/) (a Chinese video web).

- Copy `Example` directory to **desktop**
- Run `main.py`
- Enter **Example** in the dialog. The workspace created by the GUI tool is on the desktop. If the workspace exists, it will open directly.

The interface includes a menu bar and canvas, and the menu bar contains options:
- File(文件)
    - Create/open workspace(创建/打开工作空间)
    - Open kml file(打开kml文件). The first time you click, the file selection dialog will pop up; if there is a kml file in the workspace, the kml file will be opened directly and all saved temporary sections in the `temp_seg` directory will be displayed.
    - Save segment selected(保存暂存路段). Save all temporary sections and generate a txt file with no intersections in the `temp_seg` directory.
- Edit(编辑)
    - Delete the road segment(删除路段). Delete the last temporary segment selected rather than in the `temp_seg` directory
    - Road network generate(生成路网)。Read the txt file with no intersection point in the `temp_seg` directory, and generate the xml file with the intersection point in the `seg` directory.
- View(视图)
    - Init view(重置视图)
    - Inspect road network(检查路网). Read the xml file of the road segment with the intersection point in the `seg` directory, and show the connection relationship with animation.


**Operation Tips**:
- Move. **Left mouse button**, dragging canvas
- Zoom in and out. **Middle mouse**, rolling
- Select a waypoint. **Left mouse button**, Right click
- Delete waypoints. **Escape** key
- Save selected road segments. **Enter** key
