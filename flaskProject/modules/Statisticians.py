import json
import re
from collections import Counter


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
            if tag == 'svg':  # 跳过 svg 标签
                continue
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
        # result_json = self._count_groups()
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


class ColorCounter:
    def __init__(self, attribute_name, input_path, output_path):
        self.attribute_name = attribute_name  # 指定要统计的属性名（fill 或 stroke）
        self.input_path = input_path  # 输入文件路径
        self.output_path = output_path  # 输出文件路径
        self.counter = Counter()  # 使用 Counter 来统计颜色值的出现次数

    def process_data(self):
        data = self._load_data()
        self._count_colors(data)
        self._save_counts()

    def _load_data(self):
        with open(self.input_path, 'r') as file:
            return json.load(file)

    def _count_colors(self, data):
        for tag, attributes in data.items():  # 假设 data 是一个字典
            if not isinstance(attributes, dict):
                continue  # 如果 attributes 不是字典类型，跳过此项

            color = attributes.get(self.attribute_name)  # 从 attributes 中获取感兴趣的颜色值
            if color is None or color.lower() in ["transparent", "none"]:  # 忽略 None 和 "none"
                continue

            self.counter[color] += 1

    def _save_counts(self):
        with open(self.output_path, 'w') as file:
            json.dump(dict(self.counter), file, indent=4)


class FillColorCounter(ColorCounter):
    def __init__(self):
        super().__init__('fill', './GMoutput/extracted_nodes.json', './data/fill_num.json')


class StrokeColorCounter(ColorCounter):
    def __init__(self):
        super().__init__('stroke', './GMoutput/extracted_nodes.json', './data/stroke_num.json')


# fill_counter = FillColorCounter()
# fill_counter.process_data()
# stroke_counter = StrokeColorCounter()
# stroke_counter.process_data()

class LayerDataExtractor:
    def __init__(self, input_path, output_path):
        self.input_path = input_path  # Input file path
        self.output_path = output_path  # Output file path

    def process(self):
        data = self._load_data()
        layer_data = self._extract_layers(data)
        # Creating a single top-level object instead of wrapping the array in an object
        structured_data = self._create_single_top_level_object(layer_data)
        self._save_data(structured_data)

    def _load_data(self):
        # Load JSON file
        with open(self.input_path, 'r') as file:
            return json.load(file)

    def _extract_layers(self, data):
        # Extract layer data for each node
        layer_data = []
        for node_id, node_data in data.items():
            if 'layer' in node_data:
                layer_info = {
                    'id': node_id,
                    'layer': node_data['layer']
                }
                layer_data.append(layer_info)
        return layer_data

    def _create_single_top_level_object(self, data):
        # Create a single top-level object with a "name" and "children" structure
        structure = {"name": "flare", "children": []}  # Assuming top-level name is "flare"
        current_level = structure["children"]

        for item in data:
            layers = item["layer"]
            if not layers:  # If no layer info, add node directly under "flare"
                current_level.append({"name": item["id"], "value": 1})
                continue

            current_level = structure["children"]
            for layer in layers[:-1]:  # Iterate to the second last element
                found = False
                for child in current_level:
                    if child.get("name") == layer:
                        current_level = child.get("children", [])
                        found = True
                        break
                if not found:
                    new_node = {"name": layer, "children": []}
                    current_level.append(new_node)
                    current_level = new_node["children"]

            # Handle the last element, add as a node with "value"
            current_level.append({"name": item["id"], "value": 1})

        return structure

    def _save_data(self, structured_data):
        # Save the structured data to a new JSON file
        with open(self.output_path, 'w') as file:
            json.dump(structured_data, file, indent=4)


# 示例使用（请在实际使用时取消注释）
# extractor = LayerDataExtractor('./GMoutput/extracted_nodes.json', './data/layer_data.json')
# extractor.process()

