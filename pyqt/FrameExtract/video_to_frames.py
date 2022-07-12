import cv2
import os
from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication

def default_video_to_frames(video_path,result_path):
    capture = cv2.VideoCapture(video_path)
    num = 0
    while True:
        ret, img = capture.read()
        if not ret:
            break
        picname = '{:05d}.jpg'.format(num)
        cv2.imwrite(os.path.join(result_path, picname), img)
        num += 1
    capture.release()
    return num

class defaultExtract_thread(QObject):#执行交互式图像分割的ivs子线程类
    finishExtract_signal = QtCore.pyqtSignal(int)

    def __init__(self,video_path,result_path):
        super(defaultExtract_thread,self).__init__()
        self.video_path=video_path
        self.result_path=result_path

    def default_ExtractFrames_work(self):
        QApplication.processEvents()
        num=default_video_to_frames(self.video_path, self.result_path)
        self.finishExtract_signal.emit(num)

