# Parse_VIS_SVG

```
各个模块介绍：
    CreateGM: 从原始SVG提取基本数据并做第一步格式处理与部分数据运算（如提取初始bbox及将transfrom应用于提取出的bbox上）
    Add_id: 根据layer为每个元素添加唯一id
    Convert_tiHex: 把原数据的所有色值都转为16进制
    TestGM: 用以测试提取的出bbox边界框是否准确
    Gestalt_Edges_Features: 从基本数据中提取两可视节点间的格式塔特征矩阵
    Neural_Network_Weight: 通过深度神经网络学习到三层权重
    Community_Detection: 用三层权重实现多重社区检测
    Quantification_Basis: 根据各个社区的内部结构和外部结构来推断其被人感知到的顺序
    Statitication: 用以将所有所需数据调整为前端D3可直接调用的数据结构
```

```
各个json文件的用途：
GMinfo.json: CreateGM从原始数据中提取并初步处理的元素网络
extracted_nodes.json: 从初步网络中提取并二次处理出的可视节点中提取出的节点基本信息
similarity_graph.json: 根据二次提取出的节点基本信息来张开节点之间的格式塔特征矩阵
community_data.json: 用于存储社区检测结果，用于返回前端进行社区节点凸包渲染
attr_num.json: 用以统计节点的属性数据（未完成）
ele_num.json: 用以统计元素的种类和数量
group_data: 用以展示每个社区的内链接强度和外连接强度（未完成）
```

```
BBOX的格式：
    rect: bbox = [[x, y], [x + width, y + height], [x + width / 2, y + height / 2]]
    circle: bbox = [[cx - r, cy - r], [cx + r, cy + r], [cx, cy]]
    line: bbox = [[x1, y1], [x2, y2], [(x1 + x2) / 2, (y1 + y2) / 2]]
    ellipse: bbox = [[cx - rx, cy - ry], [cx + rx, cy + ry], [cx, cy]]
    polygon\polyline: bbox = [[x1, y1], [x2, y2]...points中的所有点]
    text\image: bbox = [[x, y], [x + width, y + height], [x + width/2, y + height/2]]
    path: 通过Pcode和Pnum来拟合成line集， 如[line1, line2, line3....]
```