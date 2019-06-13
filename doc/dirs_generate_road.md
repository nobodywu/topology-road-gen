拓扑路网生成GUI工具使用工作空间中的temp_seg中的暂存路段进行拓扑路网创建。`tools/dirsRoadGen.py`的作用是从多个暂存路段的目录中读取咱村路段，生成拓扑路网。需要注意，注意不同暂存路段文件夹中相邻路段的端点是否在捕获距离范围内。

### 使用步骤
- 确定需要输入的暂存路段文件夹
- 修改路径，打开`tools/dirsRoadGen.py`
    - `desktop_ws = os.path.join(home, 'Desktop', 'seg_merge')`，注意中文路径
    - `input_dirs_temp_seg = ['/home/mengze/Desktop/temp_seg1', '/home/mengze/Desktop/temp_seg2']`，可输入目录数量不限
    - `output_seg = os.path.join(desktop_ws, 'output')`指定输出目录
- 在配置好的环境中运行`(py36)$ python genRoad.py`

### 检查路网
为了验证不同暂存路段文件夹中相邻路段的端点是否在捕获距离范围内，需要[检查拓扑路网](./show_link.md)。

### 添加属性
路网属性添加GUI工具路网输入需为工作空间目录，程序检查目录下是否有`seg`文件夹和`points.txt`文件来判断是否为工作空间。

为此脚本生成的路网添加属性步骤：
- 新建工作空间文件夹，名字可任意制定
- 将此脚本生成的路网文件件更名为`seg`，并拷贝进第一步建立的工作空间文件夹中
- 在第一步建立的工作空间文件夹中新建`points.txt`空文件
- 路网属性添加GUI工具`(py36)$ python genRoad.py`


<br>
<p align="right"> Auther: Wu Mengze<br>Date: Jun 13 2019</p>
