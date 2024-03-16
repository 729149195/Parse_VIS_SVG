
import json
from collections import Counter

class ColorCounter:
    """
    一个基类，用于从指定的 JSON 数据中计数 'fill' 和 'stroke' 属性的颜色值，并保存结果。
    """
    def __init__(self, attribute_name, input_path, output_path):
        self.attribute_name = attribute_name  # 指定要统计的属性名（fill 或 stroke）
        self.input_path = input_path  # 输入文件路径
        self.output_path = output_path  # 输出文件路径
        self.counter = Counter()  # 使用 Counter 来统计颜色值的出现次数

    def process_data(self):
        """
        处理数据：加载、计数、保存。
        """
        data = self._load_data()
        self._count_colors(data)
        self._save_counts()

    def _load_data(self):
        """
        从指定的文件路径加载 JSON 数据。
        """
        with open(self.input_path, 'r') as file:
            return json.load(file)

    def _count_colors(self, data):
        """
        统计颜色值的出现次数，忽略 None。
        """
        for item in data:
            color = item.get(self.attribute_name)
            if color is not None:  # 忽略 None 值
                self.counter[color] += 1

    def _save_counts(self):
        """
        将颜色计数保存到 JSON 文件。
        """
        with open(self.output_path, 'w') as file:
            json.dump(dict(self.counter), file, indent=4)

class FillColorCounter(ColorCounter):
    """
    用于统计 'fill' 颜色值的类。
    """
    def __init__(self):
        super().__init__('fill', 'extracted_node.json', './data/fill_num.json')

class StrokeColorCounter(ColorCounter):
    """
    用于统计 'stroke' 颜色值的类。
    """
    def __init__(self):
        super().__init__('stroke', 'extracted_node.json', './data/stroke_num.json')

# 现在可以通过简单地实例化类并调用 process_data 方法来完成整个流程
# 示例：
# fill_counter = FillColorCounter()
# fill_counter.process_data()
# stroke_counter = StrokeColorCounter()
# stroke_counter.process_data()
