import sys
import time
import os
import random
from CvRecognizer import CvRecognizer
from Controller import Controller


class State(object):

    random.seed()
    scanning = True

    frequence = 0.5
    conver2scanning_time = 60
    max_times = int(conver2scanning_time/frequence)

    max_scan_times = 1000
    controller = None

    def __init__(self, parent = None):
        self.next= []

        self.run_times = 0
        self.scanning_times = 0

        if parent and isinstance(parent, State):
            parent.next.append(self)


    def add_state(self, state):
        if isinstance(state, State):
            self.next.append(state)
        else:
            raise TypeError()

    def check_state(self):
        return True
    
    def reset(self):
        for i in self.next:
            i.reset()
        return True
    
    def work(self):
        raise NotImplementedError()
    
    def run(self):

        if not State.scanning:
            self.work()
            self.run_times += 1
        
        if  not self.next:
            return None

        if not State.scanning:
            
            for _ in range(State.max_times):
                for s in self.next:
                    if s.check_state():
                        return s
                time.sleep(State.frequence)
            State.scanning = True

        if State.scanning:
            for s in self.next:
                if s.check_state():
                    State.scanning = False
                    self.scanning_times = 0
                    return s
            idx = random.randint(0, len(self.next) - 1)
            self.scanning_times += 1
            if self.scanning_times > State.max_scan_times:
                raise RuntimeError()
            return self.next[idx]
    

    @classmethod
    def set_frequence(cls, times):
        cls.frequence = times
        cls.max_times = int(cls.conver2scanning_time/cls.frequence)
    
    @classmethod
    def set_conver2scanning_time(cls, times):
        cls.conver2scanning_time = times
        cls.max_times = int(cls.conver2scanning_time/cls.frequence)
    
    @classmethod
    def set_max_scan_times(cls, times):
        cls.max_scan_times = times
    
    @classmethod
    def set_controller(cls, controller):
        cls.controller = controller


class TopState(State):

    def __init__(self, epoch = 10, controller = None):
        super().__init__(parent=None)
        self.epoch = epoch
        State.set_controller(controller)
    
    def loop(self):
        while self.next[0].run_times < self.epoch:
            state = self
            if state.scanning:
                self.work()
            while state:
                state = state.run()
            self.reset()
    
    def work(self):
        print("start:", self.next[0].run_times + 1, "epoch")

###################################################################################################
#############                   Work State
###############################################################################################
class WorkState(State):

    def __init__(self, parent = None, work_areas = None, times = 1):
        State.__init__(self, parent = parent)
        self.work_areas = work_areas
        self.set_times(times)

    def work(self):

        State.controller.click_areas(self.work_areas, self.times)
    
    def set_times(self, times):

        if isinstance(times, int):
            self.times = [times] * len(self.work_areas)
        elif isinstance(times, list):
            if len(times) != len(self.work_areas):
                print("Warming len of time error, set by 1")
                self.times = [1] * len(self.work_areas)
            else:
                self.times = times

class ImageWorkState(WorkState):

    def __init__(self, parent = None, work_areas = None, times = 1, work_imgs = None):
        WorkState.__init__(self, parent=parent, work_areas=work_areas, times=times)
        self.set_work_images(work_imgs)
    
    def work(self):
        return State.controller.click_images(self.work_areas, self.work_imgs, self.times)
    
    def set_work_images(self, imgs):
        if isinstance(imgs, list):
            self.work_imgs = [State.controller.imread(img) for img in imgs]
        else:
            raise ValueError("img path error")
###########################################################################################
#                                  Check State
#######################################################################################

class CheckState(State):

    def __init__(self, parent = None, check_areas = None):
        State.__init__(self, parent=parent)
        self.check_areas = check_areas


class ImageCheckState(CheckState):
    #check_imgs: [img....]
    #check_areas[[point, point]....]
    #check all imgs if exist return true
    def __init__(self, parent = None, check_areas = None, check_imgs = None):
        CheckState.__init__(self, parent=parent, check_areas=check_areas)
        self.set_check_images(check_imgs)
    
    
    def check_state(self, img = None):
        return State.controller.check_images(self.check_areas, self.check_imgs, img)
    
    def set_check_images(self, imgs):

        if isinstance(imgs, list):
            self.check_imgs = [State.controller.imread(img) for img in imgs]
        else:
            raise ValueError("img path error")


class TextCheckState(CheckState):
    #check_texts = [str.....]
    #
    def __init__(self, parent, check_areas = None, check_texts = None):
        CheckState.__init__(self, parent=parent, check_areas=check_areas)
        self.check_texts = check_texts
        self.config = None
    
    def check_state(self):
        print("recognizer string:", self.check_texts, self.check_areas)
        return State.controller.check_text(self.check_texts, self.check_areas, self.config)




############################################################################################

class ImageCheckClick(ImageCheckState, WorkState):
    #check img and click range
    def __init__(self, parent = None, 
                       check_imgs = None, 
                       check_areas = None, 
                       work_areas = None, 
                       times = None):
        ImageCheckState.__init__(self, parent = parent, check_imgs = check_imgs, check_areas = check_areas)
        WorkState.__init__(self, parent = parent, work_areas = work_areas, times = times)
    
    def check_state(self):
        return ImageCheckState.check_state(self)
    
    def work(self):
        WorkState.work(self)




    

'''
class ImageState(ImageCheckState, ImageWorkState):
    def __init__(self, parent = None, check_img = None, check_area = None, work_img = None, work_area = None):
        ImageCheckState.__init__(self, parent=parent, check_imgS = None, check_areaS = None)
        ImageWorkState.__init__(self, parent=parent, work_img = None, work_area = None)
    
    def check_state(self):
        return ImageCheckState.check_state(self)
    
    def work(self):
        return ImageWorkState.work(self)

class SingleImageState(ImageCheckState):
    def __init__(self, parent = None, check_img = None, check_area = None):
        super().__init__(self, parent=parent)
    
    def work(self):
        return State.controller.click_image(self.check_img, self.check_area)

    def check_state(self):
        return State.controller.check_text(self.check_img, self.check_area)
'''



if __name__ == "__main__":

    s = TopState()
    s.loop()

