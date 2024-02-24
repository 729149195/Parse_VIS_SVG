import json
import numpy as np

class NodeExtractor:
    def extract_nodes_info(self, input_file, output_file):
        with open(input_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        nodes = data['DiGraph']['Nodes']
        extracted_nodes = {}

        for node, attributes in nodes.items():
            tag = attributes['Attributes']['tag']
            attrs = attributes['Attributes']['attributes']
            level = attributes['Attributes']['level']
            layer = attributes['Attributes']['layer']

            # 初始化提取的属性字典
            extracted_attrs = {
                'tag': tag,
                'bbox': attrs.get('bbox', None),
                'stroke': attrs.get('stroke', None),
                'fill': attrs.get('fill', None),
                'level': level,
                'layer': layer
            }

            # 特殊处理对于"tag"为"path"的节点
            if tag == "path":
                extracted_attrs['Pcode'] = attrs.get('Pcode', [])
                extracted_attrs['Pnums'] = attrs.get('Pnums', [])

            extracted_nodes[node] = extracted_attrs

        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(extracted_nodes, file, indent=4)


class SimilarityGraphBuilder:
    def __init__(self, input_file, threshold):
        self.input_file = input_file
        self.threshold = threshold
        self.nodes = self.load_nodes()

    def load_nodes(self):
        with open(self.input_file, 'r') as file:
            data = json.load(file)
        return data

    def hex_to_rgb(self, hex_color):
        # 如果颜色值为None或不是有效的十六进制颜色字符串，则返回None或默认RGB值
        if hex_color is None or not hex_color.startswith('#') or len(hex_color) != 7:
            return None  # 或者返回一个默认的RGB值，例如(0, 0, 0)或其他

        # 尝试转换十六进制颜色值为RGB
        try:
            return tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
        except ValueError:
            # 如果转换失败（例如，因为颜色值包含非十六进制字符），则返回None或默认RGB值
            return None  # 或者返回一个默认的RGB值，例如(0, 0, 0)或其他

    def color_similarity(self, color1, color2):
        rgb1 = self.hex_to_rgb(color1)
        rgb2 = self.hex_to_rgb(color2)
        if rgb1 is None or rgb2 is None:  # 如果任一颜色为None
            return 0  # 返回一个默认的相似性分数，或根据需要进行调整
        diff = np.linalg.norm(np.array(rgb1) - np.array(rgb2))
        similarity = 1 / (1 + diff)  # 使用倒数转换得到相似性分数
        return similarity

    def calculate_color_similarity(self, node1, node2):
        stroke_similarity = self.color_similarity(node1.get('stroke'), node2.get('stroke'))
        fill_similarity = self.color_similarity(node1.get('fill'), node2.get('fill'))

        # 计算平均相似性得分
        return (stroke_similarity + fill_similarity) / 2

    def bbox_similarity(self, bbox1, bbox2):
        # 此处简化处理，您可能需要根据bbox的具体结构实现几何相似性的计算
        return 1  # 默认返回最高相似性

    def calculate_similarity(self, node1, node2):
        # 提取'_'之前的字符串用于比较tag
        tag1 = node1['tag'].split('_')[0]
        tag2 = node2['tag'].split('_')[0]
        tag_similarity = 1 if tag1 == tag2 else 0

        # 计算颜色相似性
        stroke_sim = self.color_similarity(node1.get('stroke', '#000'), node2.get('stroke', '#000'))
        fill_sim = self.color_similarity(node1.get('fill', '#FFF'), node2.get('fill', '#FFF'))

        # 假设已经有一个方法来计算bbox的接近性
        bbox_sim = self.bbox_similarity(node1.get('bbox'), node2.get('bbox'))

        weight = tag_similarity + bbox_sim + fill_sim + stroke_sim - 1

        # 返回包含所有相似性度量的字典
        # return {
        #     'tag_similarity': tag_similarity,
        #     'bbox_similarity': bbox_sim,
        #     'fill_similarity': fill_sim,
        #     'stroke_similarity': stroke_sim
        # }
        return {
            'weight': weight
        }

    def build_graph(self):
        graph = {}
        for node_id, node_attrs in self.nodes.items():
            for other_node_id, other_node_attrs in self.nodes.items():
                if node_id != other_node_id:
                    similarity_data = self.calculate_similarity(node_attrs, other_node_attrs)
                    # 计算相似性度量的平均值作为总相似性得分
                    average_similarity = np.mean(list(similarity_data.values()))
                    if average_similarity > self.threshold:  # 使用平均相似性得分与阈值比较
                        if node_id not in graph:
                            graph[node_id] = []
                        graph[node_id].append((other_node_id, similarity_data))
        return graph

    def print_graph(self):
        graph = self.build_graph()
        for node, edges in graph.items():
            print(f"Node {node} has edges:")
            for edge in edges:
                print(f"  to {edge[0]} with similarity {edge[1]}")

    def save_graph_to_json(self, output_json_path):
        graph = self.build_graph()
        edges_list = []

        # 构建图数据，包含具体的相似性数值
        for node, edges in graph.items():
            for edge in edges:
                similarity_data = edge[1]  # 获取相似性度量字典
                edge_data = [node, edge[0], similarity_data]  # 包含相似性数值的边信息
                edges_list.append(edge_data)

        # 准备要写入JSON文件的数据
        graph_data = {"Gestalt_Edges": edges_list}

        # 写入JSON文件
        with open(output_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(graph_data, json_file, indent=4)

        print(f"Graph data saved to {output_json_path}")


class EdgesUpdater:
    def __init__(self, gm_info_file, new_edges_file):
        self.gm_info_file = gm_info_file
        self.new_edges_file = new_edges_file

    def update_edges(self):
        # 加载原始图信息
        with open(self.gm_info_file, 'r', encoding='utf-8') as file:
            gm_info = json.load(file)

        # 加载包含新建边信息的JSON文件
        with open(self.new_edges_file, 'r', encoding='utf-8') as file:
            new_edges_info = json.load(file)

        # 获取新建边信息
        new_edges = new_edges_info['Gestalt_Edges']

        # 将新建的边添加到原始图信息的Edges数组中
        gm_info['DiGraph']['Edges'].extend(new_edges)

        # 更新边的数量
        gm_info['DiGraph']['edges'] = len(gm_info['DiGraph']['Edges'])

        # 将更新后的图信息保存回同一个GMinfo.json文件
        with open(self.gm_info_file, 'w') as file:
            json.dump(gm_info, file, indent=4)

        print(f"Updated {self.gm_info_file} with {len(new_edges)} new edges.")


def update_graph_with_similarity_edges():

    input_file = './GMoutput/GMinfo.json'
    output_nodes_file = './GMoutput/extracted_nodes.json'
    output_graph_file = './GMoutput/similarity_graph.json'
    similarity_threshold = 0.1
    gm_info_file = './GMoutput/GMinfo.json'
    new_edges_file = './GMoutput/similarity_graph.json'
    # 提取节点信息
    extractor = NodeExtractor()
    extractor.extract_nodes_info(input_file, output_nodes_file)
    print(f"Extracted nodes information saved to {output_nodes_file}")

    # 构建相似性图并保存到JSON文件
    graph_builder = SimilarityGraphBuilder(output_nodes_file, similarity_threshold)
    graph_builder.save_graph_to_json(output_graph_file)

    # 更新GMinfo.json文件中的边信息
    updater = EdgesUpdater(gm_info_file, new_edges_file)
    updater.update_edges()
