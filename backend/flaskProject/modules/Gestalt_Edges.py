import json
from sklearn.cluster import AgglomerativeClustering
import numpy as np

class NodeExtractor:
    def extract_nodes_info(self, input_file, output_file):
        with open(input_file, 'r') as file:
            data = json.load(file)

        nodes = data['DiGraph']['Nodes']
        extracted_nodes = {}

        for node, attributes in nodes.items():
            tag = attributes['Attributes']['tag']
            attrs = attributes['Attributes']['attributes']
            level = attributes['Attributes']['level']
            layer = attributes['Attributes']['layer']

            extracted_attrs = {
                'tag': tag,
                'bbox': attrs.get('bbox', None),
                'stroke': attrs.get('stroke', None),
                'fill': attrs.get('fill', None),
                'level': level,
                'layer': layer
            }

            extracted_nodes[node] = extracted_attrs

        with open(output_file, 'w') as file:
            json.dump(extracted_nodes, file, indent=4)

class HierarchicalClustering:
    def cluster_nodes(self, input_file):
        with open(input_file, 'r') as file:
            nodes = json.load(file)

        data = []
        for node, attributes in nodes.items():
            bbox = attributes['bbox']
            if bbox:
                data.append([bbox[0][0], bbox[0][1]])
            else:
                data.append([0, 0])

        data = np.array(data)
        clustering = AgglomerativeClustering(n_clusters=None, distance_threshold=0, linkage='ward').fit(data)

        clusters = {}
        for node, label in zip(nodes.keys(), clustering.labels_):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append((node, nodes[node]))

        for label, members in clusters.items():
            print(f'Cluster {label}:')
            for member in members:
                print(f'  {member[0]}: {member[1]}')
            print()

if __name__ == '__main__':
    input_file = '../GMoutput/GMinfo.json'
    output_file = '../GMoutput/extracted_nodes.json'

    extractor = NodeExtractor()
    extractor.extract_nodes_info(input_file, output_file)
    print(f"Extracted nodes information saved to {output_file}")

    clusterer = HierarchicalClustering()
    clusterer.cluster_nodes(output_file)
