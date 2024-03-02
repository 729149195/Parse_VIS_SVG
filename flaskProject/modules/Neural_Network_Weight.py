import torch
import json
from torch.utils.data import DataLoader, TensorDataset

json_file_path = '../GMoutput/similarity_graph.json'

# 1. 加载数据
with open(json_file_path, 'r') as f:
    data = json.load(f)

# 2. 提取特征
features = [item[2] for item in data['Gestalt_Edges']]

# 3. 数据转换
# 转换为PyTorch张量，这里假设所有数据都是作为输入特征，没有标签
features_tensor = torch.tensor(features, dtype=torch.float32)

# print(features_tensor)
print(torch.__version__)

# Check if CUDA is available
cuda_available = torch.cuda.is_available()

if cuda_available:
    print(f"CUDA is available. Number of GPUs: {torch.cuda.device_count()}")
    for i in range(torch.cuda.device_count()):
        print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
else:
    print("CUDA is not available. No GPU detected.")

#判断是否安装了cuda
import torch
print(torch.cuda.is_available())  #返回True则说明已经安装了cuda
#判断是否安装了cuDNN
from torch.backends import  cudnn
print(cudnn.is_available())  #返回True则说明已经安装了cuDNN