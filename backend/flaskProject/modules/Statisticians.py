import json
import re

class TagCounter:
    def __init__(self):
        # 将文件路径固定
        self.input_file_path = './GMoutput/GMinfo.json'
        self.output_file_path = './data/ele_num.json'

    def process(self):
        # 调用内部方法来统计tag数量
        result_json = self._count_tags_from_json()
        # 写入结果到文件
        self._write_result_to_file(result_json)

    def _count_tags_from_json(self):
        with open(self.input_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        nodes = data['DiGraph']['Nodes']
        tag_counts = {}
        for node in nodes.values():
            tag_full = node['Attributes']['tag']
            visible = node['Attributes']['visible']
            tag = re.sub(r'_[0-9]+$', '', tag_full)
            if tag not in tag_counts:
                tag_counts[tag] = {"num": 1, "visible": visible}
            else:
                # 如果tag已存在，只需增加计数
                tag_counts[tag]["num"] += 1

        # 构造最终的JSON格式
        result_json = [{"tag": tag, "num": info["num"], "visible": info["visible"]} for tag, info in tag_counts.items()]

        return result_json

    def _write_result_to_file(self, result_json):
        with open(self.output_file_path, 'w', encoding='utf-8') as file:
            json.dump(result_json, file, indent=4, ensure_ascii=False)

# 使用示例
if __name__ == "__main__":
    tag_counter = TagCounter()
    tag_counter.process()
    print(f"Results have been written to {tag_counter.output_file_path}")
