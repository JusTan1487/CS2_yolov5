# Done by Frannecklp（原作者註記）

import cv2
import numpy as np
import win32gui, win32ui, win32con, win32api  # 使用 pywin32 操作 Windows API

def grab_screen(region=None):
    """
    擷取整個螢幕或指定區域畫面，並轉換為 OpenCV (BGR) 圖像格式。

    參數:
        region: (left, top, right, bottom)，指定擷取範圍座標。若為 None 則擷取全螢幕。

    回傳:
        numpy 陣列 (H, W, 3)，為 OpenCV 可處理的 BGR 圖像。
    """

    # 取得整個桌面視窗的 handle
    hwin = win32gui.GetDesktopWindow()

    if region:
        # 計算擷取區域的寬與高
        left, top, x2, y2 = region
        width = x2 - left + 1
        height = y2 - top + 1
    else:
        # 擷取整個螢幕的虛擬尺寸
        width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

    # 建立 DC（Device Context）用於影像擷取
    hwindc = win32gui.GetWindowDC(hwin)  # 桌面視窗的裝置上下文
    srcdc = win32ui.CreateDCFromHandle(hwindc)  # 建立來源 DC
    memdc = srcdc.CreateCompatibleDC()          # 建立記憶體相容 DC
    bmp = win32ui.CreateBitmap()                # 建立位圖用於儲存畫面

    # 配置位圖大小
    bmp.CreateCompatibleBitmap(srcdc, width, height)
    memdc.SelectObject(bmp)

    # 擷取指定區域畫面 (Bit Block Transfer)
    memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)

    # 取得圖像資料（BGRA 格式）
    signedIntsArray = bmp.GetBitmapBits(True)
    img = np.fromstring(signedIntsArray, dtype='uint8')
    img.shape = (height, width, 4)  # BGRA 格式：4 通道

    # 清除資源
    srcdc.DeleteDC()
    memdc.DeleteDC()
    win32gui.ReleaseDC(hwin, hwindc)
    win32gui.DeleteObject(bmp.GetHandle())

    # 轉換成 BGR 格式（OpenCV 預設）
    return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
