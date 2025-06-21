# CS2 圖像辨識自動瞄準系統（YOLOv5）

本專案基於 YOLOv5 模型與 Python 所實作，提供一套適用於 CS2（Counter-Strike 2）的圖像辨識自動瞄準系統。透過即時螢幕擷取、目標偵測與滑鼠控制，實現 FPS 遊戲中的輔助瞄準功能。  
本專案亦可作為影像處理、深度學習應用與滑鼠自動化控制的學習範例。

---

## 📂 專案結構

| 檔案 | 說明 |
|------|------|
| `main.py` | 主程序，執行畫面擷取、模型推論與目標鎖定 |
| `game_model.py` | 載入 YOLOv5 模型，支援 GPU/CPU、FP16 加速 |
| `mouse_control.py` | 透過 Windows API 實現滑鼠底層控制 |
| `grabscreen.py` | 擷取 Windows 螢幕畫面並轉換為 OpenCV 格式 |
| `train.py` | YOLOv5 訓練腳本（需自行提供資料集） |

---

## 🚀 專案特色

- 🎯 即時目標偵測 + 滑鼠鎖定功能
- ⚡ 支援 GPU / FP16 推論加速，效能佳
- 🖱️ 右鍵開關自瞄模式（lock_mode），操作簡單
- 🧠 YOLOv5 模型可自行訓練、擴充目標類別
- 🧱 **使用底層 Windows API 控制滑鼠**  
  🔒 可繞過 CS2 對 PyAutoGUI 等高階滑鼠模擬的反作弊攔截  
  ✅ 適合實驗、測試與非公開用途

---

## 📦 環境安裝

### ✅ 建議使用 Python 3.8+
安裝必要套件（建議虛擬環境）：

```bash
pip install -r requirements.txt
