import os
import json
import networkx as nx
import igraph as ig
import leidenalg as la

class CommunityDetector:
    def __init__(self, json_file):
        self.json_file = json_file
        self.graph = None
        self.partition = None

    def execute(self):
        with open(self.json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 构建NetworkX图
        nx_graph = nx.DiGraph()
        for node_path, node_data in data["DiGraph"]["Nodes"].items():
            if node_data["Attributes"]["visible"]:
                nx_graph.add_node(node_path, **node_data)

        for edge in data["DiGraph"]["Edges"]:
            source, target, _ = edge
            if source in nx_graph and target in nx_graph:
                nx_graph.add_edge(source, target)

        # 转换NetworkX图为igraph图
        self.graph = ig.Graph.TupleList(nx_graph.edges(), directed=True)
        self.graph.vs["label"] = list(nx_graph.nodes())

        # 使用Leiden算法进行社区检测
        partition = la.find_partition(self.graph, la.ModularityVertexPartition)

        # 保存社区信息到partition属性
        self.partition = {node["label"]: membership for node, membership in zip(self.graph.vs, partition.membership)}

        self._save_to_json()

    def _save_to_json(self):
        # 使用NetworkX图的节点和边来构建links数据
        if isinstance(self.graph, nx.DiGraph) or isinstance(self.graph, nx.Graph):
            links_data = [
                {"source": source, "target": target, "value": 1}
                for source, target in self.graph.edges()
            ]
        # 使用igraph图的节点标签和边来构建links数据
        elif isinstance(self.graph, ig.Graph):
            links_data = [
                {"source": self.graph.vs[edge.source]["label"], "target": self.graph.vs[edge.target]["label"],
                 "value": 1}
                for edge in self.graph.es
            ]
        else:
            links_data = []

        nodes_data = [{"id": node, "group": group} for node, group in self.partition.items()]

        output_data = {
            "nodes": nodes_data,
            "links": links_data
        }

        with open("./data/community_data.json", 'w', encoding='utf-8') as file:
            json.dump(output_data, file, indent=4)
