# 配置参数，直接以变量形式暴露

device = "cpu"  # 使用 "cuda" 或 "cpu"
pretrain = True  # 是否加载预训练模型
model_type = "resnet50"  # torchvision.models 里的模型名
input_size = 224  # 输入图像的大小

normalize_mean = [0.485, 0.456, 0.406]  # 图像预处理的均值
normalize_std = [0.229, 0.224, 0.225]   # 图像预处理的标准差
