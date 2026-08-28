import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, random_split
import matplotlib.pyplot as plt
import os

# ============================================================
# 1. 基本配置
# ============================================================
data_dir = "./data/NEU-CLS"          # 数据集路径（请确认这个路径下有 Cr、In 等文件夹）
num_classes = 6                       # 6种缺陷类型
batch_size = 32                       # 每次训练32张图片
num_epochs = 30                       # 训练30轮（CPU约15-20分钟）
learning_rate = 0.001                 # 学习率

# 自动检测设备（有显卡用GPU，没有则用CPU）
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"✅ 使用设备: {device}")

# ============================================================
# 2. 数据预处理与数据增强
# ============================================================
# 训练集：随机翻转、旋转、缩放 + 归一化
train_transform = transforms.Compose([
    transforms.RandomHorizontalFlip(p=0.5),      # 随机水平翻转
    transforms.RandomRotation(15),               # 随机旋转 ±15°
    transforms.Resize((224, 224)),               # ResNet18 需要 224x224 输入
    transforms.ToTensor(),                       # 转换为张量
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# 验证集：仅缩放和归一化（不作数据增强）
val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# ============================================================
# 3. 加载数据集（按 80% 训练 / 20% 验证 划分）
# ============================================================
full_dataset = datasets.ImageFolder(root=data_dir, transform=train_transform)

train_size = int(0.8 * len(full_dataset))
val_size = len(full_dataset) - train_size
train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])

# 验证集使用独立的 transform（无数据增强）
val_dataset.dataset.transform = val_transform

train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

print(f"✅ 训练集样本数: {len(train_dataset)}")
print(f"✅ 验证集样本数: {len(val_dataset)}")
print(f"✅ 类别名称: {full_dataset.classes}")

# ============================================================
# 4. 加载预训练 ResNet18 模型（迁移学习）
# ============================================================
model = models.resnet18(pretrained=True)

# 冻结除最后一层外的所有参数
for param in model.parameters():
    param.requires_grad = False

# 替换最后一层全连接层，输出为6分类
num_features = model.fc.in_features
model.fc = nn.Linear(num_features, num_classes)

model = model.to(device)

# ============================================================
# 5. 定义损失函数和优化器
# ============================================================
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.fc.parameters(), lr=learning_rate)

# ============================================================
# 6. 开始训练
# ============================================================
train_losses = []
val_accuracies = []

print("\n🚀 开始训练...（约需15-20分钟，请耐心等待）\n")

for epoch in range(num_epochs):
    # --- 训练阶段 ---
    model.train()
    running_loss = 0.0
    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    avg_loss = running_loss / len(train_loader)
    train_losses.append(avg_loss)

    # --- 验证阶段 ---
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    accuracy = 100 * correct / total
    val_accuracies.append(accuracy)

    print(f"Epoch [{epoch+1:2d}/{num_epochs}]  Loss: {avg_loss:.4f}  Val Acc: {accuracy:.2f}%")

# ============================================================
# 7. 保存训练好的模型
# ============================================================
torch.save(model.state_dict(), "best_model.pth")
print("\n✅ 模型训练完成！已保存为 best_model.pth")

# ============================================================
# 8. 绘制并保存训练曲线
# ============================================================
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(train_losses)
plt.title("训练损失曲线")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(val_accuracies)
plt.title("验证准确率曲线")
plt.xlabel("Epoch")
plt.ylabel("Accuracy (%)")
plt.grid(True)

plt.savefig("training_curves.png")
print("✅ 训练曲线已保存为 training_curves.png")

print("\n🎉 全部完成！现在可以关闭此窗口，或继续下一步。")