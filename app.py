from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import io
import uvicorn

app = FastAPI(title="钢材表面缺陷检测API")

# ============================================================
# 1. 加载训练好的本地模型
# ============================================================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 重新构建模型结构（与训练时一致）
model = models.resnet18(pretrained=False)
num_features = model.fc.in_features
model.fc = nn.Linear(num_features, 6)  # 6分类
model.load_state_dict(torch.load("best_model.pth", map_location=device))
model = model.to(device)
model.eval()

# 类别名称（与训练时文件夹名称一致）
class_names = ['crazing', 'inclusion', 'patches', 'pitted_surface', 'rolled-in_scale', 'scratches']
class_names_zh = ['裂纹', '夹杂物', '斑块', '麻点', '氧化皮', '划痕']

# ============================================================
# 2. 图像预处理（与训练时一致）
# ============================================================
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# ============================================================
# 3. 预测接口
# ============================================================
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # 读取并转换图片
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    
    # 预处理并推理
    image_tensor = transform(image).unsqueeze(0).to(device)
    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = torch.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probabilities, 1)
    
    predicted_class = predicted.item()
    confidence_score = confidence.item()
    
    return {
        "predicted_label": class_names_zh[predicted_class],
        "confidence": confidence_score,
        "predicted_class": class_names[predicted_class]
    }

# ============================================================
# 4. 健康检查
# ============================================================
@app.get("/health")
async def health_check():
    return {"status": "ok", "model": "resnet18"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)