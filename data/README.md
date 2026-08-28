# 数据集说明

## 数据来源
东北大学NEU表面缺陷数据库（NEU-CLS）

## 数据集链接
https://www.kaggle.com/datasets/kaustubhdikshit/neu-surface-defect-database

## 数据集简介
- 发布机构：东北大学
- 包含6类缺陷：裂纹(Cr)、夹杂物(In)、斑块(Pa)、麻点(PS)、氧化皮(RS)、划痕(Sc)
- 每类300张灰度图像，共1800张
- 图像尺寸：200×200像素

## 目录结构
NEU-CLS/
├── crazing/ # 裂纹
├── inclusion/ # 夹杂物
├── patches/ # 斑块
├── pitted_surface/ # 麻点
├── rolled-in_scale/ # 氧化皮
└── scratches/ # 划痕

## 数据划分
按8:2划分训练集和验证集，使用 `data_preprocess.py` 完成划分。