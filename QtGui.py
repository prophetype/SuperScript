import sys
import time
import copy
import cv2
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Driver import *

class ImageDialog(QDialog):

    pointSignal = pyqtSignal(object)

    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self.orange_pix = QPixmap()
        self.parent = parent
        self.firstP = QPoint()
        self.scondP = QPoint()

        self.UIinit()
    
    def UIinit(self):

        vbox = QVBoxLayout()

        #add top layout
        #
        top_hbox = QHBoxLayout()

        self.cb = QComboBox()
        self.cb.addItem("rect")
        self.cb.addItem("image")
        top_hbox.addWidget(self.cb)

        fbox = QFormLayout()
        self.path_edit = QLineEdit()
        fbox.addRow("Path", self.path_edit)

        self.file_name =QLineEdit()
        fbox.addRow("name", self.file_name)
        
        self.btn_path = QPushButton("file")
        top_hbox.addLayout(fbox)
        top_hbox.addWidget(self.btn_path)
        vbox.addLayout(top_hbox)

        # add mid layout
        self.img = QLabel()
        self.img.resize(self.orange_pix.size())
        self.img.setPixmap(self.orange_pix)
        self.img.setScaledContents(True)
        vbox.addWidget(self.img, Qt.AlignCenter)

        #add bott layout
        #
        hbox = QHBoxLayout()
        self.btn_ok = QPushButton("Ok", self)
        self.btn_cancel = QPushButton("Cancel", self)
        self.btn_save = QPushButton("Save", self)

        hbox.addWidget(self.btn_ok, Qt.AlignCenter)
        hbox.addWidget(self.btn_save, Qt.AlignCenter)
        hbox.addWidget(self.btn_cancel, Qt.AlignCenter)
        vbox.addLayout(hbox, Qt.AlignBottom)
        self.setLayout(vbox)

        self.btn_path.clicked.connect(self.open_file)
        self.btn_ok.clicked.connect(self.pushPoints)
        self.btn_cancel.clicked.connect(self.close)
        self.btn_save.clicked.connect(self.save_img)

    def open_file(self):
        #保存文件或者points
        #当文件夹不存在是，需要创建文件夹
        fdlg =  QFileDialog(self)
        fdlg.setFileMode(QFileDialog.Directory)
        if fdlg.exec():
            path = fdlg.selectedFiles()
            self.path_edit.setText(str(path[0]))

    def pushPoints(self):

        print(self.conver_abs_points())
        self.pointSignal.emit(self.conver_abs_points())
    
    def save_img(self):
        if self.firstP and self.scondP and self.path_edit.text():
            
            rect = self.conver_abs_points()
            img = self.pix.copy(rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1])
            print(img.rect())
            img = img.toImage()

            file_name = self.path_edit.text()+ "/" + self.file_name.text()

            img.save(file_name + ".jpg", "JPG")
            self.parent.info.append("save image in:" + file_name)

            with open(file_name + ".conf","w") as f:
                f.write(str(rect))
            self.parent.info.append("save text in:" + file_name + " with " + str(rect))
            return True
        return False

    def setImage(self, pix):
        self.orange_pix = pix
        self.update()
    
    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            self.firstP = QMouseEvent.pos()
            self.scondP = self.firstP
    
    def mouseMoveEvent(self, QMouseEvent):
        if QMouseEvent.buttons() == Qt.LeftButton:
            self.scondP = QMouseEvent.pos()
            self.update()
    
    def mouseReleaseEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            self.scondP = QMouseEvent.pos()
            self.update()

    def paintEvent(self, QPaintEvent):

        self.pix = self.orange_pix.copy()
        paint = QPainter(self.pix)
        points = self.conver_abs_points()

        paint.drawRect(points[0], points[1], points[2] - points[0], points[3] - points[1])
        self.img.setPixmap(self.pix)
    

    def conver_abs_points(self):

        rect = self.img.geometry()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

        x1, x2 = [self.firstP.x() - x, self.scondP.x() - x]
        y1, y2 = [self.firstP.y() - y, self.scondP.y() - y]

        x1 = max(min(x1, x2), 0)
        x2 = min(max(x1, x2), w)
        y1 = max(min(y1, y2), 0)
        y2 = min(max(y1, y2), h)

        orange_size = self.orange_pix.size()
        pix_w = orange_size.width()
        pix_h = orange_size.height()

        x1, x2 = x1*pix_w/w, x2*pix_w/w
        y1, y2 = y1*pix_h/h, y2*pix_h/h

        return int(x1), int(y1), int(x2), int(y2)

class MyWidget(QWidget):

    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        
        self.resize(800, 700)
        self.driver = None

        self.imgDia = ImageDialog(self)
        self.UIinit()
    
    def UIinit(self):
        hhbox = QHBoxLayout()

        self.device_choice_box = QComboBox()
        self.device_choice_box.addItem("uiautomate")
        self.device_choice_box.addItem("hwnd")
        hhbox.addWidget(self.device_choice_box)

        self.search_seri = QLineEdit()
        hhbox.addWidget(self.search_seri)

        self.search_btn = QPushButton("Search")
        hhbox.addWidget(self.search_btn)

        vbox = QVBoxLayout()
        vbox.addLayout(hhbox, Qt.AlignTop)
        
        self.info = QTextEdit()
        self.info.setReadOnly(True)
        self.info.setFontPointSize(16)
        
        vbox.addWidget(self.info)
        
        self.show_img_btn = QPushButton("Show Image")

        vbox.addWidget(self.show_img_btn)
        self.setLayout(vbox)

        self.search_btn.clicked.connect(self.slot_search)
        self.show_img_btn.clicked.connect(self.slot_show_dialog)
        self.imgDia.pointSignal.connect(self.slot_get_points)
        
    
    def slot_search(self):
        if self.device_choice_box.currentText() == "uiautomate":
            
            self.driver = UiautoDriver(self.search_seri.text())
            self.info.append("searching device:" + self.driver.s)

    def slot_get_points(self, points):
        self.info.append("poinsts :" + str(points))

    def slot_show_dialog(self):
        img = self.driver.get_screenshot()
        #conver to pixmap
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        qimg = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg)
        self.imgDia.setImage(pix)
        self.imgDia.exec()

if __name__ == "__main__":

    app = QApplication(sys.argv)
    w = MyWidget()
    w.show()
    sys.exit(app.exec())
