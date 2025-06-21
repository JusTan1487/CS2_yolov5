import sys
import os

# 將上層目錄加入模組搜尋路徑，以便匯入自訂模組（如 models.experimental）
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch  # 引入 PyTorch，進行模型載入與推論

# 匯入 YOLOv5 中的模型載入函數
from models.experimental import attempt_load

# 判斷是否可使用 GPU，否則使用 CPU
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# 若使用 GPU，啟用 FP16 混合精度加速推論
half = device != 'cpu'

# 指定訓練好的模型權重檔路徑
weights = r'C:\STUDY\HW\PYTHON\yolov5-master\runs\train\exp4\weights\best.pt'

# 設定模型輸入影像尺寸
imgsz = 640

def load_model():
    """
    載入訓練好的 YOLOv5 模型，並根據硬體配置使用 FP16 或 FP32 模式。
    回傳已初始化的模型物件。
    """
    # 載入模型並移動到指定設備（CPU/GPU）
    model = attempt_load(weights).to(device)  # 預設為 FP32 模型

    # 若使用 GPU，則轉換為 FP16 模式加快推論速度
    if half:
        model.half()

    # 在 GPU 上先跑一次推論來初始化模型（如 BatchNorm、CUDA kernel 等）
    if device != 'cpu':
        model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))

    return model
