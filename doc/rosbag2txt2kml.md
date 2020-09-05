获取rostopic中的GPS信息，转化为KML文件，可用于：
- 在Google Earth上显示
- 在拓扑路网生成GUI程序中编辑拓扑路网

### 3.4.2 使用步骤
1. 获取rosbag中的GPS信息，以**/GPSmsg** 话题为例
    - 准备需要转换的rosbag，示例文件在`example/txt2kml` 文件夹下。
    - 转换为txt文件。在Ubuntu终端输入：`$ rostopic echo -b 2019-02-28-16-50-46.bag -p /GPSmsg > GPS_ori.txt # convert rosbag to txt`
    - 查看打开`GPS_ori.txt` 查看经纬海拔高度所在的列，为10-12，获取信息，在终端输入：`$ cut -f10,11,12 -d',' GPS_ori.txt > GPSmsg.txt # lat,lon,alt`

2. 转换为KML文件，在配置好的环境中运行`(py36)$ python txt2kml.py`
    - 在`fileName` 变量中更改`GPSmsg.txt` 文件的路径
    - 运行程序，在同目录下得到以当前时间命名的KML文件`Y-M-D-H-M-S.kml`。

**注意**：  
如果使用其他来源的txt文件，**请注意格式**。

