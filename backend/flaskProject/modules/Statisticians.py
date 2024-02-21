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
# if __name__ == "__main__":
#     tag_counter = TagCounter()
#     tag_counter.process()
#     print(f"Results have been written to {tag_counter.output_file_path}")


class AttributeCounter:
    def __init__(self):
        self.input_file_path = './GMoutput/GMinfo.json'
        self.output_file_path = './data/attr_num.json'

    def process(self):
        result_json = self._count_attributes_from_json()
        self._write_result_to_file(result_json)

    def _count_attributes_from_json(self):
        with open(self.input_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        nodes = data['DiGraph']['Nodes']
        attribute_counts = {}
        excluded_attributes = {'bbox', 'd', 'Pcode', 'Pnums'}
        for node in nodes.values():
            attributes = node['Attributes']['attributes']
            for attr in attributes:
                if attr not in excluded_attributes:
                    if attr not in attribute_counts:
                        attribute_counts[attr] = 1
                    else:
                        attribute_counts[attr] += 1

        result_json = [{"attribute": attr, "num": count} for attr, count in attribute_counts.items()]
        return result_json

    def _write_result_to_file(self, result_json):
        with open(self.output_file_path, 'w', encoding='utf-8') as file:
            json.dump(result_json, file, indent=4, ensure_ascii=False)


# if __name__ == '__main__':
# counter = AttributeCounter()
# counter.process()


class BBoxCounter:
    def __init__(self):
        self.input_file_path = './GMoutput/GMinfo.json'
        self.output_file_path = './data/bbox_points_count.json'

    def process(self):
        result_json = self._count_bbox_points()
        self._write_result_to_file(result_json)

    def _count_bbox_points(self):
        with open(self.input_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        nodes = data['DiGraph']['Nodes']
        points_count = {}
        for node in nodes.values():
            bbox = node['Attributes']['attributes']['bbox']
            for point in bbox:
                point_tuple = tuple(point)  # 将点列表转换为元组
                if point_tuple not in points_count:
                    points_count[point_tuple] = 1
                else:
                    points_count[point_tuple] += 1

        result_json = [{"point": list(point), "count": count} for point, count in points_count.items()]  # 将元组转换回列表
        return result_json

    def _write_result_to_file(self, result_json):
        with open(self.output_file_path, 'w', encoding='utf-8') as file:
            json.dump(result_json, file, indent=4, ensure_ascii=False)


# counter = BBoxCounter()
# counter.process()


class GroupCounter:
    def __init__(self):
        self.input_file_path = './data/community_data.json'
        self.output_file_path = './data/group_data.json'

    def process(self):
        result_json = self._count_groups()
        self._write_result_to_file(result_json)

    def _count_groups(self):
        with open(self.input_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        nodes = data['nodes']
        group_counts = {}
        for node in nodes:
            group = node['group']
            if group not in group_counts:
                group_counts[group] = 1
            else:
                group_counts[group] += 1

        result_json = [{"group": group, "num": count} for group, count in group_counts.items()]
        return result_json

    def _write_result_to_file(self, result_json):
        with open(self.output_file_path, 'w', encoding='utf-8') as file:
            json.dump(result_json, file, indent=4, ensure_ascii=False)


# 使用示例
# counter = GroupCounter()
# counter.process()