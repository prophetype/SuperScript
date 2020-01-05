import sys
import time
import os
import uiautomator2 as u2
import cv2

class Driver(object):
    def __init__(self):
        self.device = None
    
    def start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def click(self, x, y):
        raise NotImplementedError()

    def doubleclick(self, x, y):
        raise NotImplementedError()

    def swipe(self):
        raise NotImplementedError()

    def swipe_points(self):
        raise NotImplementedError()

    def get_window_size(self):
        raise NotImplementedError()

    def get_screenshot(self):
        raise NotImplementedError()


class UiautoDriver(Driver):
    def __init__(self, device=None):
        super().__init__()
        if device == None or device == "":
            self.s = "127.0.0.1:7555"

        cmd = os.popen("adb connect " + self.s)
        cmd.close()
        self.device = u2.connect(self.s)

    def start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def click(self, x = 0, y = 0, waite_time = 1):
        self.device.click(x, y)
        time.sleep(waite_time)
        

    def doubleclick(self, x, y):
        self.device.double_click(x, y)

    def swipe(self, sx, sy, ex, ey):
        self.device.swipe(sx, sy, ex, ey)
    
    def swipe_points(self, points):
        self.device.swipe_points(points)
        
    def get_window_size(self):
        return self.device.window_size()

    def get_screenshot(self):
        return self.device.screenshot(format='opencv')
    
    def show_creeenshot(self):
        img = self.get_screenshot()
        cv2.imshow("sss", img)
        cv2.waitKey(0)

"""
if  "win32" in sys.platform:
    import win32api
    import win32gui
    import win32ui
    import win32con
    from ctypes import windll
    from PIL import Image
    import cv2

    class WindowsDriver(Driver):
        def __init__(self, hwnd = None):
            super().__init__()
            self.device = hwnd

            self.hwndDC = win32gui.GetWindowDC(self.device)
            self.mfcDC  = win32ui.CreateDCFromHandle(self.hwndDC)
            self.saveDC = self.mfcDC.CreateCompatibleDC()
            self.saveBitMap = win32ui.CreateBitmap()

        
        def start(self):
            raise NotImplementedError()

        def stop(self):
            raise NotImplementedError()

        def click(self, x, y):
            win32api.SendMessage(self.device, win32con.WM_KEYDOWN, (x, y), 0)
            win32api.SendMessage(self.device, win32con.WM_KEYUP, (x, y), 0)  

        def doubleclick(self, x, y):
            self.device.double_click(x, y)

        def swipe(self, sx, sy, ex, ey):
            self.device.swipe(sx, sy, ex, ey)
    
        def swipe_points(self, points):
            self.device.swipe_points(points)
        
        def get_window_size(self):
            left, top, right, bot = win32gui.GetWindowRect(self.device)
            return (bot - top, right - left)

        def get_screenshot(self):

            w, h = self.get_window_size()
            self.saveBitMap.CreateCompatibleBitmap(self.mfcDC, w, h)
            self.saveDC.SelectObject(self.saveBitMap)
            result = windll.user32.PrintWindow(self.device, self.saveDC.GetSafeHdc(), 0)
            if result:
                bmpinfo = self.saveBitMap.GetInfo()
                bmpstr = self.saveBitMap.GetBitmapBits(True)
                im = Image.frombuffer('RGB',(bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                           bmpstr, 'raw', 'BGRX', 0, 1)
                return im
            else:
                return None

        def __del__(self):

            win32gui.DeleteObject(self.saveBitMap.GetHandle())
            self.saveDC.DeleteDC()
            self.mfcDC.DeleteDC()
            win32gui.ReleaseDC(self.device, self.hwndDC)

        @classmethod
        def find_window(cls, class_name, title_name):
            wnd = win32gui.FindWindow(class_name, title_name)
            if wnd:
                return WindowsDriver(wnd)
            else:
                return None
"""


if __name__ == "__main__":
    d = UiautoDriver()
    d.show_creeenshot()
