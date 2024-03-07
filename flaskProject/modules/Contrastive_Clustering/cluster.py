import json
import os
import torch
from torch.utils.data import Dataset, DataLoader
# from All import ModifiedNetwork  # 确保这个路径正确指向了您定义ModifiedNetwork的模块
from modules.Contrastive_Clustering.All import ModifiedNetwork  # 确保这个路径正确指向了您定义ModifiedNetwork的模块

# model_save_path = "./save/model_checkpoint.tar"  # 设置模型保存路径
# dataset_path = "./test"
# output_file_path = '../../data/community_data.json'
model_save_path = "./modules/Contrastive_Clustering/save/model_checkpoint.tar"  # 设置模型保存路径
dataset_path = "./modules/Contrastive_Clustering/test"
output_file_path = './data/community_data.json'


class FeatureVectorDataset(Dataset):
    def __init__(self, directory):
        super(FeatureVectorDataset, self).__init__()  # 添加这一行来正确初始化父类
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
                    identifier = parts[0]  # 提取标识符
                    features = [float(part) for part in parts[1:]]  # 提取特征向量
                    self.identifiers.append(identifier)
                    self.features.append(features)

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return self.identifiers[idx], torch.tensor(self.features[idx], dtype=torch.float32)


def load_model(model_path, model):
    checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
    model.load_state_dict(checkpoint['model_state_dict'])
    return model


def predict(model, dataset):
    model.eval()
    loader = DataLoader(dataset, batch_size=128, shuffle=False)
    all_identifiers = []
    all_predictions = []
    with torch.no_grad():
        for identifiers, features in loader:
            features = features.to(torch.device('cpu'))
            _, c = model(features)
            predicted_clusters = torch.argmax(c, dim=1)
            all_identifiers.extend(identifiers)
            all_predictions.extend(predicted_clusters.tolist())
    return all_identifiers, all_predictions


class ClusterPredictor:
    def __init__(self, model_save_path = model_save_path, dataset_path = dataset_path, output_file_path = output_file_path, input_dim=20, feature_dim=20, class_num=50):
        self.model_save_path = model_save_path
        self.dataset_path = dataset_path
        self.output_file_path = output_file_path
        self.input_dim = input_dim
        self.feature_dim = feature_dim
        self.class_num = class_num

        # 初始化模型
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
        self.model.eval()
        with torch.no_grad():
            for identifiers, features in loader:
                features = features.to(torch.device('cpu'))
                _, c = self.model(features)
                predicted_clusters = torch.argmax(c, dim=1)
                all_identifiers.extend(identifiers)
                all_predictions.extend(predicted_clusters.tolist())
        return all_identifiers, all_predictions

    def save_to_json(self, identifiers, predicted_clusters):
        unique_clusters = sorted(set(predicted_clusters))
        cluster_mapping = {cluster: i + 1 for i, cluster in enumerate(unique_clusters)}
        mapped_clusters = [cluster_mapping[cluster] for cluster in predicted_clusters]

        # 构建 nodes
        nodes = [{"id": identifier, "group": mapped_cluster} for identifier, mapped_cluster in
                 zip(identifiers, mapped_clusters)]

        # 构建 links
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

    def run(self):
        identifiers, predicted_clusters = self.predict()
        self.save_to_json(identifiers, predicted_clusters)


# predictor = ClusterPredictor()
# predictor.run()
