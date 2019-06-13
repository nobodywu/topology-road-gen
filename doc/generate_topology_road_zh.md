### 依赖
环境：Ubuntu 16.04, Python3.6

Python 第三方库：[tkinter](https://wiki.python.org/moin/TkInter)
, [pykml](https://pythonhosted.org/pykml/installation.html), [numpy](http://www.numpy.org/), [seaborn](https://seaborn.pydata.org/installing.html),, [matplotlib](https://matplotlib.org/users/installing.html), [pyproj](https://jswhit.github.io/pyproj/)

Pyhton 标准库：os, sys, time, subprocess, hashlib, shutil, re, webbrowser, xml等等

系统软件：[wmctrl](http://manpages.ubuntu.com/manpages/bionic/en/man1/wmctrl.1.html)  

### 快速开始
推荐使用conda管理Python库
- 安装系统软件 `$ sudo apt-get install wmctrl` 
- 使用conda，安装Python依赖
    - [下载](https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh) miniconda3(python3, x64)进行安装`$ bash Miniconda3-latest-Linux-x86_64.sh`。重新打开终端会在用户名前看到 **(base)**，说明此时在conda环境中
    - 创建一个新的conda环境，`(base)$conda create -n py36 python=3.6`。进入新的环境`(base)$ source activate py36`将会在用户名前面看到 **(py36)**。**不要** 在 **(base)** 中安装pykml，它会改变python环境，python3 --> python2
    - 在**py36**中安装依赖，`(py36)$ conda install -c conda-forge libiconv numpy tk pykml pyproj matplotlib seaborn`
    - 对pykml做一些改变:
        - 打开`~/miniconda3/envs/py36/lib/python3.6/site-packages/pykml/parser.py`第八行替换为`from urllib.request import urlopen`
        - 打开`~/miniconda3/envs/py36/lib/python3.6/site-packages/pykml/factor.py`最后一行应该为 `print(write_python_script_for_kml_document(doc))`.
    - 启动GUI程序`(py36)$ python genRoad.py`

Q: 如何解决conda与ROS冲突问题？  
A: 退出conda环境`(py36)$ conda deactivate`

Q: [如何在打开终端时不默认进入conda环境](https://stackoverflow.com/questions/54429210/how-do-i-prevent-conda-from-activating-the-base-environment-by-default)  
A: `$ conda config --set auto_activate_base false`. 重新打开终端将不会看到 **(base)**。进入conda环境`$ conda activate py36`，注意**不是 source**. 

### 使用说明
操作视频请见[链接](https://www.bilibili.com/video/av42444813)。

**添加路段到拓扑路网之前请保证kml文件包含了所有路径**。一个kml文件对应一个工作空间，如果想添加的路段在kml文件中不存在，则需要完善kml文件上的路径，打开新的工作空间，重新选择所有路段。或者[从多个文件夹中读取暂存路段创建新的路网](./dirs_generate_road.md)

1. 生成拓扑路网
    - 准备kml文件。[实车采集转换为kml文件](./rosbag2txt2kml.md)后在Google Earth修改或直接在Google Earth勾画需要的路线。[创建和编辑path教程](./creat_and_edit_path.md)。输出为kml文件，如示例文件`cahngsha_May20.kml`。如何Google Earth中处理路口处的路径请[参考这里](./draw_intersection.md)
    - 运行`(py36)$ python genRoad.py`，打开主界面，输入工作空间名称，创建的工作空间位于**桌面**，程序自动判断中英文路径
    - 点击菜单栏**文件** --> **打开kml文件**，选择第一步准备的kml文件。
    - 利用鼠标右键按顺序点击完成路段的选择，按回车键暂存选择的路段，端点提示范围框为8m，建议路段中点间距为5-20m。
    - 点击**文件** --> **保存暂存路段**，完成暂存路段的保存，生成的文件位于工作空间下的`temp_seg`目录，每次保存不覆盖之前的文件。
    - 点击**编辑** --> **生成路网**，工作空间`seg`目录下生成拓扑路网xml文件。每次点击此按钮会清空之前`seg`目录下的所有文件。
2. 修改路网步骤
    - 确定**路段id**。打开Google Earth导入`points.txt`文件查看。
    - 确定需要增加或删除的路网是否**打断** 或**连接** 附近路段。增加路段，其端点可能使一个路段变为两个路段。删除段落，其端点可能使附近两个路段合并为一个路段。**增加路段时要保证kml文件中存在该路段的路径**，否则修改kml文件后需要重新创建工作空间，重新选择路段。
        - 如果不影响附近路段
            - 删除路段。删除`temp_seg`对应路段id
            - 增加路段。选择新的暂存路段并保存暂存路段到`temp_seg`中
        - 如果影响附近路段，删除`temp_seg`中所有影响到的路段。重新选择要需要修改的路段。

**重要说明**：
- 可暂存多个路段后再点击**文件** --> **保存暂存路段**，此选项可多次使用
- 如果有已暂存的路段，会显示虚线圆构成的端点范围提示框，界面中已选择路段端点范围提示框为8m。选择下一个相邻路段时，端点应在范围提示框内，两个端点**不能** 在同一范围提示框内。程序使用捕获距离判断连接关系，在选点时不需要重复指定路段连接点，但应尽量靠近。
- 程序读取kml文件中的`<placemark>`标签，即为Google Earth中绘制的路径（path），**不能处理点**。
- **请在kml文件中标出所有路径再开始路段选取工作**，增加路段时要保证kml文件中存在该路段的路径，否则修改kml文件后需要重新创建工作空间，重新选择路段。
- 路网中所有路段均默认为双向路。

### 界面介绍
运行`./src/main.py`，打开**拓扑路网生成GUI** 。在创建/打开工作空间对话框中输入工作空间名称，用鼠标单击**创建/打开**按钮，完成创建/打开工作空间操作，位于**桌面**。如果工作空间已存在kml文件，将打开**存在的kml文件**。工作空间和kml文件一一对应，如果需要重新选择kml文件，请**重新建立**工作空间。

![](../figure/road_gen_small.png)

界面包括菜单栏和画布，菜单栏中包含选项：
- **文件**
    - **创建/打开工作空间**
    - **打开kml文件**。首次点击时，将弹出文件选择对话框；如果工作空间存在kml文件，将直接打开此kml文件，并显示`temp_seg`目录中所有已保存的暂存路段
    - **保存暂存路段**。保存所有暂存路段，在`temp_seg`目录下生成没有路口点的txt文件
- **编辑**
    - **删除路段**。删除上一个暂存路段，不会删除`temp_seg`目录中所有已保存的暂存路段
    - **生成路网**。读取`temp_seg`目录下生成没有路口点的txt文件，在`seg`目录下生成带有路口点的路段xml文件
- **视图**
    - **重置视图**。重置默认位置和比例
    - **检查路网**。运行路段连接关系检查程序，读取`seg`目录下带有路口点的路段xml文件，用动画展示连接关系。
- 帮助（未完善）
    - 操作提示
    - 关于

**操作提示**  
通过鼠标和键盘与界面进行交互：
- 移动。鼠标左键拖拽画布
- 放大缩小。滚动鼠标滑轮
- 选择路点。单击右键
- 删除路点。Escape键
- 暂存路段，保存选择好的路段。Enter键


<br>
<p align="right"> Auther: Wu Mengze<br>Date: Jun 12 2019</p>
