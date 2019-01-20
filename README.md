此版本为生成拓扑关系路网的GUI界面，供全局路径规划程序使用。
## 1 程序
### 1.1 程序文件
在`src`目录下包含一个`package: topologicalRoadGen`，一个主程序`main.py`。package中包含三个模块，其功能分别是：
- `selectSeg.py` 程序界面类
- `setJunctions.py` 自动判断路口点
- `showLink.py` 拓扑路网检查模块

### 1.2 依赖
环境为python3.x。需要安装的依赖：
- [tkinter](https://wiki.python.org/moin/TkInter)，制作界面
- [pykml](https://pythonhosted.org/pykml/installation.html) ，导入时的问题详⻅[我的博客](https://blog.csdn.net/NobodyWu/article/details/81168584)
- [numpy](http://www.numpy.org/)，处理数据
- [seaborn](https://seaborn.pydata.org/installing.html)，设置画图风格
- [matplotlib](https://matplotlib.org/users/installing.html)，用于画图
- [pyproj](https://jswhit.github.io/pyproj/)，投影转换

python标准库，不需要安装的依赖：
- os 
- sys
- time
- subprocess
- hashlib
- shutil
- re
- webbrowser
- xml

## 2 使用说明
### 2.1 示例文件
示例文件在`example`目录下，`Example.kml`为从Googe Earth Pro中获取的文件，为程序的输入，`Example`目录为工作空间，是程序的输出，包含：
- `seg` 目录，生成的拓扑路网，里边包含带有路口点的路段xml文件
- `temp_seg` 目录，已保存的暂存路段，里边包含不带路口店的txt文件
- `config.txt` 保存了工作空间信息
- `Example.kml` 工作空间唯一对应一个kml文件

### 2.2 界面操作
运行`main.py`，打开**创建拓扑路网** GUI。在创建/打开工作空间对话框中输入工作空间名称，用鼠标单击**创建/打开**按钮，完成创建/打开工作空间操作。

界面包括菜单栏和画布，菜单栏中包含选项：
- 文件
    - 创建/打开工作空间
    - 打开kml文件。首次点击时，将弹出文件选择对话框；如果工作空间存在kml文件，将直接打开此kml文件，并显示`temp_seg`目录中所有已保存的暂存路段
    - 保存暂存路段。保存所有暂存路段，在`temp_seg`目录下生成没有路口点的txt文件
- 编辑
    - 删除路段。删除上一个暂存路段，不会删除`temp_seg`目录中所有已保存的暂存路段
    - 生成路网。读取`temp_seg`目录下生成没有路口点的txt文件，在`seg`目录下生成带有路口点的路段xml文件
- 视图
    - 重置视图。重置默认位置和比例
    - 检查路网。运行路段连接关系检查程序，读取`seg`目录下带有路口点的路段xml文件，用动画展示连接关系。
- 帮助
    - 操作提示
    - 关于

**操作提示**：
- 移动。鼠标左键拖拽画布
- 放大缩小。滚动鼠标中间
- 选择路点。单击右键
- 删除路点。Escape键
- 暂存路段，保存选择好的路段。Enter键

**注意**：
如果有已暂存的路段，会显示虚线圆构成的端点范围提示框，选择下一个相邻路段时，端点应在范围提示框内，两个端点不能在同一范围提示框内。

## 3 未完成
- 在界面中加入添加路点属性的功能
- 添加更改范围提示框范围功能
