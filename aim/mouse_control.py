import ctypes

# 定義 MOUSEINPUT 結構，對應 Windows API 中的滑鼠輸入結構
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),            # 水平移動量
        ("dy", ctypes.c_long),            # 垂直移動量
        ("mouseData", ctypes.c_ulong),    # 滾輪資料或X按鈕
        ("dwFlags", ctypes.c_ulong),      # 行為標誌（如移動、點擊）
        ("time", ctypes.c_ulong),         # 事件發生時間（0 為系統提供時間戳）
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))  # 額外資訊
    ]

# INPUT 的聯合結構體，這裡只使用滑鼠輸入（mi）
class INPUT_I(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT)]

# 定義 Windows API 所需的 INPUT 結構
class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),         # 輸入類型：滑鼠、鍵盤或硬體
        ("ii", INPUT_I)                   # 輸入數據
    ]

# 常數定義：輸入類型與滑鼠事件標誌
INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001  # 表示滑鼠移動事件

def move_mouse_rel(dx, dy):
    """
    模擬滑鼠相對移動。
    dx, dy 表示與目前位置的偏移量。
    """
    extra = ctypes.c_ulong(0)
    ii = INPUT_I()
    ii.mi = MOUSEINPUT(dx, dy, 0, MOUSEEVENTF_MOVE, 0, ctypes.pointer(extra))
    command = INPUT(ctypes.c_ulong(INPUT_MOUSE), ii)

    # 呼叫 Windows API 傳送滑鼠輸入指令
    ctypes.windll.user32.SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))


def lock(aims, _, x, y):
    """
    鎖定目標並將滑鼠移動至目標位置（自瞄功能）。

    aims: 目標列表，每個為 (tag, x_center, y_center, w, h)
    x, y: 視窗或畫面實際解析度比例（與 YOLO 推論畫面對應）
    """
    dist_list = []
    mouse_pos = ctypes.wintypes.POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(mouse_pos))  # 取得目前滑鼠座標

    # 計算所有目標與滑鼠之間的距離平方值
    for det in aims:
        _, x_c, y_c, _, _ = det
        dist = (x * float(x_c) - mouse_pos.x) ** 2 + (y * float(y_c) - mouse_pos.y) ** 2
        dist_list.append(dist)

    # 找出最近的目標
    det = aims[dist_list.index(min(dist_list))]
    tag, x_center, y_center, width, height = det

    # 轉換成畫面座標
    x_center, width = x * float(x_center), x * float(width)
    y_center, height = y * float(y_center), y * float(height)

    # 計算準心應該移動的目標點位置
    target_x = x_center
    target_y = y_center if tag in [0, 2] else y_center - 1/3 * height  # 若不是頭部，就往上調整準心

    # 計算滑鼠需要移動的距離
    dx = int(target_x - mouse_pos.x)
    dy = int(target_y - mouse_pos.y)

    # 移動滑鼠，乘上靈敏度倍率
    sensitivity = 5  # 數值越小移動越平滑
    move_mouse_rel(int(dx * sensitivity), int(dy * sensitivity))
