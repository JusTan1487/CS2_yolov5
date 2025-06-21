# main.py
# ✅ YOLOv5 圖像辨識 + 自瞄系統主程式

from grabscreen import grab_screen  # 擷取遊戲畫面
from game_model import load_model   # 載入 YOLOv5 模型
from utils.general import non_max_suppression, scale_boxes, xyxy2xywh  # 處理模型輸出
from utils.augmentations import letterbox  # 調整輸入圖片尺寸

import cv2
import win32gui, win32con
import torch
import numpy as np
import pynput
import ctypes
from mouse_control import lock  # 自定義滑鼠移動模組

# === 自動獲取螢幕解析度 ===
user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)
x, y = screen_width, screen_height
re_x, re_y = screen_width, screen_height

# === YOLO 模型設定 ===
device = 'cuda' if torch.cuda.is_available() else 'cpu'  # 使用 GPU 或 CPU
half = device != 'cpu'  # 若使用 GPU 則使用 FP16 模式
conf_thres = 0.75       # 信心閾值
iou_thres = 0.05        # IOU 非極大值抑制
imgsz = 640             # 輸入圖像尺寸
lock_mode = False       # 自瞄開關狀態
mouse = pynput.mouse.Controller()

# === 滑鼠右鍵切換自瞄模式 ===
def on_click(x, y, button, pressed):
    global lock_mode
    if pressed and button == pynput.mouse.Button.right:
        lock_mode = not lock_mode
        print("Lock mode", "on" if lock_mode else "off")

listener = pynput.mouse.Listener(on_click=on_click)
listener.start()

# === 載入模型 ===
model = load_model().to(device)
stride, names = model.stride, model.names
if half:
    model.half()

# === 主偵測 + 自瞄迴圈 ===
while True:
    img0 = grab_screen(region=(0, 0, x, y))       # 擷取整個螢幕畫面
    img0 = cv2.resize(img0, (re_x, re_y))         # 重新調整解析度

    # 圖像預處理
    img = letterbox(img0, imgsz, stride=int(stride.max()))[0]
    img = img.transpose((2, 0, 1))[::-1]          # BGR to RGB, HWC to CHW
    img = np.ascontiguousarray(img)

    img = torch.from_numpy(img).to(device)
    img = img.half() if half else img.float()
    img /= 255.0
    if img.ndimension() == 3:
        img = img.unsqueeze(0)

    # 模型推論
    pred = model(img, augment=False, visualize=False)
    pred = non_max_suppression(pred, conf_thres, iou_thres)

    aims = []
    for det in pred:
        gn = torch.tensor(img0.shape)[[1, 0, 1, 0]]  # Normalization factor
        if len(det):
            det[:, :4] = scale_boxes(img.shape[2:], det[:, :4], img0.shape).round()
            for *xyxy, conf, cls in reversed(det):
                xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()
                aim = ("%g " * (1 + len(xywh))).rstrip() % (cls, *xywh)
                aims.append([float(x) for x in aim.split()])

    # === 執行自瞄與畫框 ===
    if aims:
        if lock_mode:
            lock(aims, None, x, y)  # 根據最近目標移動滑鼠至準心

        for det in aims:
            _, x_c, y_c, w, h = det
            x_c, w = re_x * x_c, re_x * w
            y_c, h = re_y * y_c, re_y * h
            top_left = (int(x_c - w / 2), int(y_c - h / 2))
            bottom_right = (int(x_c + w / 2), int(y_c + h / 2))
            cv2.rectangle(img0, top_left, bottom_right, (0, 255, 0), 3)

    # === 顯示偵測畫面 ===
    cv2.namedWindow('csgo-detect', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('csgo-detect', re_x // 3, re_y // 3)
    cv2.imshow('csgo-detect', img0)

    # 視窗永遠置頂
    hwnd = win32gui.FindWindow(None, 'csgo-detect')
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                          win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

    # 按 Q 結束
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
