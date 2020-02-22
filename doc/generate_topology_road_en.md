### Dependences
Env: Ubuntu 16.04, Python3.6

Python third part libs: [tkinter](https://wiki.python.org/moin/TkInter)
, [pykml](https://pythonhosted.org/pykml/installation.html), [numpy](http://www.numpy.org/), [seaborn](https://seaborn.pydata.org/installing.html),, [matplotlib](https://matplotlib.org/users/installing.html), [pyproj](https://jswhit.github.io/pyproj/)， [networkx](https://networkx.github.io/)

Python standard libs: os, sys, time, subprocess, hashlib, shutil, re, webbrowser, xml, etc...

System dependence: [wmctrl](http://manpages.ubuntu.com/manpages/bionic/en/man1/wmctrl.1.html)  

### Quick Start
We use conda manage python libraries.
- Install system dependence, `$ sudo apt-get install wmctrl` 
- Install Python dependences, using conda
    - [Download](https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh) miniconda3(python3, x64) and install,`$ bash Miniconda3-latest-Linux-x86_64.sh`. Re-open terminal, you will see **(base)** before username.
    - Creat a new environment,`(base)$conda create -n py36 python=3.6`. Enter new environment, `(base)$ source activate py36`, now you will see **(py36)** before username. **Do not** install pykml in **(base)**, it will change python3 --> python2
    - Install python dependences, `(py36)$ conda install -c conda-forge libiconv numpy tk pykml pyproj matplotlib seaborn`
    - Install python dependences for path planning, `(py36)$ conda install -c anaconda networkx`
    - Do small surgery, because pykml only support python2:
        - File `~/miniconda3/envs/py36/lib/python3.6/site-packages/pykml/parser.py`, repalce line 8 with `from urllib.request import urlopen`
        - File `~/miniconda3/envs/py36/lib/python3.6/site-packages/pykml/factor.py`, the last line should be `print(write_python_script_for_kml_document(doc))`.
    - Launch GUI, `(py36)$ python genRoad.py`

Q: How to deactivate conda?  
A: `(py36)$ conda deactivate`

Q: [How do I prevent Conda from activating the base environment by default?](https://stackoverflow.com/questions/54429210/how-do-i-prevent-conda-from-activating-the-base-environment-by-default)  
A: `$ conda config --set auto_activate_base false`.  Re-open terminal, you won't see **(base)** before username. Use `$ conda activate py36` enter conda environment, **not source**. 

### Usage

There is a video available on [Bilibili](https://www.bilibili.com/video/av42444813/) (a Chinese video web).

- Copy `example/changsha_May22` directory to **Desktop**. This folder is an workspace, each workspace identify only one KML file.
- Run `(py36)$ python genRoad.py`
- Enter **changsha_May22** in the dialog. The workspace created by the GUI tool is on the desktop.

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
    - Shortest Path(最短路径). Get the shortest path by specifying the start and end points with the mouse left click.

**Operation Tips**:
- Move. **Left mouse button**, dragging canvas
- Zoom in and out. **Middle mouse**, rolling
- Select a waypoint. **Right mouse button**, Right click
- Delete waypoints. **Escape** key
- Save selected road segments. **Enter** key

<br>
<p align="right"> Auther: Wu Mengze<br>Date: Feb 22 2020</p>
