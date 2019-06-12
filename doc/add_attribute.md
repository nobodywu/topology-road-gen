### 依赖和快速开始
请参考[拓扑路网生成工具](./generate_topology_road_zh.md)配置环境


- 将工作空间下的points.txt导入Google Earth，查看需要设置属性的路段和路点id号。例如路点id: 210004属于路段id: 210000。
- 启动GUI程序`(py36)$ python genRoad.py`

![](../figure/add_attr_startup.png)

### 属性配置文件
`example/config_attr.xml`文件的结构为
```
<?xml version="1.0" encoding="UTF-8"?>
<attr>
    <vel default="4.2">
        <seg value="2">20000,120000</seg>
        <seg value="5">30000,130000</seg>
    </vel>
    <smoke default="0">
        <node value="1">20002,130004</node>
    </smoke>
</attr>

```
- 每个xml文件只有唯一根节点，根节点`<attr>`代表了这是一个属性配置文件。
- 二级节点可以自行随意添加，示例文件中添加了两个`<vel>`和`<smoke>`。每个二级节点必须含有`default`值，代表除指定路段或路点外，按照default值添加。
- 三级节点为`<node>`或`<seg>`，数量不限，每个二级节点下只能全部为`<node>`或全部为`<seg>`不能混合指定。
- 三级节点的`value`值可以任意指定，将按照`text`指定的路段或路点进行属性添加。


<br>
<p align="right"> Auther: Wu Mengze<br>Date: Jun 12 2019</p>
