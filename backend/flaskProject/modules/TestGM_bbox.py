import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path

class SVGDrawer:
    def __init__(self, filepath):
        # 初始化时载入数据
        self.filepath = filepath
        with open(filepath, "r", encoding='utf-8') as file:
            self.data = json.load(file)
        self.nodes = self.data["DiGraph"]["Nodes"]

    def draw_svg_elements(self):
        fig, ax = plt.subplots()
        for node_id, node_info in self.nodes.items():
            attributes = node_info["Attributes"]
            tag = attributes["tag"]
            bbox = np.array(attributes["attributes"]["bbox"])

            # print(node_id + ":") 
            # print(bbox)
            # print("_______________")
            tag = tag.split('_')[0]
            # print(tag)

            # 根据不同的标签绘制不同的形状
            if tag in ["rect"]:
                # 对于矩形、图像、文本和SVG标签，绘制矩形
                rect = patches.Rectangle(
                    (bbox[0][0], bbox[1][0]),
                    bbox[0][1] - bbox[0][0],
                    bbox[1][1] - bbox[1][0],
                    linewidth=1,
                    edgecolor="r",
                    facecolor="none",
                )
                ax.add_patch(rect)
            elif tag == "circle":
                # 绘制圆形
                circle = patches.Circle(
                    (bbox[2][0], bbox[2][1]),
                    radius=(bbox[0][1] - bbox[0][0])/2,
                    linewidth=1,
                    edgecolor="r",
                    facecolor="none",
                )
                ax.add_patch(circle)

            elif tag == "ellipse":
                # 绘制椭圆
                ellipse = patches.Ellipse(
                    (bbox[2][0], bbox[2][1]),
                    (bbox[0][1] - bbox[0][0]),
                    (bbox[1][1] - bbox[1][0]),
                    linewidth=1,
                    edgecolor="r",
                    facecolor="none",
                )
                ax.add_patch(ellipse)
            elif tag == "line":
                # 绘制线段
                line = plt.Line2D(
                    (bbox[0][0], bbox[0][1]),
                    (bbox[1][0], bbox[1][1]),
                    lw=1,
                    color="red",
                    axes=ax,
                )
                ax.add_line(line)
            elif tag in ["polygon", "polyline"]:
                # 绘制多边形或折线
                poly = patches.Polygon(
                    bbox, closed=(tag == "polygon"), fill=None, edgecolor="r"
                )
                ax.add_patch(poly)
                
            # elif tag == "path":
            #     # # Assuming 'd' is your path's d attribute from the JSON
            #     # d = attributes["attributes"]["d"]
            #     # print(bbox)
            #      # 绘制线段
            #     line = plt.Line2D(
            #         (bbox[0][0], bbox[1][0]),
            #         (bbox[0][1], bbox[1][1]),
            #         lw=1,
            #         color="red",
            #         axes=ax,
            #     )
            #     ax.add_line(line)
    

        ax.set_xlim([0, 800])
        ax.set_ylim([0, 800])  # 设置y轴范围，反转y轴
        plt.gca().invert_yaxis()  # 反转y轴，使得原点在左下角

        # 确保x轴和y轴的单位比例相同
        ax.set_aspect('equal')  
        plt.show()  # 显示图表
        
    def run(self):
        drawer = SVGDrawer(self.filepath)
        drawer.draw_svg_elements()
