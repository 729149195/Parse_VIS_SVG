import json
import xml.etree.ElementTree as ET

def add_svg_id(svg_file_path, json_file_path):
    # 加载和解析JSON文件
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    # 注册SVG命名空间
    ET.register_namespace("", "http://www.w3.org/2000/svg")

    # 解析SVG文件
    tree = ET.parse(svg_file_path)
    root = tree.getroot()

    # 获取JSON中的节点数据
    nodes_data = data['DiGraph']['Nodes']

    node_map = {tuple(int(n) for n in node_data["Attributes"]["layer"].split('_')[1:]): node_key
                for node_key, node_data in nodes_data.items() if node_data["Attributes"]["layer"].count("_") > 0}

    def find_element_by_index(element, index_list):
        if not index_list:
            return element

        current_index, *remaining_indices = index_list

        children = list(element)
        reversed_index = len(children) - 1 - current_index

        if 0 <= reversed_index < len(children):
            selected_child = children[reversed_index]
            return find_element_by_index(selected_child, remaining_indices)
        else:
            return None

    # 遍历node_map，为每个元素设置id
    for index_tuple, node_key in node_map.items():
        element = find_element_by_index(root, index_tuple)
        if element is not None:
            element_id = nodes_data[node_key]["Attributes"]["tag"]
            element.set('id', element_id)

    # 保存修改后的SVG文件，覆盖原文件
    tree.write(svg_file_path, xml_declaration=True)


