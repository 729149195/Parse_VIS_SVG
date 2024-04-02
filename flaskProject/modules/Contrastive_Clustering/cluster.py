import json
import os
import torch
from torch.utils.data import Dataset, DataLoader
# from All import ModifiedNetwork  # 确保这个路径正确指向了您定义ModifiedNetwork的模块

from modules.Contrastive_Clustering.All import ModifiedNetwork  # 确保这个路径正确指向了您定义ModifiedNetwork的模块

# model_save_path = "./save/model_checkpoint_color.tar"  # 设置模型保存路径
# dataset_path = "./test"
# output_file_path = '../../data/community_data.json'
# probabilities_file_path = '../../data/cluster_probabilities.json'  # 新增：聚类概率保存路径


model_save_path = "./modules/Contrastive_Clustering/save/model_checkpoint_6_300.tar"  # 设置模型保存路径
dataset_path = "./modules/Contrastive_Clustering/test"
# dataset_path = "./modules/Contrastive_Clustering/testR"
output_file_path = './data/community_data.json'
probabilities_file_path = './data/cluster_probabilities.json'  # 新增：聚类概率保存路径


class FeatureVectorDataset(Dataset):
    def __init__(self, directory):
        super(FeatureVectorDataset, self).__init__()
        self.directory = directory
        self.files = os.listdir(directory)
        self.identifiers = []
        self.features = []
        self.load_features()

    def load_features(self):
        for file_name in self.files:
            file_path = os.path.join(self.directory, file_name)
            with open(file_path, 'r') as file:
                for line in file:
                    parts = line.strip().split()
                    identifier = parts[0]
                    features = [float(part) for part in parts[1:]]
                    self.identifiers.append(identifier)
                    self.features.append(features)

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return self.identifiers[idx], torch.tensor(self.features[idx], dtype=torch.float32)


class ClusterPredictor:
    def __init__(self, model_save_path=model_save_path, dataset_path=dataset_path, output_file_path=output_file_path,
                 input_dim=20, feature_dim=20, class_num=50):
        self.model_save_path = model_save_path
        self.dataset_path = dataset_path
        self.output_file_path = output_file_path
        self.input_dim = input_dim
        self.feature_dim = feature_dim
        self.class_num = class_num

        self.model = ModifiedNetwork(self.input_dim, self.feature_dim, self.class_num)
        self.load_model()

    def load_model(self):
        checkpoint = torch.load(self.model_save_path, map_location=torch.device('cpu'))
        self.model.load_state_dict(checkpoint['model_state_dict'])

    def predict(self):
        dataset = FeatureVectorDataset(self.dataset_path)
        loader = DataLoader(dataset, batch_size=128, shuffle=False)
        all_identifiers = []
        all_predictions = []
        all_probabilities = []  # 新增：用于保存聚类概率
        self.model.eval()
        with torch.no_grad():
            for identifiers, features in loader:
                features = features.to(torch.device('cpu'))
                _, probabilities = self.model(features)  # 获取聚类概率
                predicted_clusters = torch.argmax(probabilities, dim=1)
                all_identifiers.extend(identifiers)
                all_predictions.extend(predicted_clusters.tolist())
                all_probabilities.extend(probabilities.tolist())  # 保存聚类概率
        return all_identifiers, all_predictions, all_probabilities

    def save_probabilities_to_json(self, identifiers, probabilities):
        # 新增：将聚类概率保存到JSON文件
        data = [{"id": identifier, "probabilities": prob} for identifier, prob in zip(identifiers, probabilities)]
        with open(probabilities_file_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Cluster probabilities saved to {probabilities_file_path}")

    def run(self):
        identifiers, predicted_clusters, probabilities = self.predict()
        self.save_to_json(identifiers, predicted_clusters)
        self.save_probabilities_to_json(identifiers, probabilities)  # 保存聚类概率

    def save_to_json(self, identifiers, predicted_clusters):
        # 现有的保存聚类结果的方法保持不变
        unique_clusters = sorted(set(predicted_clusters))
        cluster_mapping = {cluster: i + 1 for i, cluster in enumerate(unique_clusters)}
        mapped_clusters = [cluster_mapping[cluster] for cluster in predicted_clusters]

        nodes = [{"id": identifier, "group": mapped_cluster} for identifier, mapped_cluster in
                 zip(identifiers, mapped_clusters)]
        links = []
        cluster_to_identifiers = {}
        for identifier, mapped_cluster in zip(identifiers, mapped_clusters):
            if mapped_cluster not in cluster_to_identifiers:
                cluster_to_identifiers[mapped_cluster] = []
            cluster_to_identifiers[mapped_cluster].append(identifier)

        for cluster, ids in cluster_to_identifiers.items():
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    links.append({"source": ids[i], "target": ids[j], "value": 1})

        output_data = {"nodes": nodes, "links": links}
        with open(self.output_file_path, 'w') as f:
            json.dump(output_data, f, indent=4)
        print(f"Output saved to {self.output_file_path}")


# predictor = ClusterPredictor()
# predictor.run()
