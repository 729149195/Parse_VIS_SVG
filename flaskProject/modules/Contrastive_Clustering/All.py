import torch
import math
import torch.nn as nn
import os
from torch.utils.data import Dataset, DataLoader
from torch.nn.functional import normalize

epochs = 300
temperature = 0.5
batch_size = 30
learning_rate = 0.0003
dataset_path = "./feature_txt"
model_save_path = "save/model_checkpoint.tar"  # 设置模型保存路径

class InstanceLoss(nn.Module):
    def __init__(self, temperature, device):
        super(InstanceLoss, self).__init__()
        self.temperature = temperature
        self.device = device
        self.criterion = nn.CrossEntropyLoss(reduction="sum")

    def forward(self, z_i, z_j):
        # Concatenate features to have a 2N x feature_dim tensor
        z = torch.cat([z_i, z_j], dim=0)
        N = z_i.size(0)

        # Compute similarity matrix
        sim = torch.mm(z, z.T) / self.temperature
        sim.fill_diagonal_(-float('inf'))  # Eliminate self-similarity

        # Create labels for matching pairs
        labels = torch.arange(N).to(self.device)
        labels = torch.cat([labels, labels], dim=0)  # Labels for both z_i and z_j
        positives = torch.cat([torch.diag(sim[:N, N:]), torch.diag(sim[N:, :N])], dim=0)

        # Mask to select negative samples
        mask = ~torch.eye(2 * N, dtype=bool).to(self.device)
        negatives = sim[mask].view(2 * N, -1)

        # Log-Softmax over the negative dimension
        logits = torch.cat((positives.unsqueeze(1), negatives), dim=1)
        labels = torch.zeros(2 * N, dtype=torch.long).to(self.device)  # Target index for positives is always 0

        # Cross-entropy loss between positive and all negatives
        loss = self.criterion(torch.log_softmax(logits, dim=1), labels)
        return loss.mean()


class DynamicClusterLoss(nn.Module):
    def __init__(self, temperature, device):
        super(DynamicClusterLoss, self).__init__()
        self.temperature = temperature
        self.device = device
        self.criterion = nn.CrossEntropyLoss(reduction="sum")
        self.similarity_f = nn.CosineSimilarity(dim=2)

    def forward(self, c_i, c_j):
        p_i = c_i.sum(0).view(-1)
        p_i /= p_i.sum()
        ne_i = math.log(p_i.size(0)) + (p_i * torch.log(p_i + 1e-8)).sum()  # Add epsilon to avoid log(0)
        p_j = c_j.sum(0).view(-1)
        p_j /= p_j.sum()
        ne_j = math.log(p_j.size(0)) + (p_j * torch.log(p_j + 1e-8)).sum()  # Add epsilon to avoid log(0)
        ne_loss = ne_i + ne_j
        c_i = c_i.t()
        c_j = c_j.t()
        class_num = c_i.size(0)  # Dynamically determine class number

        # print(class_num)

        N = 2 * class_num
        c = torch.cat((c_i, c_j), dim=0)
        sim = self.similarity_f(c.unsqueeze(1), c.unsqueeze(0)) / self.temperature
        sim_i_j = torch.diag(sim, class_num)
        sim_j_i = torch.diag(sim, -class_num)
        positive_clusters = torch.cat((sim_i_j, sim_j_i), dim=0).reshape(N, 1)
        negative_clusters = sim.masked_select(~torch.eye(N, dtype=torch.bool).to(self.device)).reshape(N, -1)
        labels = torch.zeros(N).to(self.device).long()
        logits = torch.cat((positive_clusters, negative_clusters), dim=1)
        loss = self.criterion(torch.log_softmax(logits, dim=1), labels)  # Ensure numerical stability with log_softmax
        loss /= N
        return loss + ne_loss


class ModifiedNetwork(nn.Module):
    def __init__(self, input_dim, feature_dim, class_num):
        super(ModifiedNetwork, self).__init__()
        self.input_dim = input_dim
        self.feature_dim = feature_dim
        self.cluster_num = class_num
        self.instance_projector = nn.Sequential(
            nn.Linear(self.input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, self.feature_dim),
        )
        self.cluster_projector = nn.Sequential(
            nn.Linear(self.input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, self.cluster_num),
            nn.Softmax(dim=1)
        )

    def forward(self, x):
        z = normalize(self.instance_projector(x), dim=1)
        c = self.cluster_projector(x)
        return z, c

    def forward_cluster(self, x):
        c = self.cluster_projector(x)
        c = torch.argmax(c, dim=1)
        return c


