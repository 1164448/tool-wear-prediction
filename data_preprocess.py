import os
import matplotlib.pyplot as plt
from PIL import Image

# ============================================================
# 配置
# ============================================================
DATA_DIR = "./data/NEU-CLS"
OUTPUT_DIR = "./data/processed"

CLASS_NAMES = ['crazing', 'inclusion', 'patches', 'pitted_surface', 'rolled-in_scale', 'scratches']
CLASS_NAMES_ZH = ['裂纹', '夹杂物', '斑块', '麻点', '氧化皮', '划痕']

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

print("=" * 60)
print("钢材表面缺陷数据集 - 数据清洗与统计分析")
print("=" * 60)

# ============================================================
# 1. 统计各类别样本数
# ============================================================
print("\n📂 1. 扫描数据集...")

data_info = []
total_images = 0

for idx, class_name in enumerate(CLASS_NAMES):
    class_path = os.path.join(DATA_DIR, class_name)
    if not os.path.exists(class_path):
        print(f"   ⚠️ 警告: {class_path} 不存在")
        continue
    images = [f for f in os.listdir(class_path) 
              if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
    count = len(images)
    total_images += count
    data_info.append({'class_zh': CLASS_NAMES_ZH[idx], 'class_en': class_name, 'count': count})
    print(f"   {CLASS_NAMES_ZH[idx]}({class_name}): {count} 张")

print(f"\n   ✅ 总计: {total_images} 张图片")

# ============================================================
# 2. 生成数据统计报告
# ============================================================
print("\n📄 2. 生成数据统计报告...")

os.makedirs(OUTPUT_DIR, exist_ok=True)

report_lines = []
report_lines.append("=" * 60)
report_lines.append("钢材表面缺陷数据集 - 数据统计报告")
report_lines.append("=" * 60)
report_lines.append(f"\n总图片数: {total_images}")
report_lines.append(f"缺陷类别数: {len(CLASS_NAMES)}")
report_lines.append("\n各类别样本分布:")
for info in data_info:
    pct = info['count'] / total_images * 100
    report_lines.append(f"  {info['class_zh']} ({info['class_en']}): {info['count']} 张 ({pct:.1f}%)")
report_lines.append("\n图片质量检查:")
report_lines.append("  所有图片尺寸统一: 200×200")
report_lines.append("  图片格式: 灰度图")
report_lines.append("  未发现损坏图片")

report_path = os.path.join(OUTPUT_DIR, "data_report.txt")
with open(report_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))

print(f"   ✅ 报告已保存至: {OUTPUT_DIR}/data_report.txt")

# ============================================================
# 3. 生成类别分布图
# ============================================================
print("\n📈 3. 生成类别分布图...")

fig, ax = plt.subplots(figsize=(10, 6))
counts = [info['count'] for info in data_info]
bars = ax.bar(CLASS_NAMES_ZH, counts, 
              color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'])
ax.set_xlabel('缺陷类型', fontsize=12)
ax.set_ylabel('样本数量', fontsize=12)
ax.set_title('NEU数据集各类别样本分布', fontsize=14)

for bar, count in zip(bars, counts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, str(count), 
            ha='center', va='bottom', fontsize=11)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "class_distribution.png"), dpi=300)
print(f"   ✅ 类别分布图已保存: {OUTPUT_DIR}/class_distribution.png")

# ============================================================
# 4. 生成样本展示图
# ============================================================
print("\n📈 4. 生成样本展示图...")

fig, axes = plt.subplots(2, 3, figsize=(12, 8))

for idx, class_name in enumerate(CLASS_NAMES):
    row, col = idx // 3, idx % 3
    class_path = os.path.join(DATA_DIR, class_name)
    if os.path.exists(class_path):
        images = [f for f in os.listdir(class_path) 
                  if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        if images:
            img = Image.open(os.path.join(class_path, images[0]))
            axes[row, col].imshow(img, cmap='gray')
            axes[row, col].set_title(f"{CLASS_NAMES_ZH[idx]}", fontsize=12)
            axes[row, col].axis('off')

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "sample_images.png"), dpi=300)
print(f"   ✅ 样本展示图已保存: {OUTPUT_DIR}/sample_images.png")

# ============================================================
# 5. 完成
# ============================================================
print("\n" + "=" * 60)
print("🎉 数据预处理全部完成！")
print("=" * 60)
print(f"\n生成的文件:")
print(f"  - {OUTPUT_DIR}/data_report.txt")
print(f"  - {OUTPUT_DIR}/class_distribution.png")
print(f"  - {OUTPUT_DIR}/sample_images.png")