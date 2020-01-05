import sys
import time
import uiautomator2 as u2

device = u2.connect("127.0.0.1:7555")

while True:
    device.click(500, 500)
    time.sleep(1)