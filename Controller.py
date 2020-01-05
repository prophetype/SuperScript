import sys
import time
import os
import cv2
import random
from Driver import UiautoDriver
from CvRecognizer import CvRecognizer

class Controller(object):

    random.seed(1234)

    def __init__(self, driver = None, reconizer = CvRecognizer()):
        if driver == None:
            raise ValueError("driver not set")
        self.driver = driver
        self.recognizer = reconizer

        #click ranges
        self.set_percent()
    
    def set_percent(self, percent = 0.7):
        self.percent = (1 - percent)/2
    
    @classmethod
    def imread(cls, filename):
        im = cv2.imread(filename)
        if im is None:
            raise RuntimeError("file: '%s' not exists" % filename)
        return im

    
    def get_screen(self):
        img = self.driver.get_screenshot()
        return img

    def extract_img(self, img = None, areas = None):
        imgs = []
        if areas:
            for area in areas:
                imgs.append(img[area[1]:area[3], area[0]:area[2]])
            return imgs
        else:
            raise ValueError

##############################################################
#########################Click method
###################################################################
    def click_area(self, area = None, time = 1):
        if area:
            w = int((area[2] - area[0])*self.percent)
            h = int((area[3] - area[1])*self.percent)
            x = random.randint(area[0] + w, area[2] -w)
            y = random.randint(area[1] + h, area[3] - h)
            self.driver.click(x, y, time)
        else:
            raise ValueError("click area = None")
    
    def click_areas(self, areas = None, times = None):
        #area: [x1, y1, x2, y2]
        for i in range(len(areas)):
            self.click_area(areas[i], times[i])


    def click_images(self, areas = None, images = None, times = None):
        if len(areas) == len(images):
            imgs = self.extract_img(self.get_screen(), areas)
            for i in range(len(images)):
                result = self.recognizer.find_template(imgs[i], images[i])
                if result:
                    top_left = result["rectangle"][0]
                    btn_right = result["rectangle"][-1]
                    area = [top_left[0] + areas[i][0],
                            top_left[1] + areas[i][1],
                            btn_right[2] + areas[i][0],
                            btn_right[3] + areas[i][1]]
                    self.driver.click(area)
                else:
                    print("Warming an image not find")
        
        else:
            raise ValueError("imgs len error")

#######################################################################
                    #Check method
#######################################################################
    def check_images(self, areas = None, images = None):

        if len(areas) == len(images):
            imgs = self.extract_img(self.get_screen(), areas)
            results = [self.recognizer.find_template(imgs[i], images[i]) for i in range(len(imgs))]
            if None in results:
                return False
            return results
        
        else:
            raise ValueError("imgs len error")

        
    def check_from_images(self, areas = None, images = None):

        results = []
        imgs = self.extract_img(self.get_screen(), areas)
        for img in imgs:
            for i in range(len(images)):
                if self.recognizer.find_template(img, images[i], rgb=True):
                    results.append(i)
                    break
                elif i == 3:
                    results.append(None)
        return results    
    
    def check_text(self, texts = "error", areas = None, config = None):

        imgs = self.extract_img(self.get_screen(), areas)

        for i, img in enumerate(imgs):
            result = self.recognizer.orc(img, config=config)
            print(result)
            if texts[i] in result:
                continue
            else:
                return False
        return True

    
    def set_driver(self, Driver = None):
        self.driver = Driver
    
    def set_recognizer(self, Recognizer = None):
        self.recognizer = Recognizer