class FeatureVectorDataset(Dataset):
    def __init__(self, directory):
        self.directory = directory
        self.files = os.listdir(directory)
        self.features = []
        self.load_features()

    def load_features(self):
        for file in self.files:
            file_path = os.path.join(self.directory, file)
            with open(file_path, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    features = [float(part) for part in parts[1:]]  # 跳过标识符
                    self.features.append(features)

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return torch.tensor(self.features[idx], dtype=torch.float32)


def mirror_features_horizontally(features, canvas_width):
    # 假设 features 的顺序是 [tag_encode, opacity, ..., left, right, ..., center_x, ...]
    # 注意：您需要根据实际的特征顺序调整索引
    left_index = 13  # 示例索引，实际应根据特征向量的结构调整
    right_index = 14
    center_x_index = 15
    # 水平镜像操作
    mirrored_features = features.clone()
    mirrored_features[:, left_index] = canvas_width - features[:, right_index]
    mirrored_features[:, right_index] = canvas_width - features[:, left_index]
    mirrored_features[:, center_x_index] = canvas_width - features[:, center_x_index]

    return mirrored_features


def apply_feature_transformation(features):
    # 假设画布宽度是一个固定值，这里需要根据您的实际情况来设置
    canvas_width = 500  # 例如，如果您的坐标系统的宽度范围是从0到1000
    # 对特征进行镜像变换
    mirrored_features = mirror_features_horizontally(features, canvas_width)
    return mirrored_features


def simplified_train_loop(dataset, model, instance_loss, cluster_loss, optimizer, epochs=epochs):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for features in DataLoader(dataset, batch_size=batch_size, shuffle=False):
            features = features.to(device)
            optimizer.zero_grad()

            # 对特征进行镜像变换
            transformed_features = apply_feature_transformation(features)

            # 计算原始特征和变换后特征的模型输出
            z_original, c_original = model(features)
            z_transformed, c_transformed = model(transformed_features)

            # 使用原始特征和变换后特征计算损失
            loss_i = instance_loss(z_original, z_transformed)  # 使用原始和变换后的特征计算实例损失
            loss_c = cluster_loss(c_original, c_transformed)  # 使用原始和变换后的特征计算聚类损失
            loss = loss_i + loss_c
            # print(loss_i, loss_c)

            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch + 1}/{epochs}, Loss: {total_loss / len(DataLoader(dataset))}")


def save_model(model, optimizer, epoch, save_path):
    state = {
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'epoch': epoch,
    }
    torch.save(state, save_path)


def load_model(model, optimizer, load_path):
    checkpoint = torch.load(load_path)
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    epoch = checkpoint['epoch']
    return model, optimizer, epoch


if __name__ == "__main__":
    input_dim = 20
    feature_dim = 20  # Adjusted feature dimension
    class_num = 50  # Placeholder for class number, not used in DynamicClusterLoss
    model = ModifiedNetwork(input_dim, feature_dim, class_num).to(
        torch.device("cuda" if torch.cuda.is_available() else "cpu"))
    instance_loss = InstanceLoss(temperature=temperature,
                                 device=torch.device("cuda" if torch.cuda.is_available() else "cpu"))
    cluster_loss = DynamicClusterLoss(temperature=temperature,
                                      device=torch.device("cuda" if torch.cuda.is_available() else "cpu"))
    optimizer = torch.optim.Adam(model.parameters(), lr = learning_rate)
    dataset_path = dataset_path
    dataset = FeatureVectorDataset(dataset_path)
    model_save_path = model_save_path
    start_epoch = 0
    # Check if there is a pretrained model
    if os.path.exists(model_save_path):
        checkpoint = torch.load(model_save_path)
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        start_epoch = checkpoint['epoch'] + 1
        print(f"Loaded checkpoint from epoch {start_epoch}.")
    for epoch in range(start_epoch, epochs):
        total_loss = 0
        for features in DataLoader(dataset, batch_size=batch_size, shuffle=True):
            features = features.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
            optimizer.zero_grad()
            z, c = model(features)
            transformed_features = apply_feature_transformation(features)
            z_transformed, c_transformed = model(transformed_features)
            loss_i = instance_loss(z, z_transformed)
            loss_c = cluster_loss(c, c_transformed)
            loss = loss_i + loss_c
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch + 1}/{epochs}, Loss: {total_loss / len(DataLoader(dataset))}")
        # Save model state
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
        }, model_save_path)