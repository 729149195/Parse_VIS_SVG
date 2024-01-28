import os
import json
import networkx as nx
import community as community_louvain
import matplotlib.pyplot as plt
import matplotlib


class CommunityDetector:
    def __init__(self, json_file):
        self.json_file = json_file
        self.filtered_json_file = self._create_filtered_filename(json_file)
        self.graph = None
        self.partition = None

    def _create_filtered_filename(self, original_file):
        dirname, filename = os.path.split(original_file)
        filtered_filename = f"filtered_{filename}"
        return os.path.join(dirname, filtered_filename)

    def filter_visible_nodes_and_edges(self):
        with open(self.json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        visible_nodes = {node for node, attributes in data["DiGraph"]["Nodes"].items() if attributes["Attributes"]["visible"]}
        filtered_edges = [edge for edge in data["DiGraph"]["Edges"] if edge[0] in visible_nodes and edge[1] in visible_nodes]

        new_data = {
            "DiGraph": {
                "Nodes": {node: data["DiGraph"]["Nodes"][node] for node in visible_nodes},
                "Edges": filtered_edges
            }
        }

        with open(self.filtered_json_file, 'w', encoding='utf-8') as file:
            json.dump(new_data, file, indent=4)

    def execute(self):
        self.filter_visible_nodes_and_edges()

        with open(self.filtered_json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        self.graph = nx.DiGraph()
        for node_path, node_data in data["DiGraph"]["Nodes"].items():
            self.graph.add_node(node_path, **node_data)

        for edge in data["DiGraph"]["Edges"]:
            source, target, _ = edge
            self.graph.add_edge(source, target)

        self.partition = community_louvain.best_partition(self.graph.to_undirected())
        self._visualize()

    def _visualize(self):
        plt.figure(figsize=(10, 10))
        pos = nx.spring_layout(self.graph)
        cmap = plt.cm.get_cmap('viridis', max(self.partition.values()) + 1)
        nx.draw_networkx_nodes(self.graph, pos, node_size=40, cmap=cmap, node_color=list(self.partition.values()))
        nx.draw_networkx_edges(self.graph, pos, alpha=0.5)
        plt.show()


# 使用方法
detector = CommunityDetector("../GMoutput/GMinfo.json")
detector.execute()
