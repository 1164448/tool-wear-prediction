# 基于深度学习的热轧带钢表面缺陷检测系统

基于ResNet18迁移学习，实现热轧带钢表面六类缺陷的自动识别与分类。

## 数据集

本项目使用东北大学公开发布的 **NEU表面缺陷数据库（NEU-CLS）**。

- 数据来源：https://www.kaggle.com/datasets/kaustubhdikshit/neu-surface-defect-database
- 数据规模：1800张灰度图像，6类缺陷各300张
- 图像尺寸：200×200像素
- 划分方式：训练集:验证集 = 8:2
- 存储位置：`/data/NEU-CLS/`

## 数据预处理

使用 `data_preprocess.py` 完成图片完整性检查、尺寸验证、像素分布分析及数据集划分。