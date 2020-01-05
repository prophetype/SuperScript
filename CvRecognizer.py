import cv2
import numpy as np
import time
import pytesseract


class CvRecognizer(object):

    def __init__(self, th = 0.85):
        self.threshold = th

    def set_threshold(self, th):
        self.threshold = th

    def show(self, img):
        ''' 显示一个图片 '''
        cv2.imshow('image', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def imread(self, filename):
        '''
        Like cv2.imread
        This function will make sure filename exists
        '''
        im = cv2.imread(filename)
        if im is None:
            raise RuntimeError("file: '%s' not exists" % filename)
        return im
    

    def find_template(self, im_source, im_search, threshold= None, rgb=False, bgremove=False):
        '''
        @return find location
        if not found; return None
        '''
        if threshold == None:
            threshold = self.threshold
        result = self.find_all_template(im_source, im_search, threshold, 1, rgb, bgremove)
        return result[0] if result else None

    def find_all_template(self, im_source, im_search, threshold= None, maxcnt=0, rgb=False,
                          bgremove=False):
        '''
        Locate image position with cv2.templateFind

        Use pixel match to find pictures.

        Args:
            im_source(string): 图像、素材
            im_search(string): 需要查找的图片
            threshold: 阈值，当相识度小于该阈值的时候，就忽略掉

        Returns:
            A tuple of found [(point, score), ...]

        Raises:
            IOError: when file read error
        '''
        if threshold == None:
            threshold = self.threshold
        # method = cv2.TM_CCORR_NORMED
        # method = cv2.TM_SQDIFF_NORMED
        method = cv2.TM_CCOEFF_NORMED

        if rgb:
            s_bgr = cv2.split(im_search)  # Blue Green Red
            i_bgr = cv2.split(im_source)
            weight = (0.3, 0.3, 0.4)
            resbgr = [0, 0, 0]
            for i in range(3):  # bgr
                resbgr[i] = cv2.matchTemplate(i_bgr[i], s_bgr[i], method)
            res = resbgr[0] * weight[0] + resbgr[1] * weight[1] + resbgr[2] * weight[2]
        else:
            s_gray = cv2.cvtColor(im_search, cv2.COLOR_BGR2GRAY)
            i_gray = cv2.cvtColor(im_source, cv2.COLOR_BGR2GRAY)
            # 边界提取(来实现背景去除的功能)
            if bgremove:
                s_gray = cv2.Canny(s_gray, 100, 200)
                i_gray = cv2.Canny(i_gray, 100, 200)

            res = cv2.matchTemplate(i_gray, s_gray, method)
        w, h = im_search.shape[1], im_search.shape[0]

        result = []
        while True:
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                top_left = min_loc
            else:
                top_left = max_loc
            if max_val < threshold:
                break
            # calculator middle point
            middle_point = (top_left[0] + w / 2, top_left[1] + h / 2)
            result.append(dict(
                result=middle_point,
                rectangle=(top_left, (top_left[0], top_left[1] + h), (top_left[0] + w, top_left[1]),
                           (top_left[0] + w, top_left[1] + h)),
                confidence=max_val
            ))
            if maxcnt and len(result) >= maxcnt:
                break
            # floodfill the already found area
            cv2.floodFill(res, None, max_loc, (-1000,), max_val - threshold + 0.1, 1, flags=cv2.FLOODFILL_FIXED_RANGE)
        return result

    def orc(self, img, config = None):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return pytesseract.image_to_string(img_rgb, config=config)