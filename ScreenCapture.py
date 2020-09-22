import numpy as np
import win32con
import win32gui
import win32ui

from utils import windowEnumerationHandler


class WindowCapture:

    def __init__(self, window_name, manual_offset=False, offset=(0, 0)):
        self.window_name = window_name
        self.manual_offset = manual_offset
        self.w = 1920
        self.h = 1080
        if self.manual_offset:
            self.hwnd = win32gui.GetDesktopWindow()
            self.offset_x = offset[0]
            self.offset_y = offset[1]
        else:
            du_window = self._get_du_windows()
            self.hwnd = du_window
            x_1, y_1, x_2, y_2 = win32gui.GetWindowRect(du_window)
            self.offset_x = x_1 + 13
            self.offset_y = y_1 + 58

    def _get_du_windows(self):
        top_windows = []
        win32gui.EnumWindows(windowEnumerationHandler, top_windows)
        for hwd, title in top_windows:
            if self.window_name.lower() in title.lower():
                return hwd

    def window_to_foreground(self):
        if self.manual_offset:
            raise Exception("No Window available in manuel_offset mode")
        win32gui.ShowWindow(self.hwnd, 5)
        win32gui.SetForegroundWindow(self.hwnd)

    def get_screenshot(self):

        # get the window image data
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        if self.manual_offset:
            cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (self.offset_x, self.offset_y), win32con.SRCCOPY)
        else:
            cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (13, 58), win32con.SRCCOPY)

        # convert the raw data into a format opencv can read
        # dataBitMap.SaveBitmapFile(cDC, 'debug.bmp')
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.frombuffer(signedIntsArray, dtype='uint8')
        img.shape = (self.h, self.w, 4)

        # free resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        # drop the alpha channel
        img = img[..., :3]
        img = np.ascontiguousarray(img)

        return img

    # translate a pixel position on a screenshot image to a pixel position on the screen.
    # pos = (x, y)
    # WARNING: if you move the window being captured after execution is started, this will
    # return incorrect coordinates, because the window position is only calculated in
    # the __init__ constructor.
    def get_screen_position(self, pos):
        return pos[0] + self.offset_x, pos[1] + self.offset_y
