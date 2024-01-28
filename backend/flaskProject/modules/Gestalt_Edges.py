import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches


class SVGDrawer:
    def __init__(self, filepath):
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

            tag = tag.split('_')[0]

            # 根据不同的标签绘制不同的形状
            if tag in ["rect"]:
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
                circle = patches.Circle(
                    (bbox[2][0], bbox[2][1]),
                    radius=(bbox[0][1] - bbox[0][0])/2,
                    linewidth=1,
                    edgecolor="r",
                    facecolor="none",
                )
                ax.add_patch(circle)
            elif tag == "ellipse":
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
                line = plt.Line2D(
                    (bbox[0][0], bbox[0][1]),
                    (bbox[1][0], bbox[1][1]),
                    lw=1,
                    color="red",
                    axes=ax,
                )
                ax.add_line(line)
            elif tag in ["polygon", "polyline"]:
                poly = patches.Polygon(
                    bbox, closed=(tag == "polygon"), fill=None, edgecolor="r"
                )
                ax.add_patch(poly)

        ax.set_xlim([0, 700])
        ax.set_ylim([0, 700])
        plt.gca().invert_yaxis()  # 反转y轴，使得原点在左下角
        ax.set_aspect('equal')  # 确保x轴和y轴的单位比例相同

        # 保存图表为图像文件而不是显示
        plt.savefig("./static/GMinfo.png", dpi=300)  # 指定保存路径和文件名
        plt.close(fig)  # 关闭图表，防止内存泄漏

    def run(self):
        self.draw_svg_elements()




