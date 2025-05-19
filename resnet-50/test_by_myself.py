import os
import torch
from torchvision import transforms, datasets, models
from torch.utils.data import DataLoader
import torch.nn as nn
from PIL import Image
import faiss
import numpy as np

# 设置设备（如果有 GPU 可用，则使用 GPU，否则使用 CPU）
device = torch.device( "cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)
d = 1000  # 向量维度（根据你的模型输出调整）

# 定义图像预处理
data_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# 加载已训练的模型
model = models.resnet50(pretrained=True)
#model.fc = nn.Linear(2048, d)  # 确保最后一层与训练时的设置相同
model = model.to(device)
model.eval()  # 切换到评估模式

# 图片文件夹路径
data_set_dir = '/home/cike/resnet-50/pic'

# 创建列表来存储图片张量和文件名
pic_set = []
file_names = []
for filename in os.listdir(data_set_dir):
    if filename.endswith(('.jpg', '.jpeg', '.png', '.bmp')):
        # 构建完整的图片路径
        image_path = os.path.join(data_set_dir, filename)
        image = Image.open(image_path).convert('RGB')
        image_tensor = data_transforms(image)
        image_tensor = image_tensor.unsqueeze(0).to(device)
        pic_set.append(image_tensor)
        file_names.append(filename)

# 使用模型推理得到特征向量
feature_vectors = []
for img_tensor in pic_set:
    with torch.no_grad():
        output = model(img_tensor)  # 通过网络进行推理
    output = output.squeeze(0).cpu().numpy().astype('float32')
    feature_vectors.append(output)

# 转换为 numpy 数组
xb = np.array(feature_vectors, dtype=np.float32)
# 创建 IndexFlatL2 索引
index_flat = faiss.IndexFlatL2(d)

# 将索引迁移到 GPU
res = faiss.StandardGpuResources()
gpu_index_flat = faiss.index_cpu_to_gpu(res, 0, index_flat)

# 添加数据到 GPU 索引
gpu_index_flat.add(xb)

# 示例：查询
query_image_path = '/home/cike/resnet-50/135.jpg'
query_image = Image.open(query_image_path).convert('RGB')
query_tensor = data_transforms(query_image).unsqueeze(0).to(device)
with torch.no_grad():
    query_output = model(query_tensor)
query_vector = query_output.squeeze(0).cpu().numpy().astype('float32')

k = 5  # 返回最相似的2个向量
D, I = gpu_index_flat.search(query_vector.reshape(1, -1), k)  # D为距离，I为索引

# 打印最近邻的索引和对应的距离
print("最近邻的索引:", I)
print("对应的距离:", D)

# 获取对应的文件名
nearest_neighbors = [file_names[i] for i in I[0]]
print("最近邻的图片文件名:", nearest_neighbors)

# 显示查询图片和相似图片
print('查询的图片', query_image_path)

# 显示相似图片
for filename in nearest_neighbors:
    similar_image_path = os.path.join(data_set_dir, filename)
    print('相似的图片', similar_image_path)