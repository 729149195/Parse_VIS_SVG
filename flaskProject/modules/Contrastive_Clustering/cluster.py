import os
import torch
from torch.utils.data import Dataset, DataLoader
from All import ModifiedNetwork  # 确保这个路径正确指向了您定义ModifiedNetwork的模块

model_save_path = "./save/model_checkpoint.tar"  # 设置模型保存路径
dataset_path = "./test"


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


if __name__ == "__main__":
    input_dim = 20
    feature_dim = 20
    class_num = 50
    model = ModifiedNetwork(input_dim, feature_dim, class_num)

    model_save_path = model_save_path # 确保这是您模型保存的正确路径
    dataset_path = dataset_path  # 指向您想要进行聚类预测的数据集的路径

    loaded_model = load_model(model_save_path, model)
    dataset = FeatureVectorDataset(dataset_path)

    identifiers, predicted_clusters = predict(loaded_model, dataset)

    unique_clusters = sorted(set(predicted_clusters))

    # 创建映射
    cluster_mapping = {cluster: i+1 for i, cluster in enumerate(unique_clusters)}

    # 映射聚类编号
    mapped_clusters = [cluster_mapping[cluster] for cluster in predicted_clusters]

    for identifier, mapped_cluster in zip(identifiers, mapped_clusters):
        print(f"{identifier}, Mapped Cluster: {mapped_cluster}")

