超无项目中，受遥控终端性能的限制，不能加载太多路点显示在地图上。此脚本的目的即为生成稀疏路网。

### 使用步骤
- 确定需要输入的暂存路段文件夹
- 修改路径，打开`tools/genSparseRoadpoint.py`
    - `ws_dir_path = "/home/mengze/Desktop/changsha_May20"`，工作空间路径
    - `input_dir = os.path.join(ws_dir_path, "seg")`，拓扑路网路径
    - `output_dir = ws_dir_path + "_sparse"`，输出文件夹
- 在配置好的环境中运行`(py36)$ python genSparseRoadpoint.py`

生成的稀疏路点路网放在终端route文件夹下。

