import os
import json
import networkx as nx
import community as community_louvain


class CommunityDetector:
    def __init__(self, json_file):
        self.json_file = json_file
        self.graph = None
        self.partition = None

    def execute(self):
        with open(self.json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        self.graph = nx.DiGraph()
        for node_path, node_data in data["DiGraph"]["Nodes"].items():
            if node_data["Attributes"]["visible"]:
                self.graph.add_node(node_path, **node_data)

        for edge in data["DiGraph"]["Edges"]:
            source, target, _ = edge
            if source in self.graph and target in self.graph:
                self.graph.add_edge(source, target)

        self.partition = community_louvain.best_partition(self.graph.to_undirected())

        self._save_to_json()

    def _save_to_json(self):
        nodes_data = [{"id": node, "group": group} for node, group in self.partition.items()]
        links_data = [{"source": source, "target": target, "value": 1} for source, target in self.graph.edges()]

        output_data = {
            "nodes": nodes_data,
            "links": links_data
        }

        with open("./data/community_data.json", 'w', encoding='utf-8') as file:
            json.dump(output_data, file, indent=4)
